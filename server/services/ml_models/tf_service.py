import os
import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
from data.data_preprocessing import prepare_features_for_ml

MODEL_PATH = "services/ml_models/models/tf_model.keras"
SCALER_PATH = "services/ml_models/models/tf_scaler.pkl"

print("📦 MODEL_PATH:", MODEL_PATH)
print("📦 SCALER_PATH:", SCALER_PATH)

try:
    tf_model = tf.keras.models.load_model(MODEL_PATH)
    print("✅ tf_model загружена успешно")
except Exception as e:
    tf_model = None
    print(f"❌ tf_model ошибка загрузки: {e}")

try:
    with open(SCALER_PATH, "rb") as f:
        tf_scaler = pickle.load(f)
    print("✅ tf_scaler загружен успешно")
except Exception as e:
    tf_scaler = None
    print(f"❌ tf_scaler ошибка загрузки: {e}")

def predict_tf(df: pd.DataFrame, threshold: float = 0.6) -> str:
    if tf_model is None or tf_scaler is None or df.empty:
        print("⚠️ predict_tf: модель, скейлер или датафрейм отсутствуют")
        return None

    print(f"📊 ML Input df cols: {df.columns.tolist()}")
    X_scaled, _ = prepare_features_for_ml(df, tf_scaler)
    print(f"📊 ML Scaled shape: {X_scaled.shape}")

    if X_scaled.shape[0] == 0:
        print("⚠️ predict_tf: недостаточно данных после препроцессинга")
        return None

    probs = tf_model.predict(X_scaled[-1:])
    prob_buy = probs[0][1]
    prob_sell = probs[0][2]

    print(f"🔮 predict_tf probs: hold={probs[0][0]:.4f}, buy={prob_buy:.4f}, sell={prob_sell:.4f}")

    if prob_buy > threshold:
        return "buy"
    elif prob_sell > threshold:
        return "sell"
    return "hold"