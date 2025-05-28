from flask import Blueprint, current_app
from flask_jwt_extended import jwt_required
from flask_socketio import emit
from app.extensions import socketio, limiter
from app.decorators.auth_decorator import admin_required
from app.scripts import (
  script_get_no_unique, script_get_unique, script_get_en
)

script_bp = Blueprint('script', __name__)
ALLOWED_SCRIPTS = {'script_get_no_unique', 'script_get_unique', 'script_get_en'}

def dispatch_script(script: str, workers: int = 3, faction: str = None):
    app = current_app._get_current_object()
    with app.app_context():
        try:
            if script == 'script_get_unique':
                script_get_unique.run_script(faction, workers)
            if script == 'script_get_no_unique':
                script_get_no_unique.run_script()
            if script == 'script_get_en':
                script_get_en.run_script(faction, workers)
        except Exception as e:
            socketio.emit('script_error', {'error': str(e)})
        finally:
            socketio.emit('script_finished', {'status': 'done'})

def run_with_app_context(app, script_name: str, workers: int = None, faction: str = None):
    def task():
        with app.app_context():
            try:
                dispatch_script(script_name, workers, faction)
            except Exception as e:
                socketio.emit('script_error', {'error': str(e)})
            finally:
                socketio.emit('script_finished', {'status': 'done'})

    socketio.start_background_task(task)

@script_bp.route('/start/<script_name>', defaults={'workers': None, 'faction': None})
@script_bp.route('/start/<script_name>/<int:workers>', defaults={'faction': None})
@script_bp.route('/start/<script_name>/<int:workers>/<faction>')
@jwt_required()
@admin_required
@limiter.limit("5 per minute")
def start_script(script_name: str, workers: int = None, faction: str = None):
    if script_name not in ALLOWED_SCRIPTS or '.' in script_name or '/' in script_name:
        return {'error': 'Script not allowed'}, 403 # Refuser les scripts non autorisés
    app = current_app._get_current_object()
    run_with_app_context(app, script_name, workers, faction)
    return {'status': 'started'}

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('server_message', {'data': '🟢 Connecté sur le socketio'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
