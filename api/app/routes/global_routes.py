from flask import Blueprint, jsonify
from app.services.global_service import GlobalService

global_bp = Blueprint('global', __name__)
global_service = GlobalService()

@global_bp.route('/api/ping', methods=['GET'])
def get_ping():
    return jsonify(global_service.get_ping())