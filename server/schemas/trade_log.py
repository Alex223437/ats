from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TradeLogResponse(BaseModel):
    id: int
    strategy_id: int
    symbol: str
    action: str               # buy/sell
    price: float
    quantity: int
    timestamp: datetime

    # Новые поля:
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: Optional[float] = None

    class Config:
        orm_mode = True

class TradeLogUpdate(BaseModel):
    exit_price: Optional[float] = None
    pnl: Optional[float] = None