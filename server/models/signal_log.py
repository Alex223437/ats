from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class SignalLog(Base):
    __tablename__ = "signal_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)

    ticker = Column(String, nullable=False)
    action = Column(String, nullable=False)  # buy / sell / hold
    price = Column(Float, nullable=False)
    debug_data = Column(JSON, nullable=True)
    executed = Column(Boolean, default=False)  # был ли исполнен этот сигнал (перешёл в трейд)
    result = Column(String, nullable=True)     # например: "matched", "ignored", "failed"

    created_at = Column(DateTime, default=datetime.utcnow)

    strategy = relationship("Strategy", back_populates="signals")
    user = relationship("User", back_populates="signals")