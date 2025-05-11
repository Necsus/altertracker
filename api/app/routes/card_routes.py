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
        faction = request.args.get('faction')
        set = request.args.get('set')
        main_effect = request.args.get('main_effect')
        echo_effect = request.args.get('echo_effect')
        main_cost = request.args.get('main_cost')
        recall_cost = request.args.get('recall_cost')
        cards = search_cards_service(name, faction, set, main_effect, echo_effect, main_cost, recall_cost)
        if not cards:
            return make_response(jsonify({'message': 'No cards found'}), 404)
        return jsonify([card.json() for card in cards]), 201
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)