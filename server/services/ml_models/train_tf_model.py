import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle

from data.market_data import MarketData
from data.data_preprocessing import create_labels, prepare_features_for_ml

MODEL_PATH = "services/ml_models/models/tf_model.keras"
SCALER_PATH = "services/ml_models/models/tf_scaler.pkl"

FEATURE_COLUMNS = [
    'Close', 'Volume', 'Volatility', 'Daily_Return',
    'SMA_5', 'SMA_20', 'SMA_10', 'SMA_50',
    'EMA_10', 'EMA_50', 'RSI_14', 'MACD', 'MACD_Signal'
]

def build_mlp_model(input_dim):
    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(3, activation='softmax')
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    return model

def preprocess_data_for_tf(df: pd.DataFrame):
    df = df.copy()
    df = df.dropna()

    def label(row):
        if row["Buy_Signal"] == 1:
            return 1
        elif row["Sell_Signal"] == 1:
            return 2
        else:
            return 0

    df["Target"] = df.apply(label, axis=1)
    df = df.drop(columns=["Buy_Signal", "Sell_Signal"])
    X = df[FEATURE_COLUMNS].copy()
    y = df["Target"].astype(int)

    return X, y

def train_tf_model():
    tickers = ["AAPL", "TSLA", "NVDA", "GOOGL", "AMZN"]
    all_data = []

    for ticker in tickers:
        data = MarketData.download_data(ticker, multiplier=1, timespan='hour', from_date="2024-01-01")
        if data is None or data.empty:
            print(f"⚠️ Пропущено: {ticker}, нет данных")
            continue
        data = MarketData.calculate_indicators(data)
        data["SMA_5"] = data["Close"].rolling(window=5).mean()
        data["SMA_20"] = data["Close"].rolling(window=20).mean()
        data = create_labels(data)
        data["Ticker"] = ticker
        all_data.append(data)

    if not all_data:
        raise RuntimeError("❌ Не удалось получить данные для обучения")

    df = pd.concat(all_data).reset_index()
    X, y = preprocess_data_for_tf(df)
    print(f"📦 Training X cols: {X.columns.tolist()}")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    model = build_mlp_model(X_train.shape[1])

    early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

    model.fit(X_train, y_train,
              epochs=30,
              batch_size=32,
              validation_data=(X_test, y_test),
              callbacks=[early_stop])

    model.save(MODEL_PATH)
    print(f"✅ TensorFlow модель обучена и сохранена в {MODEL_PATH}")

if __name__ == "__main__":
    train_tf_model()