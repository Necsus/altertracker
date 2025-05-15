from flask import Blueprint, jsonify, make_response, request
from marshmallow import Schema, fields, ValidationError
from app.services.card_service import (
  get_card_by_reference_service,
  search_cards_service,
  get_cards_count_service,
  get_cards_in_market_count_service,
  post_offer_live_market_service
)

card_bp = Blueprint('card', __name__)

@card_bp.route('/api/card/count', methods=['GET'])
def count_cards_route():
    try:
        # Assuming you have a function to count cards
        count = get_cards_count_service()
        return jsonify({'count': count}), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
    
@card_bp.route('/api/card/inmarketcount', methods=['GET'])
def count_cards_in_market_route():
    try:
        # Assuming you have a function to count cards
        count = get_cards_in_market_count_service()
        return jsonify({'count': count}), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)

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
        rarity = request.args.get('rarity')
        faction = request.args.get('faction')
        set = request.args.get('set')
        main_effect = request.args.get('main_effect')
        main_effect_2 = request.args.get('main_effect_2')
        echo_effect = request.args.get('echo_effect')
        main_cost = request.args.get('main_cost')
        recall_cost = request.args.get('recall_cost')
        in_market = request.args.get('in_market')
        no_condition = request.args.get('no_condition')
        cards = search_cards_service(name, rarity, faction, set, main_effect, main_effect_2, echo_effect, main_cost, recall_cost, in_market, no_condition)
        return jsonify([card.json() for card in cards]), 201
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)

class OfferLiveMarketSchema(Schema):
    id = fields.Int()
    reference = fields.Str(required=True)
    status = fields.Str(required=True)
    offerId = fields.Str()
    convertedPrice = fields.Float()
    convertedCurrency = fields.Str()
    quantity = fields.Int()

@card_bp.route('/api/card/offerlivemarket', methods=['POST'])
def post_offer_live_market():
    try:
        data = request.get_json()
        schema = OfferLiveMarketSchema(many=True)
        validated_data = schema.load(data)
        post_offer_live_market_service(validated_data)
        return jsonify({'message': 'Offres mises à jour avec succès'}), 201
    except ValidationError as ve:
        return make_response(jsonify({'message': 'Invalid data', 'errors': ve.messages}), 400)
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)