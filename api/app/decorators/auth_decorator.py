from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from functools import wraps
from app.models.user import User

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({"message": "Admin access required"}), 401
        return fn(*args, **kwargs)
    return wrapper

def publisher_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_publisher:
            return jsonify({"message": "Publisher access required"}), 401
        return fn(*args, **kwargs)
    return wrapper

def beta_tester_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_beta_tester:
            return jsonify({"message": "Beta tester access required"}), 401
        return fn(*args, **kwargs)
    return wrapper

def active_bga_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.active_bga:
            return jsonify({"message": "Bga access required"}), 401
        return fn(*args, **kwargs)
    return wrapper