from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.strategy import Strategy
from models.user import User
from routes.auth import get_current_user  # Для получения текущего пользователя
from schemas.strategy import StrategyCreate, StrategyResponse

strategy_router = APIRouter()

@strategy_router.get("/strategies", response_model=list[StrategyResponse])
def get_strategies(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Strategy).filter(Strategy.user_id == user.id).all()

@strategy_router.post("/strategies", response_model=StrategyResponse)
def create_strategy(strategy: StrategyCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_strategy = Strategy(**strategy.dict(), user_id=user.id)
    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)
    return new_strategy

@strategy_router.put("/strategies/{strategy_id}", response_model=StrategyResponse)
def update_strategy(strategy_id: int, strategy: StrategyCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_strategy = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.user_id == user.id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    for key, value in strategy.dict().items():
        setattr(db_strategy, key, value)

    db.commit()
    db.refresh(db_strategy)
    return db_strategy

@strategy_router.delete("/strategies/{strategy_id}")
def delete_strategy(strategy_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_strategy = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.user_id == user.id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    db.delete(db_strategy)
    db.commit()
    return {"message": "Strategy deleted"}

@strategy_router.get("/strategies/active")
def get_active_strategies(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    strategies = db.query(Strategy).filter_by(user_id=user.id, is_enabled=True).all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "automation_mode": s.automation_mode,
            "market_check_frequency": s.market_check_frequency,
            "tickers": [stock.ticker for stock in s.user.stocks],
        }
        for s in strategies
    ]

@strategy_router.put("/strategies/{strategy_id}/disable")
def disable_strategy(strategy_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    strategy = db.query(Strategy).filter_by(id=strategy_id, user_id=user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    strategy.is_enabled = False
    db.commit()
    return {"success": True, "message": "Strategy disabled"}
