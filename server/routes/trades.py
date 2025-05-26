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
from pydantic import BaseModel, model_validator
from typing import Optional

trades_router = APIRouter()

class OrderSchema(BaseModel):
    symbol: str
    side: str
    order_type: str
    time_in_force: str

    qty: Optional[float] = None
    notional: Optional[float] = None

    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    trail_price: Optional[float] = None
    trail_percent: Optional[float] = None

    @model_validator(mode="after")
    def validate_qty_or_notional(self):
        if not self.qty and not self.notional:
            raise ValueError("Either 'qty' or 'notional' must be provided")

        if self.qty and self.notional:
            raise ValueError("You cannot provide both 'qty' and 'notional'")

        if self.notional:
            if self.order_type != "market" or self.time_in_force != "day":
                raise ValueError("Notional orders are only allowed with 'market' order type and 'day' time in force")

        return self

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