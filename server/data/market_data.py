import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
from functools import lru_cache

load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

_data_cache = {}  # Простое in-memory кэш-хранилище

def _cache_key(ticker, from_date, to_date):
    return f"{ticker}_{from_date}_{to_date}"

class MarketData:
    @staticmethod
    def download_data(ticker: str, multiplier=1, timespan='hour', from_date=None, to_date=None, use_api=False, force_reload=False):
        """Загрузка часовых исторических данных через Polygon.io + расчёт индикаторов"""

        # 🗓 Авто-период: последние 90 дней
        if to_date is None:
            to_date = str(datetime.today().date())
        if from_date is None:
            from_date = str((datetime.today() - timedelta(days=90)).date())

        key = _cache_key(ticker, from_date, to_date)
        if not force_reload and key in _data_cache:
            print(f"🧠 Кэш: {ticker} ({from_date} → {to_date})")
            return _data_cache[key]

        print(f"🌐 Polygon: {ticker} ({from_date} → {to_date})")
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        params = {
            "apiKey": POLYGON_API_KEY,
            "limit": 50000,  # ⛽ побольше лимит для H1
            "adjustment": "raw",
            "sort": "asc"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if "results" not in data or not data["results"]:
                raise ValueError("Нет данных или неверный API-ключ.")

            df = pd.DataFrame(data["results"]).rename(columns={
                't': 'Date',
                'o': 'Open',
                'h': 'High',
                'l': 'Low',
                'c': 'Close',
                'v': 'Volume'
            })

            df['Date'] = pd.to_datetime(df['Date'], unit='ms')
            df = df.set_index('Date')

            df = MarketData.fetch_indicators_from_api(df, ticker) if use_api else MarketData.calculate_indicators(df)

            _data_cache[key] = df
            print(f"✅ Успешно: {ticker}")
            return df

        except requests.exceptions.RequestException as e:
            print(f"❌ Polygon Error: {e}")
            return None

    @staticmethod
    def fetch_indicators_from_api(df, ticker):
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
                print(f"⚠️ {indicator.upper()} API Error: {e}")

        return df

    @staticmethod
    def calculate_indicators(df):
        df['SMA_10'] = df['Close'].rolling(window=10, min_periods=1).mean()
        df['SMA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()
        df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()

        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14, min_periods=1).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14, min_periods=1).mean()
        rs = gain / (loss + 1e-10)
        df['RSI_14'] = 100 - (100 / (1 + rs))

        short_ema = df['Close'].ewm(span=12, adjust=False).mean()
        long_ema = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = short_ema - long_ema
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df["Volatility"] = df["High"] - df["Low"]
        df["Daily_Return"] = (df["Close"] - df["Open"]) / df["Open"]

        return df