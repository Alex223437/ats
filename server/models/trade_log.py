from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from database import Base

class TradeLog(Base):
    __tablename__ = "trade_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String, nullable=False)
    action = Column(String, nullable=False)  # "buy" / "sell"
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)