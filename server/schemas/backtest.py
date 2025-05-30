from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime

class BacktestRequest(BaseModel):
    strategy_id: int
    ticker: str
    parameters: Optional[Dict] = {}
    start_date: datetime
    end_date: datetime

class BacktestMetrics(BaseModel):
    total_pnl: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: Optional[float] = None
    average_pnl: Optional[float] = None

class EquityPoint(BaseModel):
    date: datetime
    pnl: float

class BacktestTrade(BaseModel):
    action: str
    price: float
    result: str
    pnl: float
    time: datetime

class BacktestResponse(BaseModel):
    id: Optional[int] = None 
    metrics: BacktestMetrics
    equity_curve: List[EquityPoint]
    trades: List[BacktestTrade]