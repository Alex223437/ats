import pandas as pd
import ta



def enrich_with_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df["EMA_10"] = df["Close"].ewm(span=10, adjust=False).mean()
    df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI_14"] = 100 - (100 / (1 + rs))

    df["Daily_Return"] = df["Close"].pct_change()
    df["Volatility"] = df["Daily_Return"].rolling(window=14).std()
    df["HL_Range"] = df["High"] - df["Low"]
    df["Candle_Body"] = df["Close"] - df["Open"]
    df["Volume_Rolling_5"] = df["Volume"].rolling(window=5).mean()
    df["Volume_Rolling_20"] = df["Volume"].rolling(window=20).mean()

    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    bb = ta.volatility.BollingerBands(close=df["Close"], window=20, window_dev=2)
    df["BB_Band_Pct"] = (df["Close"] - bb.bollinger_lband()) / (bb.bollinger_hband() - bb.bollinger_lband())

    atr = ta.volatility.AverageTrueRange(high=df["High"], low=df["Low"], close=df["Close"], window=14)
    df["ATR"] = atr.average_true_range()

    df = df.dropna()
    return df