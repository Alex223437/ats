import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from database import get_db
from datetime import datetime
from models.strategy import Strategy
from models.strategy_ticker import StrategyTicker
from models.user import User
from models.stock import UserStock
from models.signal_log import SignalLog
from routes.auth import get_current_user
from schemas.strategy import StrategyCreate, StrategyResponse, StrategyTickerLink, CustomStrategyResponse, TensorFlowStrategyResponse
from services.tensorflow_trainer import train_model_for_strategy

strategy_router = APIRouter()


from typing import Union

def serialize_strategy(s: Strategy) -> Union[CustomStrategyResponse, TensorFlowStrategyResponse]:
    if s.strategy_type == "ml_tf":
        return TensorFlowStrategyResponse(
            id=s.id,
            title=s.title,
            strategy_type=s.strategy_type,
            training_ticker=s.training_ticker or "",
            training_from_date=str(s.training_from_date) if s.training_from_date else "",
            training_to_date=str(s.training_to_date) if s.training_to_date else "",
            last_trained_at=s.last_trained_at,
            is_enabled=s.is_enabled,
            last_checked=s.last_checked,
            tickers=[link.user_stock.ticker for link in s.tickers if link.user_stock],
        )
    return CustomStrategyResponse(
        id=s.id,
        title=s.title,
        strategy_type=s.strategy_type,
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
        training_ticker=s.training_ticker or "",
        training_from_date=str(s.training_from_date) if s.training_from_date else "",
        training_to_date=str(s.training_to_date) if s.training_to_date else "",
        is_enabled=s.is_enabled,
        last_checked=s.last_checked,
        tickers=[link.user_stock.ticker for link in s.tickers if link.user_stock],
    )


@strategy_router.get("/strategies", response_model=list[StrategyResponse])
def get_strategies(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    strategies = (
        db.query(Strategy)
        .filter(Strategy.user_id == user.id)
        .options(joinedload(Strategy.tickers).joinedload(StrategyTicker.user_stock))
        .all()
    )
    return [serialize_strategy(s) for s in strategies]


@strategy_router.post("/strategies", response_model=StrategyResponse)
def create_strategy(strategy: StrategyCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_strategy = Strategy(**strategy.model_dump(), user_id=user.id)
    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)
    return serialize_strategy(new_strategy)


@strategy_router.put("/strategies/{strategy_id}", response_model=StrategyResponse)
def update_strategy(strategy_id: int, strategy: StrategyCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_strategy = db.query(Strategy).filter_by(id=strategy_id, user_id=user.id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    for key, value in strategy.model_dump().items():
        setattr(db_strategy, key, value)

    db.commit()
    db.refresh(db_strategy)
    return serialize_strategy(db_strategy)


@strategy_router.delete("/strategies/{strategy_id}")
def delete_strategy(strategy_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter_by(id=strategy_id, user_id=user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    db.delete(strategy)
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
    return [serialize_strategy(s) for s in strategies]


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
        db.add(StrategyTicker(strategy_id=strategy.id, user_stock_id=ticker_map[ticker]))

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

@strategy_router.post("/strategies/{strategy_id}/train")
def train_strategy_model(strategy_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter_by(id=strategy_id, user_id=user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    try:
        train_model_for_strategy(strategy, user.id)
        strategy.last_trained_at = datetime.utcnow()
        db.commit()
        return {"message": "Training completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")
    
@strategy_router.delete("/strategies/{strategy_id}/model")
def delete_trained_model(strategy_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter_by(id=strategy_id, user_id=user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    model_dir = f"ai_model/models/tf_models"
    paths = [
        os.path.join(model_dir, f"{user.id}_{strategy.training_ticker}.keras"),
        os.path.join(model_dir, f"{user.id}_{strategy.training_ticker}_scaler.pkl"),
        os.path.join(model_dir, f"{user.id}_{strategy.training_ticker}_encoder.pkl"),
    ]

    deleted = []
    for path in paths:
        if os.path.exists(path):
            os.remove(path)
            deleted.append(path)

    strategy.last_trained_at = None
    db.commit()

    return {"message": f"Deleted {len(deleted)} model files"}