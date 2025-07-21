import eventlet
eventlet.monkey_patch()
from app import create_app
from app.extensions import socketio
from app.scheduler import start_scheduler
from app.config import ConfigEnv

app = create_app()
if ConfigEnv.FLASK_ENV == 'production':
    start_scheduler(app)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)