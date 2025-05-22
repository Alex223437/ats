import pickle
import pandas as pd
from data.data_preprocessing import preprocess_data

def load_model():
    """Загрузка обученной модели"""
    with open("ai_model/ai_model.pkl", "rb") as f:
        model = pickle.load(f)
    return model

def predict_signals(data):
    """Прогнозируем сигналы на новых данных"""
    model = load_model()
     # Удаляем целевые колонки, если они присутствуют (их нет при инференсе)
    data = data.drop(columns=["Buy_Signal", "Sell_Signal"], errors="ignore")
    X_new, _ = preprocess_data(data)
    predictions = model.predict(X_new)

    data['Buy_Prediction'] = predictions[:, 0]
    data['Sell_Prediction'] = predictions[:, 1]

    return data