from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.user import (
    UserSettingsUpdate,
    UserSettingsResponse,
)
from database import get_db
from models.user import User
from routes.auth import get_current_user
from services.security import get_password_hash

user_router = APIRouter()


@user_router.get("/user/settings", response_model=UserSettingsResponse)
async def get_user_settings(user: User = Depends(get_current_user)):
    """Получение всех настроек пользователя"""
    return {
        "username": user.username,
        "email": user.email,
    }


@user_router.put("/user/settings/profile")
async def update_user_profile(
    settings: UserSettingsUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление username / email / password"""
    if settings.username:
        user.username = settings.username
    if settings.email:
        user.email = settings.email
    if settings.password:
        user.password = get_password_hash(settings.password)

    db.commit()
    db.refresh(user)
    return {"success": True, "message": "Профиль обновлён"}