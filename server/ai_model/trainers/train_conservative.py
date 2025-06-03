import os
import argparse
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
import pickle
# from imblearn.over_sampling import RandomOverSampler

from ai_model.preprocessing.data_fetcher import fetch_ohlcv_range_quarterly
from ai_model.preprocessing.indicator_engine import enrich_with_indicators

load_dotenv()

FEATURE_COLUMNS = [
    'Open', 'High', 'Low', 'Close', 'Volume',
    'EMA_10', 'EMA_50', 'RSI_14', 'Daily_Return', 'Volatility',
    'HL_Range', 'Candle_Body', 'Volume_Rolling_5', 'Volume_Rolling_20',
    'MACD', 'MACD_Signal', 'BB_Band_Pct', 'ATR'
]
SEQUENCE_LENGTH = 30
TARGET_COLUMN = "Close"
HORIZON = 6


def generate_labels(df: pd.DataFrame, horizon=HORIZON) -> pd.DataFrame:
    df = df.copy()
    future_return = (df[TARGET_COLUMN].shift(-horizon) - df[TARGET_COLUMN]) / df[TARGET_COLUMN]
    df["Label"] = pd.cut(
        future_return,
        bins=[-np.inf, -0.01, 0.01, np.inf],
        labels=["sell", "hold", "buy"]
    )
    return df.dropna()


def prepare_sequences(df: pd.DataFrame, sequence_length: int):
    X, y = [], []
    for i in range(len(df) - sequence_length):
        seq_x = df.iloc[i:i + sequence_length][FEATURE_COLUMNS].values
        label = df.iloc[i + sequence_length]["Label"]
        X.append(seq_x)
        y.append(label)
    return np.array(X), np.array(y)


def build_classifier_model(input_shape, num_classes):
    model = models.Sequential([
        layers.Input(shape=input_shape),
        layers.Conv1D(64, kernel_size=3, activation='relu'),
        layers.MaxPooling1D(pool_size=2),
        layers.LSTM(64),
        layers.Dropout(0.3),
        layers.Dense(32, activation='relu'),
        layers.Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model


def train_classifier(ticker: str, user_id: int, from_date: str, to_date: str):
    print(f"Loading data for {ticker}...")
    df = fetch_ohlcv_range_quarterly(ticker, from_date, to_date)
    df = enrich_with_indicators(df)
    df = generate_labels(df)
    df = df[df["Label"].isin(["buy", "hold", "sell"])]

    scaler = MinMaxScaler()
    df[FEATURE_COLUMNS] = scaler.fit_transform(df[FEATURE_COLUMNS])

    encoder = LabelEncoder()
    df["Label"] = encoder.fit_transform(df["Label"])

    X, y = prepare_sequences(df, SEQUENCE_LENGTH)
    print(f"Shape after preprocessing: {X.shape}")

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = build_classifier_model((SEQUENCE_LENGTH, len(FEATURE_COLUMNS)), num_classes=3)
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    from sklearn.utils.class_weight import compute_class_weight
    class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(y_train), y=y_train)
    class_weight_dict = dict(zip(np.unique(y_train), class_weights))

    model.fit(X_train, y_train,
              epochs=30,
              batch_size=32,
              validation_data=(X_val, y_val),
              callbacks=[early_stop],
              class_weight=class_weight_dict)

    model_dir = f"ai_model/models/tf_models"
    model_path = os.path.join(model_dir, f"{user_id}_{ticker}.keras")
    scaler_path = os.path.join(model_dir, f"{user_id}_{ticker}_scaler.pkl")
    encoder_path = os.path.join(model_dir, f"{user_id}_{ticker}_encoder.pkl")

    os.makedirs(model_dir, exist_ok=True)
    model.save(model_path)
    print(f"Model saved to {model_path}")

    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    with open(encoder_path, "wb") as f:
        pickle.dump(encoder, f)
    print("Scaler and encoder saved")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", required=True, help="Ticker symbol")
    parser.add_argument("--user_id", required=True, help="User ID")
    parser.add_argument("--from_date", default="2024-01-01", help="Start date for data")
    parser.add_argument("--to_date", default="2025-03-01", help="End date for data")
    args = parser.parse_args()

    train_classifier(args.ticker, args.user_id, args.from_date, args.to_date)