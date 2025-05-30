from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SignalLogResponse(BaseModel):
    id: int
    strategy_id: int
    ticker: str
    action: str               
    price: float
    created_at: datetime
    executed: bool            
    result: Optional[str] = None 
    debug_data: Optional[dict] = None

    class Config:
        orm_mode = True

class SignalLogUpdate(BaseModel):
    executed: Optional[bool] = None