from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from services.automation_service import check_and_run_strategies
import atexit


def start_strategy_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=check_and_run_strategies,
        trigger=IntervalTrigger(minutes=1),
        id='strategy_runner',
        name='Run enabled strategies every minute',
        replace_existing=True
    )
    scheduler.start()
    print("🟢 Strategy scheduler started (interval: 1 min)")

    atexit.register(lambda: scheduler.shutdown())