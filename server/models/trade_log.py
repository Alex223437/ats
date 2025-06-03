from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, func
from database import Base

class TradeLog(Base):
    __tablename__ = "trade_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String, nullable=False)
    action = Column(String, nullable=False) 
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    exit_price = Column(Float, nullable=True)
    exit_time = Column(DateTime, nullable=True)
    pnl = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

    status = Column(String, default="pending") 
    is_order = Column(Boolean, default=True)
    broker_order_id = Column(String, nullable=True)