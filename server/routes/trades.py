from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User, UserBroker
from database import get_db
from services.alpaca_service import (
    get_positions,
    get_open_orders,
    place_order,
    cancel_order,
    close_position
)
from pydantic import BaseModel
from routes.auth import get_current_user

trades_router = APIRouter()

class OrderSchema(BaseModel):
    symbol: str
    qty: int
    side: str  # buy / sell
    order_type: str  # market / limit / stop / stop_limit / trailing_stop
    time_in_force: str  # gtc / day
    limit_price: float | None = None
    stop_price: float | None = None
    trail_price: float | None = None
    trail_percent: float | None = None

def get_broker_or_404(user: User, db: Session) -> UserBroker:
    broker = db.query(UserBroker).filter_by(user_id=user.id, broker="alpaca").first()
    if not broker:
        raise HTTPException(status_code=404, detail="Alpaca broker not connected")
    return broker


@trades_router.get("/trades")
async def get_trades(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    broker = get_broker_or_404(user, db)
    return get_positions(broker)


@trades_router.get("/orders")
async def get_orders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    broker = get_broker_or_404(user, db)
    return get_open_orders(broker)


@trades_router.post("/orders")
async def create_order(
    order: OrderSchema,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    broker = get_broker_or_404(user, db)
    return place_order(broker, **order.dict())


@trades_router.delete("/orders/{order_id}")
async def delete_order(
    order_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    broker = get_broker_or_404(user, db)
    return cancel_order(broker, order_id)


@trades_router.delete("/trades/{symbol}")
async def delete_trade(
    symbol: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    broker = get_broker_or_404(user, db)
    return close_position(broker, symbol)