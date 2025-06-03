import pandas as pd
import numpy as np

TAKE_PROFIT = 0.01 
STOP_LOSS = -0.005  
# ALLOWED_HOURS = range(15, 22)
MIN_CONFIDENCE = 0.4


def run_conservative_strategy(df: pd.DataFrame, current_position: dict | None = None) -> dict:
    """
    Executes a conservative trading strategy based on the latest signals in the DataFrame.
    
    current_position: dict = {
        "type": "long" | "short",
        "entry_price": float,
        "entry_time": datetime
    }
    """
    df = df.copy()
    df = df.sort_values("timestamp").reset_index(drop=True)

    latest = df.iloc[-1]
    signal = latest["signal"]
    price = latest["real_close"]
    time = latest["timestamp"]
    confidence = latest.get("confidence", 1.0)

    if confidence < MIN_CONFIDENCE:
        return None
    # if time.hour not in ALLOWED_HOURS:
    #     return None

    if current_position is None:
        if signal == "buy":
            return {"action": "open", "type": "long", "price": price, "time": time}
        elif signal == "sell":
            return {"action": "open", "type": "short", "price": price, "time": time}
        else:
            return None

    pos_type = current_position["type"]
    entry_price = current_position["entry_price"]
    entry_time = current_position["entry_time"]

    change = (price - entry_price) / entry_price if pos_type == "long" else (entry_price - price) / entry_price

    if change >= TAKE_PROFIT:
        return {"action": "close", "reason": "take_profit", "price": price, "time": time}
    elif change <= STOP_LOSS:
        return {"action": "close", "reason": "stop_loss", "price": price, "time": time}

    if (pos_type == "long" and signal == "sell") or (pos_type == "short" and signal == "buy"):
        return {"action": "close", "reason": "opposite_signal", "price": price, "time": time}

    return {"action": "hold"}
