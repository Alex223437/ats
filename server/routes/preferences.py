from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from routes.auth import get_current_user
from models import UserPreferences, User
from schemas.preferences import TradingPreferencesResponse, TradingPreferencesUpdate

preferences_router = APIRouter(prefix="/settings/trading", tags=["Settings"])

@preferences_router.get("", response_model=TradingPreferencesResponse)
def get_trading_preferences(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prefs = db.query(UserPreferences).filter_by(user_id=user.id).first()

    if not prefs:
        prefs = UserPreferences(user_id=user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)

    return prefs


@preferences_router.post("", response_model=TradingPreferencesResponse)
def update_trading_preferences(
    update: TradingPreferencesUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prefs = db.query(UserPreferences).filter_by(user_id=user.id).first()

    if not prefs:
        prefs = UserPreferences(user_id=user.id)
        db.add(prefs)

    for field, value in update.dict(exclude_unset=True).items():
        setattr(prefs, field, value)

    db.commit()
    db.refresh(prefs)
    return prefs