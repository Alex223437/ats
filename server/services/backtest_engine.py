from datetime import datetime, timedelta
from models import Strategy
from schemas import BacktestRequest
from sqlalchemy.orm import Session
from models.backtest_result import BacktestResult
from data.alpaca_data import fetch_history_alpaca
import pandas as pd
from utils.strategy_evaluator import eval_expr
import numpy as np

def build_expr(signals):
        expressions = []
        for s in signals:
            raw_indicator = s.get('indicator')
            operator = s.get('operator', '>')
            value = s.get('value')

            if not raw_indicator or value is None:
                continue

            # 🩹 Временная подмена Bollinger Bands → BB_lower
            indicator = "BB_lower" if raw_indicator == "Bollinger Bands" else raw_indicator

            expressions.append(f"{indicator} {operator} {value}")
        return " and ".join(expressions)


def run_backtest(request: BacktestRequest, user_id: int, db: Session):
    strategy = db.query(Strategy).filter_by(id=request.strategy_id, user_id=user_id).first()
    if not strategy:
        raise ValueError("Strategy not found")

    df = fetch_history_alpaca(
        symbol=request.ticker,
        start=request.start_date,
        end=request.end_date,
        timeframe="1Hour"
    )

    if df is None or df.empty:
        raise ValueError("Исторические данные не загружены")

    metrics = simulate_strategy(strategy, df)

    result = BacktestResult(
        user_id=user_id,
        strategy_id=request.strategy_id,
        parameters=request.parameters,
        ticker=request.ticker,
        start_date=request.start_date,
        end_date=request.end_date,
        metrics={key: metrics[key] for key in ["total_pnl", "win_rate", "trades", "sharpe_ratio", "max_drawdown", "average_pnl"]},
        equity_curve=metrics["equity_curve"],
        trades=metrics["trades"]
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def simulate_strategy(strategy: Strategy, df: pd.DataFrame):
    df = df.copy()
    df = df.rename(columns={"close": "Close", "volume": "Volume"})

        # Подготовка индикаторов, если они встречаются в выражениях
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

    # 🔍 Логируем входные сигналы
    print("📊 Buy signals:", strategy.buy_signals)
    print("📊 Sell signals:", strategy.sell_signals)

    

    buy_expr = build_expr(strategy.buy_signals)
    sell_expr = build_expr(strategy.sell_signals)


    print("🧠 buy_expr:", buy_expr)
    print("🧠 sell_expr:", sell_expr)

    df["Buy"] = eval_expr(buy_expr, df) if buy_expr else False
    df["Sell"] = eval_expr(sell_expr, df) if sell_expr else False

    position = 0
    entry_price = 0
    trades_log = []
    pnl = 0
    trade_pnls = []

    for index, row in df.iterrows():
        if row["Buy"] and position == 0:
            position = 1
            entry_price = row["Close"]
            trades_log.append({"action": "buy", "price": round(entry_price, 2), "result": "opened", "pnl": 0, "time": index})
        elif row["Sell"] and position == 1:
            position = 0
            exit_price = row["Close"]
            trade_pnl = exit_price - entry_price
            trades_log.append({"action": "sell", "price": round(exit_price, 2), "result": "closed", "pnl": round(trade_pnl, 2), "time": index})
            pnl += trade_pnl
            trade_pnls.append(trade_pnl)

    df["Equity"] = df["Close"].pct_change().fillna(0)
    df["Strategy"] = df["Equity"] * df["Buy"].astype(int)

    cumulative = 0
    equity_curve = []
    for d, v in df["Strategy"].items():
        cumulative += v
        equity_curve.append({"date": d.isoformat(), "pnl": round(cumulative, 4)})

    win_rate = (np.array(trade_pnls) > 0).mean() * 100 if trade_pnls else 0
    sharpe_ratio = (np.mean(df["Strategy"]) / np.std(df["Strategy"])) * np.sqrt(252) if np.std(df["Strategy"]) > 0 else 0

    peak = max_drawdown = 0
    curve = [point["pnl"] for point in equity_curve]
    for val in curve:
        if val > peak:
            peak = val
        drawdown = peak - val
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    avg_pnl = np.mean(trade_pnls) if trade_pnls else 0

    return {
        "total_pnl": round(pnl, 2),
        "trades": len(trade_pnls),
        "win_rate": round(win_rate, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "max_drawdown": round(max_drawdown, 2),
        "average_pnl": round(avg_pnl, 2),
        "equity_curve": equity_curve,
        "trades": [
            {
                "action": t["action"],
                "price": t["price"],
                "result": t["result"],
                "pnl": t["pnl"],
                "time": t["time"].isoformat() if isinstance(t["time"], pd.Timestamp) else t["time"]
            } for t in trades_log
        ]
    }