import os
import numpy as np
import pandas as pd
import pickle
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from ai_model.preprocessing.indicator_engine import enrich_with_indicators


def predict_signals_batch(ticker: str, user_id: int, df: pd.DataFrame) -> pd.DataFrame:
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

    if not (os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(encoder_path)):
        raise FileNotFoundError("Required model/scaler/encoder files are missing.")

    model = load_model(model_path)
    with open(scaler_path, "rb") as f:
        scaler: MinMaxScaler = pickle.load(f)
    with open(encoder_path, "rb") as f:
        encoder: LabelEncoder = pickle.load(f)

    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty or None.")

    df = df.copy()
    df = enrich_with_indicators(df)
    df.dropna(inplace=True)
    df = df.sort_index()
    original_closes = df["Close"].copy()
    timestamps = df.index.copy()

    # Scale features
    df[feature_columns] = scaler.transform(df[feature_columns])

    # Prepare sequences
    sequences = []
    meta = []
    for i in range(sequence_length, len(df)):
        seq = df.iloc[i - sequence_length:i][feature_columns].values
        sequences.append(seq)
        meta.append({
            "timestamp": timestamps[i],
            "real_close": original_closes.iloc[i]
        })

    if not sequences:
        return pd.DataFrame(columns=["timestamp", "real_close", "signal", "confidence"])

    X = np.array(sequences)
    predictions = model.predict(X, verbose=0)
    predicted_labels = np.argmax(predictions, axis=1)
    confidences = np.max(predictions, axis=1)
    decoded_labels = encoder.inverse_transform(predicted_labels)

    # Collect into DataFrame
    output = []
    for i in range(len(meta)):
        output.append({
            "timestamp": meta[i]["timestamp"],
            "real_close": meta[i]["real_close"],
            "signal": decoded_labels[i],
            "confidence": confidences[i]
        })

    return pd.DataFrame(output).set_index("timestamp")