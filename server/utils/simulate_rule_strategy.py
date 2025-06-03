import pandas as pd
from utils.strategy_evaluator import eval_expr


def build_expr(signals):
    expressions = []
    for s in signals:
        raw_indicator = s.get("indicator")
        operator = s.get("operator", ">")
        value = s.get("value")

        if not raw_indicator or value is None:
            continue

        indicator = "BB_lower" if raw_indicator == "Bollinger Bands" else raw_indicator
        expressions.append(f"{indicator} {operator} {value}")
    return " and ".join(expressions)


def simulate_rule_strategy(strategy, df: pd.DataFrame) -> tuple[list[dict], list[dict], str | None, float | None]:
    df = df.copy()
    df = df.rename(columns={"close": "Close", "volume": "Volume"})

    needed_cols = [s["indicator"] for s in strategy.buy_signals + strategy.sell_signals]
    if "EMA_10" in needed_cols:
        df["EMA_10"] = df["Close"].ewm(span=10).mean()
    if "SMA_10" in needed_cols:
        df["SMA_10"] = df["Close"].rolling(window=10).mean()
    if "RSI" in needed_cols:
        delta = df["Close"].diff()
        up = delta.clip(lower=0).rolling(14).mean()
        down = -delta.clip(upper=0).rolling(14).mean()
        rs = up / down
        df["RSI"] = 100 - (100 / (1 + rs))
    if "MACD" in needed_cols:
        exp1 = df["Close"].ewm(span=12, adjust=False).mean()
        exp2 = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = exp1 - exp2
    if "Bollinger Bands" in needed_cols or "BB_upper" in needed_cols or "BB_lower" in needed_cols:
        sma = df["Close"].rolling(window=20).mean()
        std = df["Close"].rolling(window=20).std()
        df["BB_upper"] = sma + 2 * std
        df["BB_lower"] = sma - 2 * std

    buy_expr = build_expr(strategy.buy_signals)
    sell_expr = build_expr(strategy.sell_signals)

    df["Buy"] = eval_expr(buy_expr, df) if buy_expr else False
    df["Sell"] = eval_expr(sell_expr, df) if sell_expr else False

    position = None
    entry_price = None
    trades_log = []
    equity_curve = []

    cumulative_pnl = 0.0

    for index, row in df.iterrows():
        current_price = row["Close"]
        realized_pnl = 0.0

        if position in ("long", "short"):
            sl_triggered = tp_triggered = False

            if strategy.stop_loss:
                sl_threshold = entry_price * (1 - strategy.stop_loss / 100) if position == "long" else entry_price * (1 + strategy.stop_loss / 100)
                sl_triggered = current_price <= sl_threshold if position == "long" else current_price >= sl_threshold

            if strategy.take_profit:
                tp_threshold = entry_price * (1 + strategy.take_profit / 100) if position == "long" else entry_price * (1 - strategy.take_profit / 100)
                tp_triggered = current_price >= tp_threshold if position == "long" else current_price <= tp_threshold

            if sl_triggered or tp_triggered:
                exit_price = current_price
                trade_pnl = (
                    ((exit_price - entry_price) / entry_price) * 100
                    if position == "long"
                    else ((entry_price - exit_price) / entry_price) * 100
                )
                realized_pnl = trade_pnl
                trades_log.append({
                    "action": "exit",
                    "price": round(exit_price, 2),
                    "result": "stop_loss" if sl_triggered else "take_profit",
                    "pnl": round(trade_pnl, 4),
                    "time": index
                })
                position = None
                entry_price = None

        if row["Buy"] and position is None:
            position = "long"
            entry_price = current_price
            trades_log.append({"action": "buy", "price": round(entry_price, 2), "result": "opened", "pnl": 0, "time": index})

        elif row["Sell"] and position is None:
            position = "short"
            entry_price = current_price
            trades_log.append({"action": "sell", "price": round(entry_price, 2), "result": "opened", "pnl": 0, "time": index})

        elif row["Sell"] and position == "long":
            exit_price = current_price
            trade_pnl = ((exit_price - entry_price) / entry_price) * 100
            realized_pnl = trade_pnl
            trades_log.append({"action": "sell", "price": round(exit_price, 2), "result": "closed", "pnl": round(trade_pnl, 4), "time": index})
            position = None
            entry_price = None

        elif row["Buy"] and position == "short":
            exit_price = current_price
            trade_pnl = ((entry_price - exit_price) / entry_price) * 100
            realized_pnl = trade_pnl
            trades_log.append({"action": "buy", "price": round(exit_price, 2), "result": "closed", "pnl": round(trade_pnl, 4), "time": index})
            position = None
            entry_price = None

        cumulative_pnl += realized_pnl

        unrealized_pnl = 0.0
        if position == "long":
            unrealized_pnl = ((current_price - entry_price) / entry_price) * 100
        elif position == "short":
            unrealized_pnl = ((entry_price - current_price) / entry_price) * 100

        equity_curve.append({
            "date": index.isoformat(),
            "pnl": round(cumulative_pnl + unrealized_pnl, 4)
        })

    return trades_log, equity_curve, position, entry_price