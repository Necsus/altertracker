from flask import Blueprint, jsonify
from app.scripts.card_routine import getToken


cookiemanager_bp = Blueprint('cookiemanager', __name__)

@cookiemanager_bp.route('/getaccesstoken', methods=['GET'])
def get_access_token():
    try:
        token = getToken()
        if not token:
            return jsonify({"message": "No token found"}), 404
        return token, 200
    except Exception as e:
        print(f"Error fetching cookies: {e}")
        return jsonify({"message": "An error occurred while fetching cookies"}), 500