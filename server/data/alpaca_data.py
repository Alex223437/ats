import requests
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime

# загрузка .env переменных
load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_API_SECRET")
ALPACA_BASE_URL = "https://data.alpaca.markets/v2/stocks/bars"


def fetch_history_alpaca(
    symbol: str,
    start: datetime,
    end: datetime,
    timeframe: str = "1Hour"
) -> pd.DataFrame:
    headers = {
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
    }

    params = {
        "symbols": symbol,
        "timeframe": timeframe,
        "start": start.replace(tzinfo=None).isoformat() + "Z",
        "end": end.replace(tzinfo=None).isoformat() + "Z",
        "limit": 10000,
        "feed": "iex",
        "adjustment": "raw",
        "sort": "asc"
    }

    print("🔗 Alpaca Params:", params)

    response = requests.get(ALPACA_BASE_URL, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if symbol not in data.get("bars", {}):
        print(f"⚠️ Нет данных по {symbol}")
        return pd.DataFrame()

    bars = data["bars"][symbol]

    records = [
        {
            "Date": bar["t"],
            "Open": bar["o"],
            "High": bar["h"],
            "Low": bar["l"],
            "Close": bar["c"],
            "Volume": bar["v"]
        }
        for bar in bars
    ]

    df = pd.DataFrame(records)
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    print(f"✅ Получено {len(df)} записей по {symbol} с Alpaca")
    return df