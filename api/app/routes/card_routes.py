from flask import Blueprint, jsonify, make_response, request
from app.services.card_service import (
  get_card_by_reference_service,
  search_cards_service
)

card_bp = Blueprint('card', __name__)

@card_bp.route('/api/card/<string:reference>', methods=['GET'])
def get_card_by_reference_route(reference):
    try:
        card = get_card_by_reference_service(reference)
        return jsonify(card.json()), 201
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
    
@card_bp.route('/api/card/search', methods=['GET'])
def search_cards_route():
    try:
        name = request.args.get('name')
        effect = request.args.get('effect')
        cost = request.args.get('cost')
        cards = search_cards_service(name, effect, cost)
        if not cards:
            return make_response(jsonify({'message': 'No cards found'}), 404)
        return jsonify([card.json() for card in cards]), 201
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)