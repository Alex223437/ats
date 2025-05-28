from database import SessionLocal
from models.strategy import Strategy
from services.tf_strategy_service import run_tf_strategy_for_ticker  # путь к твоей функции
from sqlalchemy.orm import Session

# Подставь реальные значения
TEST_STRATEGY_ID = 12
TEST_TICKER = "AS"

def test():
    db: Session = SessionLocal()
    strategy = db.query(Strategy).filter(Strategy.id == TEST_STRATEGY_ID).first()
    user = strategy.user

    run_tf_strategy_for_ticker(strategy, TEST_TICKER, user, db)

if __name__ == "__main__":
    test()