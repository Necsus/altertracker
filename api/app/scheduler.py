from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.routes.script_routes import dispatch_script

def start_scheduler(app):
    scheduler = BackgroundScheduler()

    # Script toutes les 24h
    scheduler.add_job(
        lambda: run_script_with_context(app, 'script_get_unique', 3),
        trigger=CronTrigger(hour='2', minute=0))

    # Script toutes les 8h
    scheduler.add_job(
        lambda: run_script_with_context(app, 'script_get_offers', 1),
        trigger=CronTrigger(hour='8,16', minute=0))

    scheduler.start()

def run_script_with_context(app, script_name, workers):
    with app.app_context():
        dispatch_script(script_name, workers)