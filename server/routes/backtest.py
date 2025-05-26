from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from routes.auth import get_current_user
from database import get_db
from models import User
from schemas.backtest import (
    BacktestRequest,
    BacktestResponse,
    BacktestMetrics,
    EquityPoint,
    BacktestTrade
)
from services.backtest_engine import run_backtest

backtest_router = APIRouter(prefix="/backtest", tags=["Backtest"])

@backtest_router.post("/run", response_model=BacktestResponse)
def run_backtest_endpoint(
    request: BacktestRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        result = run_backtest(request, user.id, db)

        metrics = BacktestMetrics(**result["metrics"])
        equity_curve = [EquityPoint(**pt) for pt in result["equity_curve"]]
        trades = [BacktestTrade(**t) for t in result["trades"]]

        return BacktestResponse(
            id=None,
            metrics=metrics,
            equity_curve=equity_curve,
            trades=trades
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

