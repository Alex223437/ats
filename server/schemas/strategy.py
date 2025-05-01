from pydantic import BaseModel
from typing import List

class Signal(BaseModel):
    indicator: str
    value: float  # 🔥 Теперь FastAPI будет требовать float, а не строку

class StrategyCreate(BaseModel):
    title: str
    buy_signals: List[Signal]  # 🔥 Заменили dict на List[Signal]
    sell_signals: List[Signal]
    market_check_frequency: str
    automation_mode: str

class StrategyResponse(StrategyCreate):
    id: int

    class Config:
        from_attributes = True