from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user import (
    UserSettingsUpdate,
    UserSettingsResponse,
    UserBrokerSettingsUpdate,
)
from database import get_db
from models.user import User
from routes.auth import get_current_user
from services.security import get_password_hash
from services.broker_factory import get_alpaca_api 

user_router = APIRouter()


@user_router.get("/user/settings", response_model=UserSettingsResponse)
async def get_user_settings(user: User = Depends(get_current_user)):
    """Получение всех настроек пользователя"""
    return {
        "username": user.username,
        "email": user.email,
        "alpaca_api_key": user.alpaca_api_key,
        "alpaca_api_secret": user.alpaca_api_secret,
        "alpaca_base_url": user.alpaca_base_url,
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


@user_router.put("/user/settings/broker")
async def update_user_broker_settings(
    broker_settings: UserBrokerSettingsUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление брокерских ключей"""
    if broker_settings.broker == "alpaca":
        user.alpaca_api_key = broker_settings.api_key
        user.alpaca_api_secret = broker_settings.api_secret
        user.alpaca_base_url = broker_settings.base_url

    db.commit()
    db.refresh(user)
    return {"success": True, "message": "API ключи обновлены"}

@user_router.get("/user/broker/check")
async def check_broker_connection(user: User = Depends(get_current_user)):
    """Проверяет подключение к Alpaca API"""
    try:
        api = get_alpaca_api(user)
        account = api.get_account()
        return {
            "connected": True,
            "data": {
                "account_status": account.status,
                "cash": account.cash
            }
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}
    
@user_router.delete("/user/broker")
async def disconnect_broker(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user.alpaca_api_key = None
    user.alpaca_api_secret = None
    user.alpaca_base_url = None
    db.commit()
    return {"success": True, "message": "Broker disconnected"}