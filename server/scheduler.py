from apscheduler.schedulers.background import BackgroundScheduler
from server.services.automation_service import check_and_run_strategies

scheduler = BackgroundScheduler()
scheduler.add_job(check_and_run_strategies, 'interval', minutes=1, id='run_strategies_job')

def start_scheduler():
    print("🔁 Стартуем планировщик стратегий...")
    scheduler.start()