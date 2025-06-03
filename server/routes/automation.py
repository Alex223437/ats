from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.strategy import Strategy
from services.automation_service import run_strategy_for_ticker

automation_router = APIRouter()

@automation_router.post("/run-automation")
def run_automation_all_strategies(db: Session = Depends(get_db)):
    strategies = db.query(Strategy).filter(Strategy.is_enabled.is_(True)).all()

    if not strategies:
        return {"message": "No active strategies found."}

    executed = []

    for strategy in strategies:
        user = strategy.user
        for stock in user.stocks:
            run_strategy_for_ticker(strategy, stock.ticker, user, db)
            executed.append({
                "strategy": strategy.title,
                "ticker": stock.ticker,
                "user": user.email
            })

    return {
        "message": f"Did {len(executed)} control actions",
        "executed": executed
    }