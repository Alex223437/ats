import os
import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
from data.data_preprocessing import prepare_features_for_ml

MODEL_PATH = "services/ml_models/models/tf_model.keras"
SCALER_PATH = "services/ml_models/models/tf_scaler.pkl"

try:
    tf_model = tf.keras.models.load_model(MODEL_PATH)
except Exception as e:
    tf_model = None
    print(f"⚠️ Ошибка загрузки TensorFlow модели: {e}")

try:
    with open(SCALER_PATH, "rb") as f:
        tf_scaler = pickle.load(f)
except Exception as e:
    tf_scaler = None
    print(f"⚠️ Ошибка загрузки скейлера TensorFlow: {e}")

def predict_tf(df: pd.DataFrame) -> str:
    if tf_model is None or tf_scaler is None or df.empty:
        print("⚠️ predict_tf: модель, скейлер или датафрейм отсутствуют")
        return None

    # Подготовка фичей так же, как в обучении
    X_scaled, _ = prepare_features_for_ml(df, tf_scaler)
    if X_scaled.shape[0] == 0:
        print("⚠️ predict_tf: недостаточно данных после препроцессинга")
        return None

    probs = tf_model.predict(X_scaled[-1:])
    pred_class = np.argmax(probs[0])
    print(f"🔮 predict_tf raw prediction: {pred_class} (probs: {probs[0]})")

    if pred_class == 1:
        return "buy"
    elif pred_class == 2:
        return "sell"
    return "hold"