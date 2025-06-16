from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from app.routes.script_routes import dispatch_script
from app.extensions import socketio

def start_scheduler(app):
    print(f'Heure locale Europe/Paris : {datetime.now(pytz.timezone("Europe/Paris"))}')
    scheduler = BackgroundScheduler(timezone="Europe/Paris")

    # Script toutes les 24h
    scheduler.add_job(
        lambda: run_script_with_context(app, 'script_get_unique'),
        trigger=CronTrigger(hour='4,16', minute=0))

    # Script toutes les 4h
    scheduler.add_job(
        lambda: run_script_with_context(app, 'script_get_offers'),
        trigger=CronTrigger(hour='2,8,14,20', minute=0))

    scheduler.start()

def run_script_with_context(app, script_name):
    with app.app_context():
        dispatch_script(script_name)