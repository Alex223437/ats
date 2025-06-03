from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, JSON, Boolean, Float, Date
from sqlalchemy.orm import relationship
from database import Base

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)

    strategy_type = Column(String, default="custom")

    buy_signals = Column(JSON, nullable=False, default={})
    sell_signals = Column(JSON, nullable=False, default={})
    signal_logic = Column(String, default="AND")
    confirmation_candles = Column(Integer, default=1)

    order_type = Column(String, default="market")
    use_notional = Column(Boolean, default=False)
    trade_amount = Column(Float, default=1.0)

    use_balance_percent = Column(Boolean, default=False)

    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    sl_tp_is_percent = Column(Boolean, default=True)

    default_timeframe = Column(String, default="1H")
    market_check_frequency = Column(String, default="1 Hour")
    automation_mode = Column(String, default="SemiAuto")

    is_enabled = Column(Boolean, default=False)
    last_checked = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    training_ticker = Column(String, nullable=True)
    training_from_date = Column(Date, nullable=True)
    training_to_date = Column(Date, nullable=True)
    last_trained_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="strategies")
    signals = relationship("SignalLog", back_populates="strategy", cascade="all, delete-orphan")
    tickers = relationship("StrategyTicker", cascade="all, delete-orphan")