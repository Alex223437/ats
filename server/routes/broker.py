from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserBroker
from schemas.broker import UserBrokerSettingsUpdate, BrokerConnectionResponse
from routes.auth import get_current_user
from services.broker_factory import get_api_client

broker_router = APIRouter(prefix="/user/brokers", tags=["Brokers"])


@broker_router.post("", response_model=BrokerConnectionResponse)
def connect_broker(
    data: UserBrokerSettingsUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    existing = (
        db.query(UserBroker)
        .filter_by(user_id=user.id, broker=data.broker.lower())
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Broker already connected")

    new_broker = UserBroker(
        user_id=user.id,
        broker=data.broker.lower(),
        api_key=data.api_key,
        api_secret=data.api_secret,
        base_url=data.base_url,
        is_connected=True,
    )
    db.add(new_broker)
    db.commit()
    db.refresh(new_broker)
    return BrokerConnectionResponse.from_orm(new_broker)


@broker_router.get("", response_model=list[BrokerConnectionResponse])
def get_connected_brokers(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(UserBroker).filter_by(user_id=user.id).all()


@broker_router.delete("/{broker_name}")
def disconnect_broker(
    broker_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    broker = (
        db.query(UserBroker)
        .filter_by(user_id=user.id, broker=broker_name.lower())
        .first()
    )
    if not broker:
        raise HTTPException(status_code=404, detail="Broker not found")

    db.delete(broker)
    db.commit()
    return {"success": True, "message": f"{broker_name} disconnected"}


@broker_router.get("/{broker_name}/check")
def check_broker_connection(
    broker_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    broker = (
        db.query(UserBroker)
        .filter_by(user_id=user.id, broker=broker_name.lower())
        .first()
    )
    if not broker:
        raise HTTPException(status_code=404, detail="Broker not found")

    try:
        client = get_api_client(broker)
        account = client.get_account()

        try:
            equity = float(getattr(account, "equity", 0))
            last_equity = float(getattr(account, "last_equity", 0))
            today_pnl = round(equity - last_equity, 2)
        except Exception:
            today_pnl = None

        pnl_total = None
        try:
            activities = client.get_activities(activity_types="FILL")
            pnl_total = sum(
                float(act.price) * int(act.qty) * (1 if act.side == 'sell' else -1)
                for act in activities
            )
        except Exception:
            pass

        return {
            "connected": True,
            "account_status": account.status,
            "cash": float(account.cash),
            "buying_power": float(account.buying_power),
            "portfolio_value": float(account.portfolio_value),
            "today_pnl": today_pnl,
            "total_pnl": round(pnl_total, 2) if pnl_total is not None else None,
        }

    except Exception as e:
        return {"connected": False, "error": str(e)}