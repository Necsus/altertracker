from flask import Blueprint, jsonify
from app.services.example_service import ExampleService

example_bp = Blueprint('example', __name__)
example_service = ExampleService()

@example_bp.route('/api/example', methods=['GET'])
def get_example():
    return jsonify(example_service.get_example_data())