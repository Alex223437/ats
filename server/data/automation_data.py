import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_API_SECRET")
ALPACA_BASE_URL = "https://data.alpaca.markets/v2/stocks/bars"

def fetch_intraday_alpaca(
    symbol: str,
    timeframe: str = "5Min",
    minutes_back: int = 60
) -> pd.DataFrame:
    """
    Fetches intraday stock data from Alpaca using IEX feed.
    :param symbol: e.g. "AAPL"
    :param timeframe: e.g. "1Min", "5Min"
    :param minutes_back: how many minutes back from now to load
    """
    end = datetime.utcnow()
    start = end - timedelta(minutes=minutes_back)

    headers = {
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY
    }

    params = {
        "symbols": symbol,
        "timeframe": timeframe,
        "start": start.isoformat() + "Z",
        "end": end.isoformat() + "Z",
        "limit": 1000,
        "feed": "iex",
        "adjustment": "raw",
        "sort": "asc"
    }

    print("🔗 Alpaca Params:", params)

    response = requests.get(ALPACA_BASE_URL, headers=headers, params=params)
    response.raise_for_status()
    json_data = response.json()

    if symbol not in json_data.get("bars", {}):
        print(f"⚠️ Нет данных по {symbol}")
        return pd.DataFrame()

    bars = json_data["bars"][symbol]

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