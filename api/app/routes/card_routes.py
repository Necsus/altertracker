from flask import Blueprint, jsonify, make_response
from app.services.card_service import CardService

card_bp = Blueprint('card', __name__)
card_service = CardService()

@card_bp.route('/api/card/<string:reference>', methods=['GET'])
def get_card_by_reference(reference):
    try:
        return jsonify(card_service.get_card_by_reference(reference).json()), 201
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)