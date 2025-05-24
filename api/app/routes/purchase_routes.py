from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.purchase_service import (
    add_purchase_offer_service,
    delete_purchase_offer_service,
    get_purchases_by_reference_service,
    get_purchases_by_user_service
)

purchase_bp = Blueprint('purchase', __name__)

@purchase_bp.route('/reference/<reference>', methods=['GET'])
def get_purchase_by_reference_route(reference: str):
    try:
        # Assuming you have a function to get purchase by reference
        purchase = get_purchases_by_reference_service(reference)
        if not purchase:
            return make_response(jsonify({'message': 'Purchase not found'}), 404)
        return jsonify(purchase.json()), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)

@purchase_bp.route('/mine', methods=['GET'])
@jwt_required()
def get_purchases_by_user_route():
    try:
        user_id = get_jwt_identity()
        purchases = get_purchases_by_user_service(user_id)
        if not purchases:
            return make_response(jsonify({'message': 'No purchases found for this user'}), 404)
        return jsonify(purchases), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)

@purchase_bp.route('/', methods=['POST'])
@jwt_required()
def add_purchase_offer_route():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        data['id_user'] = user_id  # Associer l'utilisateur connecté à l'achat
        new_purchase = add_purchase_offer_service(data)
        if not new_purchase:
            return make_response(jsonify({'message': 'Failed to add purchase offer'}), 400)
        return jsonify(new_purchase), 201
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)

@purchase_bp.route('/<int:purchase_id>', methods=['DELETE'])
@jwt_required()
def delete_purchase_offer_route(purchase_id: int):
    try:
        success = delete_purchase_offer_service(purchase_id)
        if not success:
            return make_response(jsonify({'message': 'Failed to delete purchase offer'}), 404)
        return jsonify({'message': 'Purchase offer deleted successfully'}), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)

