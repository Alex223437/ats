from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base 

class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)

    ticker = Column(String, nullable=False)
    parameters = Column(JSON, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    metrics = Column(JSON, nullable=False)  # {'total_pnl': ..., 'sharpe_ratio': ..., 'win_rate': ..., 'average_pnl': ..., 'max_drawdown': ...}
    equity_curve = Column(JSON, nullable=True)  # [{'date': ..., 'pnl': ...}, ...]
    trades = Column(JSON, nullable=True)  # [{'action': ..., 'price': ..., 'result': ..., 'pnl': ..., 'time': ...}, ...]

    created_at = Column(DateTime, default=datetime.utcnow)

    strategy = relationship("Strategy", back_populates="backtest_results")