from datetime import datetime, timedelta
from models import Strategy
from schemas import BacktestRequest
from sqlalchemy.orm import Session
from data.alpaca_data import fetch_history_alpaca
import pandas as pd
from utils.strategy_evaluator import eval_expr
from services.ml_models.rf_service import predict_rf
from services.ml_models.tf_service import predict_tf
from data.data_preprocessing import prepare_features_for_ml
from services.ml_models.tf_service import tf_model, tf_scaler
from data.market_data import MarketData

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

    return {
        "metrics": {key: metrics[key] for key in ["total_pnl", "win_rate", "trades", "sharpe_ratio", "max_drawdown", "average_pnl"]},
        "equity_curve": metrics["equity_curve"],
        "trades": metrics["trades"]
    }


def simulate_strategy(strategy: Strategy, df: pd.DataFrame):
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

    print("📊 Buy signals:", strategy.buy_signals)
    print("📊 Sell signals:", strategy.sell_signals)

    buy_expr = build_expr(strategy.buy_signals)
    sell_expr = build_expr(strategy.sell_signals)

    print("🧠 buy_expr:", buy_expr)
    print("🧠 sell_expr:", sell_expr)

    df["Buy"] = eval_expr(buy_expr, df) if buy_expr else False
    df["Sell"] = eval_expr(sell_expr, df) if sell_expr else False

    position = None  # None, 'long', or 'short'
    entry_price = 0
    trades_log = []
    pnl = 0
    trade_pnls = []

    use_ml = strategy.strategy_type in ("ml_rf", "ml_tf")

    for index, row in df.iterrows():
        current_price = row["Close"]

        # === Stop Loss / Take Profit for open position ===
        if position in ('long', 'short'):
            sl_triggered = False
            tp_triggered = False

            if strategy.stop_loss:
                if strategy.sl_tp_is_percent:
                    sl_threshold = entry_price * (1 - strategy.stop_loss / 100) if position == 'long' else entry_price * (1 + strategy.stop_loss / 100)
                else:
                    sl_threshold = entry_price - strategy.stop_loss if position == 'long' else entry_price + strategy.stop_loss
                sl_triggered = current_price <= sl_threshold if position == 'long' else current_price >= sl_threshold

            if strategy.take_profit:
                if strategy.sl_tp_is_percent:
                    tp_threshold = entry_price * (1 + strategy.take_profit / 100) if position == 'long' else entry_price * (1 - strategy.take_profit / 100)
                else:
                    tp_threshold = entry_price + strategy.take_profit if position == 'long' else entry_price - strategy.take_profit
                tp_triggered = current_price >= tp_threshold if position == 'long' else current_price <= tp_threshold

            if sl_triggered or tp_triggered:
                exit_price = current_price
                trade_pnl = exit_price - entry_price if position == 'long' else entry_price - exit_price
                trades_log.append({
                    "action": "exit",
                    "price": round(exit_price, 2),
                    "result": "stop_loss" if sl_triggered else "take_profit",
                    "pnl": round(trade_pnl, 2),
                    "time": index
                })
                pnl += trade_pnl
                trade_pnls.append(trade_pnl)
                position = None
                continue

       # === Machine Learning Predictions ===
        if use_ml:
            last_slice = df.loc[:index].tail(50).dropna()
            if len(last_slice) < 5:
                print(f"⚠️ Недостаточно данных для ML предсказания на {index}")
                continue

            ml_df = last_slice.drop(columns=["Buy", "Sell"], errors="ignore")
            ml_df = MarketData.calculate_indicators(ml_df)

            prediction = None

            if strategy.strategy_type == "ml_rf":
                prediction = predict_rf(ml_df)

            elif strategy.strategy_type == "ml_tf":
                print(f"📦 tf_model: {tf_model}")
                X_scaled, _ = prepare_features_for_ml(ml_df, tf_scaler)
                if X_scaled.shape[0] == 0:
                    continue
                probs = predict_tf(X_scaled[-1:])
                pred_class = np.argmax(probs[0])
                print(f"🔮 predict_tf raw prediction: {pred_class} (probs: {probs[0]})")
                prediction = {1: "buy", 2: "sell"}.get(pred_class, "hold")

            # === Логика торговли по AI ===
            if prediction == "buy":
                if position == "short":
                    exit_price = current_price
                    trade_pnl = entry_price - exit_price
                    trades_log.append({
                        "action": "buy", "price": round(exit_price, 2), "result": "closed", "pnl": round(trade_pnl, 2), "time": index
                    })
                    pnl += trade_pnl
                    trade_pnls.append(trade_pnl)
                    position = None
                if position is None:
                    position = "long"
                    entry_price = current_price
                    trades_log.append({
                        "action": "buy", "price": round(entry_price, 2), "result": "opened", "pnl": 0, "time": index
                    })

            elif prediction == "sell":
                if position == "long":
                    exit_price = current_price
                    trade_pnl = exit_price - entry_price
                    trades_log.append({
                        "action": "sell", "price": round(exit_price, 2), "result": "closed", "pnl": round(trade_pnl, 2), "time": index
                    })
                    pnl += trade_pnl
                    trade_pnls.append(trade_pnl)
                    position = None
                if position is None:
                    position = "short"
                    entry_price = current_price
                    trades_log.append({
                        "action": "sell", "price": round(entry_price, 2), "result": "opened", "pnl": 0, "time": index
                    })

        # === Open Long ===
        if row["Buy"] and position is None:
            position = 'long'
            entry_price = current_price
            trades_log.append({"action": "buy", "price": round(entry_price, 2), "result": "opened", "pnl": 0, "time": index})
            continue

        # === Open Short ===
        if row["Sell"] and position is None:
            position = 'short'
            entry_price = current_price
            trades_log.append({"action": "sell", "price": round(entry_price, 2), "result": "opened", "pnl": 0, "time": index})
            continue

        # === Close Long ===
        if row["Sell"] and position == 'long':
            position = None
            exit_price = current_price
            trade_pnl = exit_price - entry_price
            trades_log.append({"action": "sell", "price": round(exit_price, 2), "result": "closed", "pnl": round(trade_pnl, 2), "time": index})
            pnl += trade_pnl
            trade_pnls.append(trade_pnl)
            continue

        # === Close Short ===
        if row["Buy"] and position == 'short':
            position = None
            exit_price = current_price
            trade_pnl = entry_price - exit_price
            trades_log.append({"action": "buy", "price": round(exit_price, 2), "result": "closed", "pnl": round(trade_pnl, 2), "time": index})
            pnl += trade_pnl
            trade_pnls.append(trade_pnl)
            continue

    equity_curve = []
    cumulative = 0

    # Мапа: дата → pnl по сделке
    trade_pnl_map = {t["time"]: t["pnl"] for t in trades_log if t["result"] in ("closed", "stop_loss", "take_profit")}

    for index in df.index:
        pnl_step = trade_pnl_map.get(index, 0)
        cumulative += pnl_step
        equity_curve.append({"date": index.isoformat(), "pnl": round(cumulative, 4)})

    win_rate = (np.array(trade_pnls) > 0).mean() * 100 if trade_pnls else 0
    returns = [t["pnl"] for t in trades_log if t["result"] in ("closed", "stop_loss", "take_profit")]
    sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if len(returns) > 1 and np.std(returns) > 0 else 0

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