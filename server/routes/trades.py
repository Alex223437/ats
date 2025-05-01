from fastapi import APIRouter
from server.services.alpaca_service import get_positions, place_order
from fastapi import Depends
from server.routes.auth import get_current_user
from server.services.alpaca_service import get_open_orders, cancel_order, close_position
from pydantic import BaseModel
from server.models.user import User

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


trades_router = APIRouter()

from server.services.alpaca_service import get_positions, get_open_orders, place_order, cancel_order, close_position

@trades_router.get("/trades")
async def get_trades(user: User = Depends(get_current_user)):
    return get_positions(user)

@trades_router.get("/orders")
async def get_orders(user: User = Depends(get_current_user)):
    return get_open_orders(user)

@trades_router.post("/orders")
async def create_order(order: OrderSchema, user: User = Depends(get_current_user)):
    return place_order(user, **order.dict())

@trades_router.delete("/orders/{order_id}")
async def delete_order(order_id: str, user: User = Depends(get_current_user)):
    return cancel_order(user, order_id)

@trades_router.delete("/trades/{symbol}")
async def delete_trade(symbol: str, user: User = Depends(get_current_user)):
    return close_position(user, symbol)