import os
import time
import requests
import pandas as pd
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")

def fetch_ohlcv_polygon(ticker: str, from_date: str, to_date: str, timespan="hour", multiplier=1, api_key=API_KEY) -> pd.DataFrame:
    print(f"\n\U0001F4E1 Получение данных для: {ticker}")
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
    params = {"apiKey": api_key, "adjusted": "true", "sort": "asc", "limit": 50000}
    print(f"✨ URL: {url}")
    response = requests.get(url, params=params)
    data = response.json()
    if "results" not in data:
        print("❌ Ответ:", data)
        raise ValueError(f"❌ Нет данных по {ticker}: {data.get('message', 'Unknown error')}")
    df = pd.DataFrame(data["results"])
    print(f"📊 Загружено строк: {len(df)}")
    df.rename(columns={"t": "timestamp", "o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"}, inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    print("✅ OHLCV данные получены")
    return df

def fetch_ohlcv_range_quarterly(ticker: str, from_date: str, to_date: str, timespan="hour", multiplier=1, api_key=API_KEY) -> pd.DataFrame:
    print(f"\n\U0001F4F1 Загрузка данных по кварталам для: {ticker}")
    all_data = []
    current = pd.to_datetime(from_date)
    end = pd.to_datetime(to_date)
    while current < end:
        next_date = min(current + pd.DateOffset(months=3) - timedelta(days=1), end)
        print(f"📋 Период: {current.date()} — {next_date.date()}")
        try:
            chunk = fetch_ohlcv_polygon(ticker, current.strftime("%Y-%m-%d"), next_date.strftime("%Y-%m-%d"), timespan, multiplier, api_key)
            all_data.append(chunk)
            time.sleep(15)
        except Exception as e:
            print(f"⚠️ Пропущен период {current.date()} — {next_date.date()} из-за ошибки: {e}")
        current = next_date + timedelta(days=1)
    if not all_data:
        raise ValueError("❌ Не удалось загрузить ни одного квартала данных.")
    full_df = pd.concat(all_data).sort_index()
    print(f"✅ Загружено всего строк: {len(full_df)}")
    return full_df