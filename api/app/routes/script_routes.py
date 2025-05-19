
import subprocess
import threading
from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.extensions import socketio

script_bp = Blueprint('script', __name__)

def run_script():
    try:
        process = subprocess.Popen(
            ['python3', 'app/scripts/script_get_no_unique.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in process.stdout:
            socketio.emit('script_output', {'data': line})

        process.stdout.close()
        process.wait()
    except Exception as e:
        socketio.emit('script_error', {'error': str(e)})
    finally:
        socketio.emit('script_finished', {'status': 'done'})

@script_bp.route('/start-script')
@jwt_required()
def start_script():
    # thread = threading.Thread(target=run_script)
    # thread.start()
    return {'status': 'started'}
