import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def create_labels(data: pd.DataFrame, future_days=3, threshold=0.02):
    """
    Разметка данных: целевая переменная для AI
    future_days - на сколько дней вперед смотреть
    threshold - % роста/падения для сигнала
    """
    data['Future_Close'] = data['Close'].shift(-future_days)
    data['Price_Change'] = (data['Future_Close'] - data['Close']) / data['Close']

    data['Buy_Signal'] = (data['Price_Change'] > threshold).astype(int)
    data['Sell_Signal'] = (data['Price_Change'] < -threshold).astype(int)

    # Убираем строки, где нет будущих данных
    data = data.dropna()

    return data

def preprocess_data(data):
    """Нормализация данных перед обучением"""
    data["Volatility"] = data["High"] - data["Low"]
    data["Daily_Return"] = (data["Close"] - data["Open"]) / data["Open"]
    data["SMA_5"] = data["Close"].rolling(window=5).mean()
    data["SMA_20"] = data["Close"].rolling(window=20).mean()
    
    feature_columns = ['Close', 'Volume', 'Volatility', 'Daily_Return', 
                       'SMA_5', 'SMA_20', 'SMA_10', 'SMA_50', 'EMA_10', 'EMA_50', 'RSI_14', 'MACD', 'MACD_Signal']
    
    target_columns = ['Buy_Signal', 'Sell_Signal']

    X = data[feature_columns].fillna(0)
    # Проверяем, есть ли целевые колонки в данных (если инференс - их не будет)
    if set(target_columns).issubset(data.columns):
        y = data[target_columns]
    else:
        y = None  # При инференсе таргетов нет

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y
