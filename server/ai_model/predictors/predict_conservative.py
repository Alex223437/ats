import os
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from ai_model.preprocessing.indicator_engine import enrich_with_indicators

def predict_signals(ticker: str, user_id: int, df: pd.DataFrame):
    sequence_length = 30
    feature_columns = [
        'Open', 'High', 'Low', 'Close', 'Volume',
        'EMA_10', 'EMA_50', 'RSI_14', 'Daily_Return', 'Volatility',
        'HL_Range', 'Candle_Body', 'Volume_Rolling_5', 'Volume_Rolling_20',
        'MACD', 'MACD_Signal', 'BB_Band_Pct', 'ATR'
    ]

    base_path = f"ai_model/models/tf_models/{user_id}_{ticker}"
    model_path = base_path + ".keras"
    scaler_path = base_path + "_scaler.pkl"
    encoder_path = base_path + "_encoder.pkl"

    print("Loading model and scalers...")
    model = load_model(model_path)
    with open(scaler_path, "rb") as f:
        scaler: MinMaxScaler = pickle.load(f)
    with open(encoder_path, "rb") as f:
        encoder: LabelEncoder = pickle.load(f)

    if df is None or df.empty:
        return None
    df = df.copy()
    df = enrich_with_indicators(df)
    df.dropna(inplace=True)
    original_closes = df["Close"].copy()
    timestamps = df.index.copy()

    df[feature_columns] = scaler.transform(df[feature_columns])

    X, clean_timestamps, closes = [], [], []
    for i in range(sequence_length, len(df)):
        seq = df.iloc[i - sequence_length:i][feature_columns].values
        X.append(seq)
        clean_timestamps.append(timestamps[i])
        closes.append(original_closes.iloc[i])
    X = np.array(X)

    if len(X) == 0:
        print("Not enough data to make prediction.")
        return None

    print("Generating predictions...")
    preds = model.predict(X)
    predicted_classes_idx = np.argmax(preds, axis=1)
    predicted_confidences = np.max(preds, axis=1)
    predicted_classes = encoder.inverse_transform(predicted_classes_idx)

    results = pd.DataFrame({
        "timestamp": clean_timestamps,
        "real_close": closes,
        "signal": predicted_classes,
        "confidence": predicted_confidences
    })

    if len(results) == 0:
        return None

    return {
        "timestamp": results.iloc[-1]["timestamp"],
        "real_close": results.iloc[-1]["real_close"],
        "signal": results.iloc[-1]["signal"],
        "confidence": results.iloc[-1]["confidence"]
    }

if __name__ == "__main__":
    print(predict_signals("AAPL", 1, None))