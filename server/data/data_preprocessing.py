import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    'Close', 'Volume', 'Volatility', 'Daily_Return',
    'SMA_5', 'SMA_20', 'SMA_10', 'SMA_50',
    'EMA_10', 'EMA_50', 'RSI_14', 'MACD', 'MACD_Signal'
]


def create_labels(data: pd.DataFrame, future_days=3, threshold=0.02):
    """
    Добавляет колонку Target: 
    1 — покупка, -1 — продажа, 0 — удержание
    """
    data = data.copy()
    data['Future_Close'] = data['Close'].shift(-future_days)
    data['Price_Change'] = (data['Future_Close'] - data['Close']) / data['Close']

    data['Buy_Signal'] = (data['Price_Change'] > threshold).astype(int)
    data['Sell_Signal'] = (data['Price_Change'] < -threshold).astype(int)

    def assign_target(row):
        if row['Buy_Signal'] == 1:
            return 1
        elif row['Sell_Signal'] == 1:
            return -1
        return 0

    data['Target'] = data.apply(assign_target, axis=1)
    return data.dropna()


def preprocess_data(data: pd.DataFrame):
    """
    Генерация признаков для обучения, без масштабирования.
    Возвращает X (features), без нормализации.
    """
    data = data.copy()
    data["Volatility"] = data["High"] - data["Low"]
    data["Daily_Return"] = (data["Close"] - data["Open"]) / data["Open"]
    data["SMA_5"] = data["Close"].rolling(window=5).mean()
    data["SMA_20"] = data["Close"].rolling(window=20).mean()

    data = data.fillna(0)

    X = data[FEATURE_COLUMNS]
    return X, data.get("Target")


def prepare_features_for_ml(df: pd.DataFrame, scaler: StandardScaler = None):
    """
    Подготовка признаков для предсказаний, включая масштабирование.
    """
    df = df.copy()
    df["Volatility"] = df["High"] - df["Low"]
    df["Daily_Return"] = (df["Close"] - df["Open"]) / df["Open"]
    df["SMA_5"] = df["Close"].rolling(window=5).mean()
    df["SMA_20"] = df["Close"].rolling(window=20).mean()

    df = df.fillna(0)

    X = df[FEATURE_COLUMNS]

    if scaler is None:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
    else:
        X_scaled = scaler.transform(X)

    return X_scaled, scaler