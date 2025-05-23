from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    default_timeframe = Column(String, default="1Min")  # 1Min | 5Min | 1H | 1D
    auto_trading_enabled = Column(Boolean, default=False)
    default_trade_amount = Column(Float, default=100.0)  # в $
    use_percentage = Column(Boolean, default=False)  # если true — % от баланса

    default_stop_loss = Column(Float, nullable=True)  # в %
    default_take_profit = Column(Float, nullable=True)

    user = relationship("User", back_populates="preferences")