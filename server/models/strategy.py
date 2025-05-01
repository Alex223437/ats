from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from server.database import Base

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Связь с пользователем
    title = Column(String, nullable=False)
    buy_signals = Column(JSON, nullable=False, default={})
    sell_signals = Column(JSON, nullable=False, default={})
    market_check_frequency = Column(String, nullable=False, default="1 Hour")
    automation_mode = Column(String, nullable=False, default="Semi-Automatic")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_enabled = Column(Boolean, default=False)
    user = relationship("User", back_populates="strategies")  # Связь с моделью User
    