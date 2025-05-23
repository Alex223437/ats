from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserPreferences
from routes.auth import get_current_user
from schemas.preferences import NotificationSettings

settings_router = APIRouter(prefix="/settings", tags=["Settings"])

@settings_router.get("/notifications", response_model=NotificationSettings)
def get_notification_settings(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    prefs = db.query(UserPreferences).filter_by(user_id=user.id).first()
    if not prefs:
        raise HTTPException(status_code=404, detail="User preferences not found")
    return NotificationSettings(**prefs.__dict__)


@settings_router.post("/notifications")
def update_notification_settings(
    settings: NotificationSettings,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    prefs = db.query(UserPreferences).filter_by(user_id=user.id).first()
    if not prefs:
        raise HTTPException(status_code=404, detail="User preferences not found")

    prefs.email_alerts_enabled = settings.email_alerts_enabled
    prefs.notify_on_signal = settings.notify_on_signal
    prefs.notify_on_order_filled = settings.notify_on_order_filled
    prefs.notify_on_error = settings.notify_on_error

    db.commit()
    db.refresh(prefs)

    return {"success": True, "message": "Notification settings updated"}