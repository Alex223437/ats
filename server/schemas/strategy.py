from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal, Union, Annotated
from datetime import datetime
from pydantic import model_validator

class Signal(BaseModel):
    indicator: str
    value: float
    operator: Optional[Literal["<", "<=", "==", ">=", ">"]] = ">"  # по умолчанию >

class CustomStrategyBase(BaseModel):
    strategy_type: Literal["custom"] = "custom"
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

class TensorFlowStrategyBase(BaseModel):
    strategy_type: Literal["ml_tf"] = "ml_tf"
    title: str
    training_ticker: str
    training_from_date: str
    training_to_date: str
    trade_amount: float
    use_balance_percent: bool
    use_notional: bool
    automation_mode: Literal["Manual", "NotifyOnly", "SemiAuto", "FullAuto"]

StrategyBase = Annotated[
    Union[CustomStrategyBase, TensorFlowStrategyBase],
    Field(discriminator="strategy_type")
]

class TickerWithSignal(BaseModel):
    ticker: str
    last_signal: Optional[str] = None
    last_price: Optional[float] = None
    updated_at: Optional[datetime] = None

class CustomStrategyCreate(CustomStrategyBase):
    @model_validator(mode="after")
    def validate_combinations(self):
        if self.use_notional and self.order_type != "market":
            raise ValueError("Notional is only allowed with market orders.")

        uses_qty = not self.use_notional and not self.use_balance_percent
        has_sl_tp = (self.stop_loss is not None and self.stop_loss != 0) or (self.take_profit is not None and self.take_profit != 0)

        if has_sl_tp and not uses_qty:
            raise ValueError("Stop Loss / Take Profit requires a fixed quantity (disable notional and % balance).")

        return self

StrategyCreate = Annotated[
    Union[CustomStrategyCreate, TensorFlowStrategyBase],
    Field(discriminator="strategy_type")
]

class CustomStrategyResponse(CustomStrategyBase):
    id: int
    is_enabled: bool
    tickers: List[str] = []
    last_checked: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TensorFlowStrategyResponse(TensorFlowStrategyBase):
    id: int
    is_enabled: bool
    tickers: List[str] = []
    last_checked: Optional[datetime] = None
    last_trained_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

StrategyResponse = Annotated[
    Union[CustomStrategyResponse, TensorFlowStrategyResponse],
    Field(discriminator="strategy_type")
]

class StrategyTickerLink(BaseModel):
    tickers: List[str]