from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from server.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)  
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)  
    stocks = relationship("UserStock", back_populates="user", cascade="all, delete")
    strategies = relationship("Strategy", back_populates="user", cascade="all, delete")
    alpaca_api_key = Column(String, nullable=True)
    alpaca_api_secret = Column(String, nullable=True)
    alpaca_base_url = Column(String, nullable=True)