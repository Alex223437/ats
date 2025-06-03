from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    default_timeframe = Column(String, default="1H") 
    auto_trading_enabled = Column(Boolean, default=False)
    default_trade_amount = Column(Float, default=100.0)  
    use_percentage = Column(Boolean, default=False) 

    default_stop_loss = Column(Float, nullable=True)  
    default_take_profit = Column(Float, nullable=True)

    email_alerts_enabled = Column(Boolean, default=True)
    notify_on_signal = Column(Boolean, default=True)
    notify_on_order_filled = Column(Boolean, default=True)
    notify_on_error = Column(Boolean, default=True)

    user = relationship("User", back_populates="preferences")