import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.strategy import Strategy
from services.automation_service import run_strategy

db = SessionLocal()

strategy = db.query(Strategy).filter(Strategy.is_enabled == True).first()
if strategy:
    run_strategy(strategy, db)
    print("✅ Автоматизация стратегии выполнена")
else:
    print("⚠️ Нет включённых стратегий для запуска")