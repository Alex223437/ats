import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_API_SECRET")
ALPACA_BASE_URL = "https://data.alpaca.markets/v2/stocks/bars"

def fetch_intraday_alpaca(
    symbol: str,
    timeframe: str = "5Min",
    start_date: datetime = None,
    end_date: datetime = None
) -> pd.DataFrame:
    """
    Download intraday market data from Alpaca API.
    """
    end = end_date or datetime.utcnow()
    start = start_date or (end - timedelta(days=7)) 

    headers = {
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY
    }

    params = {
        "symbols": symbol,
        "timeframe": timeframe,
        "start": start.isoformat() + "Z",
        "end": end.isoformat() + "Z",
        "limit": 10000, 
        "feed": "iex",
        "adjustment": "raw",
        "sort": "asc"
    }

    response = requests.get(ALPACA_BASE_URL, headers=headers, params=params)
    response.raise_for_status()
    json_data = response.json()

    if symbol not in json_data.get("bars", {}):
        print(f"No data for {symbol}")
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

    print(f"Recieved {len(df)} candles {symbol} from Alpaca")
    return df