import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from server.data.market_data import MarketData
from server.data.data_preprocessing import create_labels
import pickle

MODEL_PATH = "server/ai_model/ai_model_tf.keras"
SCALER_PATH = "server/ai_model/scaler_tf.pkl"


def build_mlp_model(input_dim):
    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(3, activation='softmax')  # 3 класса: Hold, Buy, Sell
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
            return 1  # Buy
        elif row["Sell_Signal"] == 1:
            return 2  # Sell
        else:
            return 0  # Hold

    df["Target"] = df.apply(label, axis=1)
    X = df.drop(columns=["Buy_Signal", "Sell_Signal", "Target"])
    y = df["Target"].astype(int)

    return X, y


def train_tf_model(X, y):
    print("📦 Обучаем MLP-модель на TensorFlow...")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    model = build_mlp_model(X_train.shape[1])
    model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

    model.save(MODEL_PATH)
    print("✅ Модель сохранена в", MODEL_PATH)


def load_tf_model():
    if not os.path.exists(MODEL_PATH):
        raise ValueError("❌ TensorFlow модель не найдена!")
    return keras.models.load_model(MODEL_PATH)


def predict_tf(model, X):
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    X_scaled = scaler.transform(X)
    probs = model.predict(X_scaled)
    return np.argmax(probs, axis=1), probs


if __name__ == "__main__":
    # 🔍 Загружаем и подготавливаем данные
    df = MarketData.download_data("AAPL")
    df = create_labels(df)
    X, y = preprocess_data_for_tf(df)

    # 🧠 Обучаем модель
    train_tf_model(X, y)

    # ✅ Загружаем модель и делаем предсказания
    model = load_tf_model()
    classes, probs = predict_tf(model, X)

    print("🔮 Предсказания:", classes[:10])
    print("📊 Вероятности:", probs[:3])
