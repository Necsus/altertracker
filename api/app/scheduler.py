from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.routes.script_routes import dispatch_script

def start_scheduler(app):
    scheduler = BackgroundScheduler()

    # # Script toutes les 24h
    # scheduler.add_job(
    #     lambda: run_script_with_context(app, 'script_get_unique'),
    #     trigger=CronTrigger(hour='2,14', minute=0))

    # # Script toutes les 4h
    # scheduler.add_job(
    #     lambda: run_script_with_context(app, 'script_get_offers'),
    #     trigger=CronTrigger(hour='0,6,12,18', minute=0))

    scheduler.start()

def run_script_with_context(app, script_name):
    with app.app_context():
        dispatch_script(script_name)