from flask import Blueprint, jsonify, request
from app.scripts.card_routine import getToken
from app.extensions import db


cookiemanager_bp = Blueprint('cookiemanager', __name__)

@cookiemanager_bp.route('/getaccesstoken', methods=['GET'])
def get_access_token():
    session = db.session
    clear_token = request.args.get('clearToken', default=False, type=bool) 
    try:
        token = getToken(session, clear_token)
        if not token:
            return jsonify({"message": "No token found"}), 404
        return jsonify({"token":token}), 200
    except Exception as e:
        print(f"Error fetching cookies: {e}")
        return jsonify({"message": "An error occurred while fetching cookies"}), 500