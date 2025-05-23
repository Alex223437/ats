from pydantic import BaseModel
from typing import Optional


class TradingPreferencesResponse(BaseModel):
    default_timeframe: str
    auto_trading_enabled: bool
    default_trade_amount: float
    use_percentage: bool
    default_stop_loss: Optional[float] = None
    default_take_profit: Optional[float] = None

    class Config:
        from_attributes = True


class TradingPreferencesUpdate(BaseModel):
    default_timeframe: Optional[str] = None
    auto_trading_enabled: Optional[bool] = None
    default_trade_amount: Optional[float] = None
    use_percentage: Optional[bool] = None
    default_stop_loss: Optional[float] = None
    default_take_profit: Optional[float] = None