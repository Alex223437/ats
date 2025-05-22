from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SignalLogResponse(BaseModel):
    id: int
    strategy_id: int
    ticker: str
    action: str                # раньше было signal — заменяем на action (buy/sell/hold)
    price: float
    created_at: datetime
    executed: bool             # был ли исполнен (перешёл в сделку)
    result: Optional[str] = None  # matched / ignored / failed / null
    debug_data: Optional[dict] = None

    class Config:
        orm_mode = True

class SignalLogUpdate(BaseModel):
    executed: Optional[bool] = None