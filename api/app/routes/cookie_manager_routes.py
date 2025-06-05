from flask import Blueprint, jsonify
from app.scripts.card_routine import getToken
from app.extensions import db


cookiemanager_bp = Blueprint('cookiemanager', __name__)

@cookiemanager_bp.route('/getaccesstoken', methods=['GET'])
def get_access_token():
    session = db.session
    try:
        token = getToken(session)
        if not token:
            return jsonify({"message": "No token found"}), 404
        return jsonify({"token":token}), 200
    except Exception as e:
        print(f"Error fetching cookies: {e}")
        return jsonify({"message": "An error occurred while fetching cookies"}), 500