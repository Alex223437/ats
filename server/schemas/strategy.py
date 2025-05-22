from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class Signal(BaseModel):
    indicator: str
    value: float
    operator: Optional[Literal["<", "<=", "==", ">=", ">"]] = ">"  # по умолчанию >

class TickerWithSignal(BaseModel):
    ticker: str
    last_signal: Optional[str] = None
    last_price: Optional[float] = None
    updated_at: Optional[datetime] = None

class StrategyCreate(BaseModel):
    title: str
    buy_signals: List[Signal]
    sell_signals: List[Signal]
    market_check_frequency: str
    automation_mode: str = "Semi-Automatic"

    # Новые поля:
    signal_logic: Literal["AND", "OR"] = "AND"
    confirmation_candles: int = 1
    notify_on_signal: bool = True
    auto_trade: bool = False
    order_type: Literal["market", "limit", "stop", "trailing_stop"] = "market"
    trade_amount: int = 100  

class StrategyResponse(StrategyCreate):
    id: int
    is_enabled: bool
    tickers: List[str] = []
    last_checked: Optional[datetime] = None
    class Config:
        from_attributes = True

class StrategyTickerLink(BaseModel):
    tickers: List[str]

