from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from pydantic import model_validator

class Signal(BaseModel):
    indicator: str
    value: float
    operator: Optional[Literal["<", "<=", "==", ">=", ">"]] = ">"  # по умолчанию >

class StrategyBase(BaseModel):
    title: str
    buy_signals: List[Signal]
    sell_signals: List[Signal]
    market_check_frequency: str
    automation_mode: Literal["Manual", "NotifyOnly", "SemiAuto", "FullAuto"]
    signal_logic: Literal["AND", "OR"]
    confirmation_candles: int
    order_type: Literal["market", "limit", "trailing_stop", "bracket"]
    use_notional: bool
    trade_amount: float
    use_balance_percent: bool
    stop_loss: Optional[float]
    take_profit: Optional[float]
    sl_tp_is_percent: bool
    default_timeframe: Literal["1Min", "5Min", "1H", "1D"]

class TickerWithSignal(BaseModel):
    ticker: str
    last_signal: Optional[str] = None
    last_price: Optional[float] = None
    updated_at: Optional[datetime] = None

class StrategyCreate(StrategyBase):
    @model_validator(mode="after")
    def validate_combinations(self):
        # 🔒 Notional работает только с market
        if self.use_notional and self.order_type != "market":
            raise ValueError("Notional is only allowed with market orders.")

        # ⚠️ SL/TP можно только при qty (не notional и не % баланса)
        uses_qty = not self.use_notional and not self.use_balance_percent
        has_sl_tp = (self.stop_loss is not None and self.stop_loss != 0) or (self.take_profit is not None and self.take_profit != 0)

        if has_sl_tp and not uses_qty:
            raise ValueError("Stop Loss / Take Profit requires a fixed quantity (disable notional and % balance).")

        return self

class StrategyResponse(StrategyBase):
    id: int
    is_enabled: bool
    tickers: List[str] = []
    last_checked: Optional[datetime] = None

    class Config:
        from_attributes = True

class StrategyTickerLink(BaseModel):
    tickers: List[str]

