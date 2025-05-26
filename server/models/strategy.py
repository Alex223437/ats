from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from database import Base

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)

    strategy_type = Column(String, default="custom")  # custom | ml_rf | ml_tf

    buy_signals = Column(JSON, nullable=False, default={})
    sell_signals = Column(JSON, nullable=False, default={})
    signal_logic = Column(String, default="AND")
    confirmation_candles = Column(Integer, default=1)

    order_type = Column(String, default="market")              # market / limit / stop ...
    use_notional = Column(Boolean, default=False)              # true → $ (notional), false → qty
    trade_amount = Column(Float, default=1.0)                  # количество или сумма

    use_balance_percent = Column(Boolean, default=False)       # использовать % от кэша

    stop_loss = Column(Float, nullable=True)                   # если None — не использовать
    take_profit = Column(Float, nullable=True)
    sl_tp_is_percent = Column(Boolean, default=True)

    default_timeframe = Column(String, default="1H")           # 1Min / 5Min / 1H / 1D
    market_check_frequency = Column(String, default="1 Hour")  # UI frequency
    automation_mode = Column(String, default="SemiAuto")       # Manual / NotifyOnly / SemiAuto / FullAuto

    is_enabled = Column(Boolean, default=False)
    last_checked = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="strategies")
    signals = relationship("SignalLog", back_populates="strategy", cascade="all, delete-orphan")
    tickers = relationship("StrategyTicker", cascade="all, delete-orphan")