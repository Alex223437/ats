import os
import pickle
import numpy as np
import pandas as pd
import joblib
from data.data_preprocessing import prepare_features_for_ml

MODEL_PATH = "services/ml_models/models/rf_model.pkl"
SCALER_PATH = "services/ml_models/models/scaler_rf.pkl"

try:
    with open(MODEL_PATH, "rb") as f:
        rf_model = pickle.load(f)
except FileNotFoundError:
    rf_model = None
    print("⚠️ Random Forest модель не найдена")

try:
    scaler = joblib.load(SCALER_PATH)
except FileNotFoundError:
    scaler = None
    print("⚠️ Scaler для Random Forest не найден")

def predict_rf(df: pd.DataFrame) -> str:
    global rf_model, scaler

    if df.empty:
        print("⚠️ predict_rf: пустой DataFrame")
        return None

    if rf_model is None:
        if not os.path.exists(MODEL_PATH):
            print("❌ Модель не найдена")
            return None
        with open(MODEL_PATH, "rb") as f:
            rf_model = pickle.load(f)

    if scaler is None:
        if not os.path.exists(SCALER_PATH):
            print("❌ Scaler не найден")
            return None
        scaler = joblib.load(SCALER_PATH)

    X_scaled, _ = prepare_features_for_ml(df, scaler)
    if X_scaled.shape[0] == 0:
        print("⚠️ predict_rf: нет нормализованных данных")
        return None

    raw = rf_model.predict(X_scaled[-1:])

    # Если вдруг модель возвращает array-of-array — достаём скаляр
    prediction = raw[0]
    if isinstance(prediction, (np.ndarray, list)):
        prediction = prediction[0]

    if prediction == 1:
        return "buy"
    elif prediction == -1:
        return "sell"
    return "hold"