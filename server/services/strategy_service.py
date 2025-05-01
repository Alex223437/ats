import pandas as pd
from sqlalchemy.orm import Session
from server.database import get_db
from server.models.strategy import Strategy
from server.services.ai_service import predict_signals  

class StrategyService:
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
        """ Применяет сохраненную стратегию к данным """
        if data is None or data.empty:
            return pd.DataFrame()

        if db is None:
            from server.database import get_db  # Импорт только если db не передан
            db = next(get_db())  

        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            return data  # Если стратегии нет, просто возвращаем данные

        # Проверяем, какие индикаторы используются в стратегии
        needs_sma = any(sig['indicator'] == "SMA" for sig in strategy.buy_signals + strategy.sell_signals)
        needs_rsi = any(sig['indicator'] == "RSI" for sig in strategy.buy_signals + strategy.sell_signals)

        # Рассчитываем SMA, если он нужен
        if needs_sma:
            data['SMA_Short'] = data['Close'].rolling(window=10, min_periods=1).mean()
            data['SMA_Long'] = data['Close'].rolling(window=50, min_periods=1).mean()

        # Рассчитываем RSI, если он нужен
        if needs_rsi:
            data['RSI'] = StrategyService.calculate_rsi(data)

        # Применяем buy_signals
        data['Buy_Signal'] = False
        for signal in strategy.buy_signals:
            indicator = signal['indicator']
            value = float(signal['value'])
            
            if indicator == "RSI" and needs_rsi:
                data.loc[data['RSI'] < value, 'Buy_Signal'] = True
            
            elif indicator == "SMA" and needs_sma:
                data.loc[data['SMA_Short'] > data['SMA_Long'], 'Buy_Signal'] = True

        # Применяем sell_signals
        data['Sell_Signal'] = False
        for signal in strategy.sell_signals:
            indicator = signal['indicator']
            value = float(signal['value'])

            if indicator == "RSI" and needs_rsi:
                data.loc[data['RSI'] > value, 'Sell_Signal'] = True

            elif indicator == "SMA" and needs_sma:
                data.loc[data['SMA_Short'] < data['SMA_Long'], 'Sell_Signal'] = True

        return data
    @staticmethod
    def apply_ai_prediction(data: pd.DataFrame):
        """
        Применяет AI модель для генерации сигналов покупок и продаж.
        AI предсказывает точки входа и выхода на основе исторических данных.
        """
        if data is None or data.empty:
            return pd.DataFrame()

        if 'Date' not in data.columns:
            if 'date' in data.columns:
                data = data.rename(columns={'date': 'Date'})

        if not isinstance(data.index, pd.DatetimeIndex):
            data['Date'] = pd.to_datetime(data['Date'])
            data = data.set_index('Date')

        # Запускаем AI-предсказания
        ai_predictions = predict_signals(data)

        # Добавляем AI-сигналы в общий датасет
        data['Buy_Signal'] = ai_predictions['Buy_Prediction'].astype(bool)
        data['Sell_Signal'] = ai_predictions['Sell_Prediction'].astype(bool)

        return data

    @staticmethod
    def calculate_rsi(data, period=14):
        """ Рассчитывает RSI на основе цен закрытия """
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()

        rs = gain / (loss + 1e-10)  # Чтобы избежать деления на 0
        rsi = 100 - (100 / (1 + rs))

        return rsi