import pandas as pd
from sqlalchemy.orm import Session
from database import get_db
from models.strategy import Strategy

class StrategyService:
    @staticmethod
    def compare(series, operator: str, value: float):
        if operator == "<":
            return series < value
        elif operator == "<=":
            return series <= value
        elif operator == "==":
            return series == value
        elif operator == ">=":
            return series >= value
        elif operator == ">":
            return series > value
        else:
            raise ValueError(f"Unsupported operator: {operator}")
    @staticmethod
    def apply_moving_average_strategy(data: pd.DataFrame, short_window=10, long_window=50):
        if data is None or data.empty:
            return pd.DataFrame()

        if 'Date' not in data.columns:
            if 'date' in data.columns:
                data = data.rename(columns={'date': 'Date'})

        if not isinstance(data.index, pd.DatetimeIndex):
            data['Date'] = pd.to_datetime(data['Date'])
            data = data.set_index('Date')

        if len(data) < long_window:
            long_window = max(len(data) // 2, short_window + 1)

        data['SMA_Short'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
        data['SMA_Long'] = data['Close'].rolling(window=long_window, min_periods=1).mean()

        data['Signal'] = 0
        data.loc[data['SMA_Short'] > data['SMA_Long'], 'Signal'] = 1
        data.loc[data['SMA_Short'] < data['SMA_Long'], 'Signal'] = -1

        data['Buy_Signal'] = (data['Signal'] == 1) & (data['Signal'].shift(1) == -1)
        data['Sell_Signal'] = (data['Signal'] == -1) & (data['Signal'].shift(1) == 1)

        data.dropna(subset=['SMA_Short', 'SMA_Long'], inplace=True)

        return data

    @staticmethod
    def apply_saved_strategy(data: pd.DataFrame, strategy_id: int, db: Session = None):
        if data is None or data.empty:
            return pd.DataFrame()

        if db is None:
            from database import get_db
            db = next(get_db())

        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            return data

        all_signals = strategy.buy_signals + strategy.sell_signals

        indicators = {s["indicator"] for s in all_signals}

        if "SMA" in indicators:
            data["SMA_Short"] = data["Close"].rolling(window=10, min_periods=1).mean()
            data["SMA_Long"] = data["Close"].rolling(window=50, min_periods=1).mean()

        if "RSI" in indicators:
            data["RSI"] = StrategyService.calculate_rsi(data)

        if "MACD" in indicators:
            macd, macd_signal = StrategyService.calculate_macd(data)
            data["MACD"] = macd
            data["MACD_SIGNAL"] = macd_signal

        if "Bollinger Bands" in indicators:
            upper, lower = StrategyService.calculate_bollinger_bands(data)
            data["BB_UPPER"] = upper
            data["BB_LOWER"] = lower

        def process_signals(signal_list, column_name):
            data[column_name] = False
            for signal in signal_list:
                ind = signal["indicator"]
                val = float(signal["value"])
                op = signal.get("operator", ">")

                if ind == "RSI" and "RSI" in data:
                    data[column_name] |= StrategyService.compare(data["RSI"], op, val)

                elif ind == "SMA" and "SMA_Short" in data and "SMA_Long" in data:
                    data[column_name] |= StrategyService.compare(data["SMA_Short"] - data["SMA_Long"], op, 0)

                elif ind == "MACD" and "MACD" in data and "MACD_SIGNAL" in data:
                    data[column_name] |= StrategyService.compare(data["MACD"] - data["MACD_SIGNAL"], op, val)

                elif ind == "Bollinger Bands" and "BB_UPPER" in data and "BB_LOWER" in data:
                    data[column_name] |= StrategyService.compare(data["Close"], op, val)

        process_signals(strategy.buy_signals, "Buy_Signal")
        process_signals(strategy.sell_signals, "Sell_Signal")

        return data
    
    @staticmethod
    def calculate_rsi(data, period=14):
        """ Рассчитывает RSI на основе цен закрытия """
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()

        rs = gain / (loss + 1e-10) 
        rsi = 100 - (100 / (1 + rs))

        return rsi
    
    @staticmethod
    def calculate_macd(data, fast=12, slow=26, signal=9):
        """Calculate MACD and MACD Signal Line"""
        ema_fast = data['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = data['Close'].ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        return macd, macd_signal

    @staticmethod
    def calculate_bollinger_bands(data, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        rolling_mean = data['Close'].rolling(window=window).mean()
        rolling_std = data['Close'].rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, lower_band