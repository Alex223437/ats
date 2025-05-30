from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.signal_log import SignalLog
from models.trade_log import TradeLog
from models.user import User
from routes.auth import get_current_user
from schemas.signal_log import SignalLogResponse, SignalLogUpdate
from schemas.trade_log import TradeLogResponse, TradeLogUpdate
from schemas.analytics import AnalyticsOverviewResponse, StrategyPnlItem, TopTickerItem, DailyPnlItem
from services.analytics_service import get_overview_analytics, get_strategies_pnl, get_top_tickers, get_equity_curve

analytics_router = APIRouter()

@analytics_router.get("/analytics/trades", response_model=List[TradeLogResponse])
def get_trades(
    strategy_id: Optional[int] = Query(None),
    ticker: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(TradeLog).filter(TradeLog.user_id == user.id)
    if strategy_id is not None:
        query = query.filter(TradeLog.strategy_id == strategy_id)
    if ticker:
        query = query.filter(TradeLog.symbol == ticker)
    if start_date:
        query = query.filter(TradeLog.timestamp >= start_date)
    if end_date:
        query = query.filter(TradeLog.timestamp <= end_date)
    return query.order_by(TradeLog.timestamp.desc()).all()


@analytics_router.put("/analytics/signals/{signal_id}", response_model=SignalLogResponse)
def update_signal_status(
    signal_id: int,
    update: SignalLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    signal = db.query(SignalLog).filter_by(id=signal_id, user_id=user.id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    if update.executed is not None:
        signal.executed = update.executed

    db.commit()
    db.refresh(signal)
    return signal


@analytics_router.put("/analytics/trades/{trade_id}", response_model=TradeLogResponse)
def update_trade_log(
    trade_id: int,
    update: TradeLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    trade = db.query(TradeLog).filter_by(id=trade_id, user_id=user.id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    if update.exit_price is not None:
        trade.exit_price = update.exit_price
    if update.pnl is not None:
        trade.pnl = update.pnl

    db.commit()
    db.refresh(trade)
    return trade

@analytics_router.get("/analytics/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(
    strategy_id: Optional[int] = Query(None),
    ticker: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_overview_analytics(db, user, strategy_id, ticker, start_date, end_date)

@analytics_router.get("/analytics/strategies-pnl", response_model=List[StrategyPnlItem])
def get_strategies_pnl_route(
    strategy_id: Optional[int] = Query(None),
    ticker: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_strategies_pnl(db, user, strategy_id, ticker, start_date, end_date)

@analytics_router.get("/analytics/top-tickers", response_model=List[TopTickerItem])
def get_top_tickers_route(
    limit: int = 5,
    strategy_id: Optional[int] = Query(None),
    ticker: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_top_tickers(db, user, limit, strategy_id, ticker, start_date, end_date)

@analytics_router.get("/analytics/equity-curve", response_model=List[DailyPnlItem])
def get_equity_curve_route(
    strategy_id: Optional[int] = Query(None),
    ticker: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_equity_curve(db, user, strategy_id, ticker, start_date, end_date)