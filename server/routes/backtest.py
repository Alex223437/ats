from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from routes.auth import get_current_user
from database import get_db
from models import User, BacktestResult
from schemas.backtest import (
    BacktestRequest,
    BacktestResponse,
    BacktestResultInDB,
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

        # преобразование JSON в нужные схемы
        metrics = BacktestMetrics(**result.metrics)
        equity_curve = [EquityPoint(**pt) for pt in result.equity_curve or []]
        trades = [BacktestTrade(**t) for t in result.trades or []]

        return BacktestResponse(
            id=result.id,
            metrics=metrics,
            equity_curve=equity_curve,
            trades=trades
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@backtest_router.get("/results/{id}", response_model=BacktestResultInDB)
def get_backtest_result(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = db.query(BacktestResult).filter_by(id=id, user_id=user.id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Backtest result not found")

    # преобразование
    return BacktestResultInDB(
        id=result.id,
        strategy_id=result.strategy_id,
        ticker=result.ticker,
        start_date=result.start_date,
        end_date=result.end_date,
        parameters=result.parameters,
        created_at=result.created_at,
        metrics=BacktestMetrics(**result.metrics),
        equity_curve=[EquityPoint(**pt) for pt in result.equity_curve or []],
        trades=[BacktestTrade(**t) for t in result.trades or []]
    )