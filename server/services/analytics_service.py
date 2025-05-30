from sqlalchemy.orm import Session
from models.trade_log import TradeLog
from models.strategy import Strategy
from models.user import User
from sqlalchemy import func, desc
from datetime import datetime
from typing import Optional
import numpy as np

def get_overview_analytics(
    db: Session,
    user: User,
    strategy_id: Optional[int] = None,
    ticker: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(TradeLog).filter(TradeLog.user_id == user.id)

    if strategy_id:
        query = query.filter(TradeLog.strategy_id == strategy_id)
    if ticker:
        query = query.filter(TradeLog.symbol == ticker)
    if start_date:
        query = query.filter(TradeLog.timestamp >= start_date)
    if end_date:
        query = query.filter(TradeLog.timestamp <= end_date)

    trades = query.all()

    total_trades = len([t for t in trades if not t.is_order])
    total_orders = len([t for t in trades if t.is_order])
    success_trades = len([t for t in trades if t.pnl and t.pnl > 0])
    win_rate = (success_trades / total_trades) * 100 if total_trades > 0 else 0
    total_pnl = sum(t.pnl for t in trades if t.pnl)
    average_pnl = total_pnl / total_trades if total_trades > 0 else 0

    pnl_curve = []
    pnl_series = []
    cumulative = 0
    for t in sorted(trades, key=lambda x: x.timestamp):
        if t.pnl is not None:
            cumulative += t.pnl
            pnl_curve.append(cumulative)
            pnl_series.append(t.pnl)

    peak = max_drawdown = 0
    for x in pnl_curve:
        if x > peak:
            peak = x
        drawdown = peak - x
        max_drawdown = max(max_drawdown, drawdown)

    sharpe_ratio = 0.0
    if len(pnl_series) >= 2:
        mean_return = np.mean(pnl_series)
        std_dev = np.std(pnl_series)
        if std_dev != 0:
            sharpe_ratio = mean_return / std_dev

    return {
        "total_trades": total_trades,
        "total_orders": total_orders,
        "success_trades": success_trades,
        "win_rate": round(win_rate, 2),
        "total_pnl": round(total_pnl, 2),
        "average_pnl": round(average_pnl, 2),
        "max_drawdown": round(max_drawdown, 2),
        "sharpe_ratio": round(sharpe_ratio, 2)
    }

def get_strategies_pnl(
    db: Session,
    user: User,
    strategy_id: int = None,
    ticker: str = None,
    start_date: datetime = None,
    end_date: datetime = None
):
    query = (
        db.query(
            TradeLog.strategy_id,
            Strategy.title,
            func.sum(TradeLog.pnl).label("total_pnl")
        )
        .join(Strategy, Strategy.id == TradeLog.strategy_id)
        .filter(
            TradeLog.user_id == user.id,
            TradeLog.is_order == False,
            TradeLog.pnl.isnot(None)
        )
    )

    if strategy_id:
        query = query.filter(TradeLog.strategy_id == strategy_id)
    if ticker:
        query = query.filter(TradeLog.symbol == ticker)
    if start_date:
        query = query.filter(TradeLog.timestamp >= start_date)
    if end_date:
        query = query.filter(TradeLog.timestamp <= end_date)

    results = query.group_by(TradeLog.strategy_id, Strategy.title).all()

    return [
        {
            "strategy_id": row.strategy_id,
            "title": row.title,
            "pnl": round(row.total_pnl, 2) if row.total_pnl else 0.0
        }
        for row in results
    ]

def get_top_tickers(
    db: Session,
    user: User,
    limit: int = 5,
    strategy_id: int = None,
    ticker: str = None,
    start_date: datetime = None,
    end_date: datetime = None
):
    query = (
        db.query(
            TradeLog.symbol,
            func.sum(TradeLog.pnl).label("total_pnl")
        )
        .filter(
            TradeLog.user_id == user.id,
            TradeLog.is_order == False,
            TradeLog.pnl.isnot(None)
        )
    )

    if strategy_id:
        query = query.filter(TradeLog.strategy_id == strategy_id)
    if ticker:
        query = query.filter(TradeLog.symbol == ticker)
    if start_date:
        query = query.filter(TradeLog.timestamp >= start_date)
    if end_date:
        query = query.filter(TradeLog.timestamp <= end_date)

    results = (
        query.group_by(TradeLog.symbol)
        .order_by(desc("total_pnl"))
        .limit(limit)
        .all()
    )

    return [
        {
            "symbol": row.symbol,
            "pnl": round(row.total_pnl, 2) if row.total_pnl else 0.0
        }
        for row in results
    ]

def get_equity_curve(
    db: Session,
    user: User,
    strategy_id: Optional[int] = None,
    ticker: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(TradeLog).filter(
        TradeLog.user_id == user.id,
        TradeLog.is_order == False,
        TradeLog.pnl.isnot(None)
    )

    if strategy_id:
        query = query.filter(TradeLog.strategy_id == strategy_id)
    if ticker:
        query = query.filter(TradeLog.symbol == ticker)
    if start_date:
        query = query.filter(TradeLog.timestamp >= start_date)
    if end_date:
        query = query.filter(TradeLog.timestamp <= end_date)

    trades = query.order_by(TradeLog.timestamp.asc()).all()

    cumulative = 0
    daily_pnls = {}

    for t in trades:
        date_key = t.timestamp.date()
        cumulative += t.pnl
        daily_pnls[date_key] = cumulative

    return [
        {"date": date, "pnl": pnl}
        for date, pnl in sorted(daily_pnls.items())
    ]