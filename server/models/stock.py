from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class UserStock(Base):
    __tablename__ = "user_stocks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    ticker = Column(String, nullable=False)

    user = relationship("User", back_populates="stocks")