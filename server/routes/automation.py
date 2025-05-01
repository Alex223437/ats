from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.database import get_db
from server.models.strategy import Strategy
from server.services.automation_service import run_strategy

automation_router = APIRouter()

@automation_router.post("/run-automation")
def run_automation_all_strategies(db: Session = Depends(get_db)):
    strategies = db.query(Strategy).filter(Strategy.is_enabled == True).all()
    for strategy in strategies:
        run_strategy(strategy, db)
    return {"message": "✅ Автоматизация выполнена"}