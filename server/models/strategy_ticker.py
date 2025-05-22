from sqlalchemy import Column, Integer, ForeignKey, Table
from database import Base
from sqlalchemy.orm import relationship

class StrategyTicker(Base):
    __tablename__ = "strategy_tickers"
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="CASCADE"))
    user_stock_id = Column(Integer, ForeignKey("user_stocks.id", ondelete="CASCADE"))
    user_stock = relationship("UserStock", back_populates="strategy_links")