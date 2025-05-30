import pandas as pd

TAKE_PROFIT = 1.0 
STOP_LOSS = -0.5   
MIN_CONFIDENCE = 0.4
# ALLOWED_HOURS = [9, 10, 11, 12, 13, 14, 15, 16, 17]  # UTC hours for trading
OFFSET_TICKS = 3

def execute_conservative_strategy(df: pd.DataFrame) -> tuple[list[dict], list[dict], str | None, float | None]:
    df = df.copy()
    df = df.sort_index()
    df = df[df["confidence"] >= MIN_CONFIDENCE]
    # df = df[df.index.hour.isin(ALLOWED_HOURS)]

    trades = []
    equity_curve = []

    position = None
    entry_price = None
    entry_time = None
    cooldown = 0
    cumulative = 0.0

    for timestamp, row in df.iterrows():
        signal = row["signal"]
        price = row["real_close"]

        if cooldown > 0:
            cooldown -= 1
            equity_curve.append({"date": timestamp.isoformat(), "pnl": round(cumulative, 4)})
            continue

        if position is None:
            if signal == "buy":
                position = "long"
                entry_price = price
                entry_time = timestamp
                trades.append({"action": "buy", "price": round(price, 2), "result": "opened", "pnl": 0, "time": timestamp})
            elif signal == "sell":
                position = "short"
                entry_price = price
                entry_time = timestamp
                trades.append({"action": "sell", "price": round(price, 2), "result": "opened", "pnl": 0, "time": timestamp})
            equity_curve.append({"date": timestamp.isoformat(), "pnl": round(cumulative, 4)})
            continue

        change = ((price - entry_price) / entry_price * 100) if position == "long" else ((entry_price - price) / entry_price * 100)
        if change >= TAKE_PROFIT or change <= STOP_LOSS:
            pnl = change
            cumulative += pnl
            trades.append({"action": "sell" if position == "long" else "buy", "price": round(price, 2),
                           "result": "closed", "pnl": round(pnl, 4), "time": timestamp})
            equity_curve.append({"date": timestamp.isoformat(), "pnl": round(cumulative, 4)})
            position = None
            entry_price = None
            entry_time = None
            cooldown = OFFSET_TICKS
            continue

        if (position == "long" and signal == "sell") or (position == "short" and signal == "buy"):
            pnl = ((price - entry_price) / entry_price * 100) if position == "long" else ((entry_price - price) / entry_price * 100)
            cumulative += pnl
            trades.append({"action": "sell" if position == "long" else "buy", "price": round(price, 2),
                           "result": "closed", "pnl": round(pnl, 4), "time": timestamp})
            equity_curve.append({"date": timestamp.isoformat(), "pnl": round(cumulative, 4)})
            position = None
            entry_price = None
            entry_time = None
            cooldown = OFFSET_TICKS
            continue

        if position == "long":
            unrealized = (price - entry_price) / entry_price * 100
            equity_curve.append({"date": timestamp.isoformat(), "pnl": round(cumulative + unrealized, 4)})
        elif position == "short":
            unrealized = (entry_price - price) / entry_price * 100
            equity_curve.append({"date": timestamp.isoformat(), "pnl": round(cumulative + unrealized, 4)})
        else:
            equity_curve.append({"date": timestamp.isoformat(), "pnl": round(cumulative, 4)})

    return trades, equity_curve, position, entry_price