import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score, log_loss
import joblib

from data.data_preprocessing import preprocess_data, create_labels, prepare_features_for_ml
from data.market_data import MarketData

MODEL_PATH = "services/ml_models/models/rf_model.pkl"
SCALER_PATH = "services/ml_models/models/scaler_rf.pkl"
LAST_TRAIN_PATH = "services/ml_models/models/last_train.txt"
TRAIN_INTERVAL_DAYS = 7

def should_retrain():
    if not os.path.exists(LAST_TRAIN_PATH):
        return True
    with open(LAST_TRAIN_PATH, "r") as f:
        last_train_date = datetime.strptime(f.read().strip(), "%Y-%m-%d")
    return (datetime.now() - last_train_date).days >= TRAIN_INTERVAL_DAYS

def save_train_date():
    with open(LAST_TRAIN_PATH, "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d"))

def evaluate_model(model, X_test, y_test, feature_names):
    y_pred = model.predict(X_test)
    if hasattr(model, "predict_proba"):
        y_pred_prob = np.array(model.predict_proba(X_test))
        if y_pred_prob.ndim == 3:
            y_pred_prob = np.mean(y_pred_prob, axis=0)
        print("📉 Log Loss:", log_loss(y_test, y_pred_prob))
    print("📊 Accuracy:", accuracy_score(y_test, y_pred))
    print("🔎 Precision:", precision_score(y_test, y_pred, average="weighted"))
    print("📉 Recall:", recall_score(y_test, y_pred, average="weighted"))
    print("📊 F1-score:", f1_score(y_test, y_pred, average="weighted"))
    print(classification_report(y_test, y_pred))
    feature_importance = model.feature_importances_
    feature_names = feature_names[:len(feature_importance)]
    plt.figure(figsize=(10, 5))
    plt.barh(feature_names, feature_importance, color='skyblue')
    plt.xlabel("Важность признаков")
    plt.ylabel("Фичи")
    plt.title("Feature Importance в RandomForest")
    plt.show()

def train_model(tickers=["AAPL", "TSLA", "NVDA", "GOOGL", "AMZN"]):
    if not should_retrain():
        print("✅ Модель уже обучена недавно, переобучение не требуется.")
        return

    all_data = []
    for ticker in tickers:
        try:
            data = MarketData.download_data(ticker)
            if data is None or data.empty:
                print(f"⚠️ Пропускаем {ticker}, данных нет")
                continue
            data = create_labels(data)  # добавит Target: -1, 0, 1
            data["Ticker"] = ticker
            all_data.append(data)
        except Exception as e:
            print(f"❌ Ошибка при загрузке {ticker}: {e}")

    if not all_data:
        raise ValueError("❌ Не удалось загрузить данные ни для одного тикера")

    full_data = pd.concat(all_data, axis=0)

    # One-hot encoding для тикеров
    encoder = OneHotEncoder(sparse_output=False, drop='first')
    ticker_encoded = encoder.fit_transform(full_data[['Ticker']])
    ticker_df = pd.DataFrame(ticker_encoded, columns=encoder.get_feature_names_out(['Ticker']))

    full_data = full_data.drop(columns=['Ticker']).reset_index(drop=True)
    ticker_df = ticker_df.reset_index(drop=True)
    full_data = pd.concat([full_data, ticker_df], axis=1)

    # X — без масштабирования, y = Target
    X, y = preprocess_data(full_data)
    if y is None or y.empty:
        raise ValueError("❌ Нет таргетов для обучения (Target)")

    # Сохраняем и применяем масштабирование
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, SCALER_PATH)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    param_grid = {
        "n_estimators": [50, 100],
        "max_depth": [None, 10],
        "min_samples_split": [2, 5],
        "min_samples_leaf": [1, 2]
    }

    model = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(model, param_grid, cv=3, n_jobs=-1, verbose=2)
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_

    evaluate_model(best_model, X_test, y_test, X.columns.tolist())

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(best_model, f)

    save_train_date()
    print("🎯 Оптимизированная модель обучена и сохранена!")

if __name__ == "__main__":
    train_model()

