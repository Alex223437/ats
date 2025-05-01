import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

class MarketData:
    @staticmethod
    def download_data(ticker: str, multiplier=1, timespan='day', from_date='2024-01-01', to_date='2025-01-01', use_api=False):
        """Загрузка исторических данных через Polygon.io + расчет индикаторов (локально или через API)"""
        print(f"🔍 Загружаем данные для {ticker} с {from_date} по {to_date}...")

        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        params = {"apiKey": POLYGON_API_KEY}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if "results" not in data or not data["results"]:
                raise ValueError("Данные отсутствуют или API-ключ недействителен.")

            df = pd.DataFrame(data["results"])

            # Приводим к стандартным именам столбцов
            df = df.rename(columns={
                't': 'Date',
                'o': 'Open',
                'h': 'High',
                'l': 'Low',
                'c': 'Close',
                'v': 'Volume'
            })

            # Преобразуем timestamp в дату
            df['Date'] = pd.to_datetime(df['Date'], unit='ms')
            df = df.set_index('Date')

            # Если включен API-режим, загружаем индикаторы через Polygon.io
            if use_api:
                df = MarketData.fetch_indicators_from_api(df, ticker)
            else:
                df = MarketData.calculate_indicators(df)

            print(f"✅ Данные успешно загружены для {ticker}")
            return df

        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка загрузки данных с Polygon.io: {e}")
            return None

    @staticmethod
    def fetch_indicators_from_api(df, ticker):
        """Загружаем индикаторы через API Polygon.io"""
        indicators = ["sma", "ema", "macd", "rsi"]
        for indicator in indicators:
            try:
                url = f"https://api.polygon.io/v1/indicators/{indicator}/{ticker}"
                params = {"apiKey": POLYGON_API_KEY}
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if "results" in data and data["results"]:
                    df[indicator.upper()] = [x["value"] for x in data["results"]]

            except requests.exceptions.RequestException as e:
                print(f"⚠️ Ошибка загрузки {indicator.upper()} с API: {e}")

        return df

    @staticmethod
    def calculate_indicators(df):
        """Локальный расчет технических индикаторов"""

        # ✅ SMA (Simple Moving Average)
        df['SMA_10'] = df['Close'].rolling(window=10, min_periods=1).mean()
        df['SMA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()

        # ✅ EMA (Exponential Moving Average)
        df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()

        # ✅ RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / (loss + 1e-10)  # избегаем деления на ноль
        df['RSI_14'] = 100 - (100 / (1 + rs))

        # ✅ MACD (Moving Average Convergence Divergence)
        short_ema = df['Close'].ewm(span=12, adjust=False).mean()
        long_ema = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = short_ema - long_ema
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

        return df