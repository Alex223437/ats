from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class UserBroker(Base):
    __tablename__ = "user_brokers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    broker = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    api_secret = Column(String, nullable=False)
    base_url = Column(String, nullable=True)
    is_connected = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="brokers")