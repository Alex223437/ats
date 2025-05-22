from datetime import datetime
from pydantic import BaseModel

class AnalyticsOverviewResponse(BaseModel):
    total_trades: int
    total_orders: int
    success_trades: int
    win_rate: float
    total_pnl: float
    average_pnl: float
    max_drawdown: float
    sharpe_ratio: float

class StrategyPnlItem(BaseModel):
    strategy_id: int
    title: str
    pnl: float

class DailyPnlItem(BaseModel):
    date: datetime
    pnl: float

class TopTickerItem(BaseModel):
    symbol: str
    pnl: float

class StrategyDetailAnalytics(BaseModel):
    total_trades: int
    pnl: float
    win_rate: float
    average_duration_minutes: float