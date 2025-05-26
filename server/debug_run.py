from database import SessionLocal
from models.strategy import Strategy
from services.automation_service import run_strategy_for_ticker  # путь к твоему файлу
from sqlalchemy.orm import joinedload
from models.user import User
from models.strategy_ticker import StrategyTicker

# 👉 Настраиваем сессию
db = SessionLocal()

# 👉 Вытаскиваем конкретную стратегию (ID поменяй на свою)
strategy_id = 1
strategy = db.query(Strategy).options(joinedload(Strategy.user), joinedload(Strategy.tickers).joinedload(StrategyTicker.user_stock)).filter_by(id=strategy_id).first()

if not strategy:
    print("❌ Strategy not found")
    exit()

user = strategy.user

# 👉 Для отладки можно вызвать конкретный тикер
for link in strategy.tickers:
    ticker = link.user_stock.ticker
    print(f"🔍 Manually testing strategy {strategy.title} on {ticker}")
    run_strategy_for_ticker(strategy, ticker, user, db)