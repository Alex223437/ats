from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from models.signal_log import SignalLog
from models.strategy import Strategy
from datetime import datetime, timedelta
from models.user import User
from routes.auth import get_current_user


signals_router = APIRouter(
    prefix="/signals",
    tags=["Signals"]
)

@signals_router.get("/recent")
def get_recent_signals(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    since = datetime.utcnow() - timedelta(hours=24)
    signals = (
        db.query(SignalLog)
        .join(Strategy)
        .filter(
            SignalLog.user_id == user.id,
            SignalLog.created_at >= since
        )
        .order_by(SignalLog.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "ticker": s.ticker,
            "action": s.action,
            "strategy_title": s.strategy.title if s.strategy else "Unknown",
            "created_at": s.created_at
        }
        for s in signals
    ]

@signals_router.get("/last")
def get_latest_signal(
    strategy_id: int,
    ticker: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    signal = (
        db.query(SignalLog)
        .filter(
            SignalLog.user_id == user.id,
            SignalLog.strategy_id == strategy_id,
            func.lower(SignalLog.ticker) == ticker.lower()
        )
        .order_by(SignalLog.created_at.desc())
        .first()
    )

    return {
        "action": signal.action.upper() if signal else None
    }