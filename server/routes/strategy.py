from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
from sqlalchemy import desc
from models.strategy import Strategy
from models.strategy_ticker import StrategyTicker
from models.user import User
from models.stock import UserStock
from models.signal_log import SignalLog
from routes.auth import get_current_user
from schemas.strategy import StrategyCreate, StrategyResponse, StrategyTickerLink

strategy_router = APIRouter()

@strategy_router.get("/strategies", response_model=list[StrategyResponse])
def get_strategies(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    strategies = (
        db.query(Strategy)
        .filter(Strategy.user_id == user.id)
        .options(joinedload(Strategy.tickers).joinedload(StrategyTicker.user_stock))
        .all()
    )

    return [
        StrategyResponse(
            id=s.id,
            title=s.title,
            buy_signals=s.buy_signals,
            sell_signals=s.sell_signals,
            market_check_frequency=s.market_check_frequency,
            automation_mode=s.automation_mode,
            signal_logic=s.signal_logic,
            confirmation_candles=s.confirmation_candles,
            order_type=s.order_type,
            use_notional=s.use_notional,
            trade_amount=s.trade_amount,
            use_balance_percent=s.use_balance_percent,
            stop_loss=s.stop_loss,
            take_profit=s.take_profit,
            sl_tp_is_percent=s.sl_tp_is_percent,
            default_timeframe=s.default_timeframe,
            is_enabled=s.is_enabled,
            last_checked=s.last_checked,
            tickers=[link.user_stock.ticker for link in s.tickers if link.user_stock]
        )
        for s in strategies
    ]

@strategy_router.post("/strategies", response_model=StrategyResponse)
def create_strategy(strategy: StrategyCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_strategy = Strategy(**strategy.dict(), user_id=user.id)
    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)

    return StrategyResponse(
        id=new_strategy.id,
        title=new_strategy.title,
        buy_signals=new_strategy.buy_signals,
        sell_signals=new_strategy.sell_signals,
        market_check_frequency=new_strategy.market_check_frequency,
        automation_mode=new_strategy.automation_mode,
        signal_logic=new_strategy.signal_logic,
        confirmation_candles=new_strategy.confirmation_candles,
        order_type=new_strategy.order_type,
        use_notional=new_strategy.use_notional,
        trade_amount=new_strategy.trade_amount,
        use_balance_percent=new_strategy.use_balance_percent,
        stop_loss=new_strategy.stop_loss,
        take_profit=new_strategy.take_profit,
        sl_tp_is_percent=new_strategy.sl_tp_is_percent,
        default_timeframe=new_strategy.default_timeframe,
        is_enabled=new_strategy.is_enabled,
        last_checked=new_strategy.last_checked,
        tickers=[]
    )

@strategy_router.put("/strategies/{strategy_id}", response_model=StrategyResponse)
def update_strategy(strategy_id: int, strategy: StrategyCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_strategy = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.user_id == user.id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    for key, value in strategy.dict().items():
        setattr(db_strategy, key, value)

    db.commit()
    db.refresh(db_strategy)

    tickers = [link.user_stock.ticker for link in db_strategy.tickers if link.user_stock]

    return StrategyResponse(
        id=db_strategy.id,
        title=db_strategy.title,
        buy_signals=db_strategy.buy_signals,
        sell_signals=db_strategy.sell_signals,
        market_check_frequency=db_strategy.market_check_frequency,
        automation_mode=db_strategy.automation_mode,
        signal_logic=db_strategy.signal_logic,
        confirmation_candles=db_strategy.confirmation_candles,
        order_type=db_strategy.order_type,
        use_notional=db_strategy.use_notional,
        trade_amount=db_strategy.trade_amount,
        use_balance_percent=db_strategy.use_balance_percent,
        stop_loss=db_strategy.stop_loss,
        take_profit=db_strategy.take_profit,
        sl_tp_is_percent=db_strategy.sl_tp_is_percent,
        default_timeframe=db_strategy.default_timeframe,
        is_enabled=db_strategy.is_enabled,
        last_checked=db_strategy.last_checked,
        tickers=tickers
    )

@strategy_router.delete("/strategies/{strategy_id}")
def delete_strategy(strategy_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_strategy = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.user_id == user.id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    db.delete(db_strategy)
    db.commit()
    return {"message": "Strategy deleted"}

@strategy_router.get("/strategies/active", response_model=list[StrategyResponse])
def get_active_strategies(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    strategies = (
        db.query(Strategy)
        .filter_by(user_id=user.id, is_enabled=True)
        .options(joinedload(Strategy.tickers).joinedload(StrategyTicker.user_stock))
        .all()
    )

    return [
        StrategyResponse(
            id=s.id,
            title=s.title,
            buy_signals=s.buy_signals,
            sell_signals=s.sell_signals,
            market_check_frequency=s.market_check_frequency,
            automation_mode=s.automation_mode,
            signal_logic=s.signal_logic,
            confirmation_candles=s.confirmation_candles,
            order_type=s.order_type,
            use_notional=s.use_notional,
            trade_amount=s.trade_amount,
            use_balance_percent=s.use_balance_percent,
            stop_loss=s.stop_loss,
            take_profit=s.take_profit,
            sl_tp_is_percent=s.sl_tp_is_percent,
            default_timeframe=s.default_timeframe,
            is_enabled=s.is_enabled,
            last_checked=s.last_checked,
            tickers=[link.user_stock.ticker for link in s.tickers if link.user_stock]
        )
        for s in strategies
    ]

@strategy_router.put("/strategies/{strategy_id}/enable")
def enable_strategy(strategy_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter_by(id=strategy_id, user_id=user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    strategy.is_enabled = True
    db.commit()
    return {"success": True, "message": "Strategy enabled"}

@strategy_router.put("/strategies/{strategy_id}/disable")
def disable_strategy(strategy_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter_by(id=strategy_id, user_id=user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    strategy.is_enabled = False
    db.commit()
    return {"success": True, "message": "Strategy disabled"}

@strategy_router.get("/strategies/{strategy_id}/tickers")
def get_strategy_tickers(strategy_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    strategy = (
        db.query(Strategy)
        .filter(Strategy.id == strategy_id, Strategy.user_id == user.id)
        .options(joinedload(Strategy.tickers).joinedload(StrategyTicker.user_stock))
        .first()
    )
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    return [link.user_stock.ticker for link in strategy.tickers if link.user_stock]

@strategy_router.post("/strategies/{strategy_id}/tickers")
def assign_tickers_to_strategy(strategy_id: int, payload: StrategyTickerLink, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter_by(id=strategy_id, user_id=user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    user_stocks = db.query(UserStock).filter_by(user_id=user.id).all()
    ticker_map = {stock.ticker: stock.id for stock in user_stocks}

    invalid = [t for t in payload.tickers if t not in ticker_map]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Invalid tickers: {', '.join(invalid)}")

    db.query(StrategyTicker).filter_by(strategy_id=strategy.id).delete()

    for ticker in payload.tickers:
        link = StrategyTicker(strategy_id=strategy.id, user_stock_id=ticker_map[ticker])
        db.add(link)

    db.commit()
    return {"message": f"{len(payload.tickers)} tickers linked to strategy"}

@strategy_router.get("/strategies/{strategy_id}/logs")
def get_strategy_logs(strategy_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db), limit: int = 20):
    strategy = db.query(Strategy).filter_by(id=strategy_id, user_id=user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    logs = (
        db.query(SignalLog)
        .filter(SignalLog.strategy_id == strategy_id, SignalLog.user_id == user.id)
        .order_by(desc(SignalLog.created_at))
        .limit(limit)
        .all()
    )

    return [
        {
            "id": log.id,
            "ticker": log.ticker,
            "action": log.action,
            "price": log.price,
            "executed": log.executed,
            "result": log.result,
            "created_at": log.created_at,
            "debug_data": log.debug_data,
        }
        for log in logs
    ]