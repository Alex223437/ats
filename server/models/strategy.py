from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)

    # Условия сигнала
    buy_signals = Column(JSON, nullable=False, default={})     
    sell_signals = Column(JSON, nullable=False, default={})
    signal_logic = Column(String, default="AND")               
    confirmation_candles = Column(Integer, default=1)           

    # Поведение при срабатывании
    notify_on_signal = Column(Boolean, default=True)
    auto_trade = Column(Boolean, default=False)
    order_type = Column(String, default="market")
    trade_amount = Column(Integer, default=1)                 

    # Управление
    market_check_frequency = Column(String, nullable=False, default="1 Hour")
    automation_mode = Column(String, nullable=False, default="Semi-Automatic")
    is_enabled = Column(Boolean, default=False)
    last_checked = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Связи
    user = relationship("User", back_populates="strategies")
    signals = relationship("SignalLog", back_populates="strategy", cascade="all, delete-orphan")
    tickers = relationship("StrategyTicker", cascade="all, delete-orphan")