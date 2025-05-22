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
    try:
        api = get_alpaca_api(user)
        account = api.get_account()

        # Optional: получаем историю торгов для расчета total_pnl
        try:
            activities = api.get_activities(activity_types="FILL")
            pnl_total = 0
            for act in activities:
                price = float(act.price)
                qty = int(act.qty)
                if act.side == 'sell':
                    pnl_total += price * qty
                elif act.side == 'buy':
                    pnl_total -= price * qty
        except Exception:
            pnl_total = None  # на случай, если API не даёт данные

        today_pnl = None
        try:
            equity = float(account.equity)
            last_equity = float(account.last_equity)
            today_pnl = round(equity - last_equity, 2)
        except Exception:
            pass

        return {
            "connected": True,
            "data": {
                "account_status": account.status,
                "cash": float(account.cash),
                "portfolio_value": float(account.portfolio_value),
                "buying_power": float(account.buying_power),
                "today_pnl": today_pnl,
                "total_pnl": round(pnl_total, 2) if pnl_total is not None else None
            }
        }

    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }
    
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