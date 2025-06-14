import eventlet
eventlet.monkey_patch()
from app import create_app
from app.extensions import socketio
from app.scheduler import start_scheduler

app = create_app()
# start_scheduler()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)