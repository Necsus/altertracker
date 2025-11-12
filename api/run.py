from gevent import monkey
monkey.patch_all()

import logging
from app import create_app
from app.extensions import socketio
from app.scheduler import start_scheduler
from app.config import ConfigEnv

app = create_app()

# Configuration des logs uniquement en développement
if ConfigEnv.FLASK_ENV != 'production':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.getLogger('werkzeug').setLevel(logging.INFO)

if ConfigEnv.FLASK_ENV == 'production':
    start_scheduler(app)

if __name__ == '__main__':
    socketio.run(
        app, 
        debug=(ConfigEnv.FLASK_ENV != 'production'),
        host='0.0.0.0', 
        port=5001,
        log_output=(ConfigEnv.FLASK_ENV != 'production'),
        use_reloader=(ConfigEnv.FLASK_ENV != 'production')
    )