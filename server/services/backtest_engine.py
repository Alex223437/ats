from datetime import datetime
from models import Strategy
from schemas import BacktestRequest
from sqlalchemy.orm import Session
from data.alpaca_data import fetch_history_alpaca
from ai_model.predictors.predict_signals_batch import predict_signals_batch
from utils.simulate_rule_strategy import simulate_rule_strategy
from utils.simulate_ai_strategy import simulate_ai_strategy
from utils.calculate_metrics import calculate_metrics, calculate_equity_curve
import pandas as pd

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
        raise ValueError("Исторические данные не загружены?")

    if strategy.strategy_type == "ml_tf":
        trades_log, equity_curve, position, entry_price = simulate_ai_strategy(
            ticker=request.ticker,
            user_id=user_id,
            df=df
        )
    else:
        trades_log, equity_curve, position, entry_price = simulate_rule_strategy(strategy, df)

    
    metrics = calculate_metrics(trades_log, equity_curve)

    return {
        "metrics": metrics,
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
