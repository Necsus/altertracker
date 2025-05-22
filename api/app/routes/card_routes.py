from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import Schema, fields, ValidationError
from app.services.card_service import (
  get_card_by_reference_service,
  search_cards_service,
  get_cards_count_service,
  get_cards_in_market_count_service,
  post_offer_live_market_service,
  get_last_added_cards_service,
  get_count_cards_created_today_service
)
from app.services.offer_service import get_offers_by_reference_service


card_bp = Blueprint('card', __name__)

@card_bp.route('/count', methods=['GET'])
def count_cards_route():
    try:
        # Assuming you have a function to count cards
        count = get_cards_count_service()
        return jsonify({'count': count}), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
    
@card_bp.route('/inmarketcount', methods=['GET'])
def count_cards_in_market_route():
    try:
        # Assuming you have a function to count cards
        count = get_cards_in_market_count_service()
        return jsonify({'count': count}), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)

@card_bp.route('/<string:reference>', methods=['GET'])
def get_card_by_reference_route(reference):
    try:
        card = get_card_by_reference_service(reference)
        return jsonify(card.json()), 201
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
    
@card_bp.route('/search', methods=['GET'])
@jwt_required(optional=True)
def search_cards_route():
    try:
        user_id = get_jwt_identity()
        name = request.args.get('name')
        rarity = request.args.get('rarity')
        faction = request.args.get('faction')
        set = request.args.get('set')
        main_effect = request.args.get('main_effect')
        main_effect_2 = request.args.get('main_effect_2')
        echo_effect = request.args.get('echo_effect')
        main_cost = request.args.get('main_cost')
        recall_cost = request.args.get('recall_cost')
        forest_power = request.args.get('forest_power')
        mountain_power = request.args.get('mountain_power')
        ocean_power = request.args.get('ocean_power')
        in_market = request.args.get('in_market')
        no_condition = request.args.get('no_condition')
        cards = search_cards_service(
            name, rarity, faction, set, main_effect, main_effect_2,
            echo_effect, main_cost, recall_cost, forest_power, mountain_power, ocean_power,
            in_market, no_condition, user_id
        )
        return jsonify(cards), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)

class OfferLiveMarketSchema(Schema):
    reference = fields.Str(required=True)
    status = fields.Str(required=True)
    offerId = fields.Str()
    price = fields.Float()
    currency = fields.Str()

@card_bp.route('/offerlivemarket', methods=['POST'])
def post_offer_live_market():
    try:
        data = request.get_json()
        schema = OfferLiveMarketSchema(many=True)
        validated_data = schema.load(data)
        print('post_offer_live_market_service')
        post_offer_live_market_service(validated_data)
        return jsonify({'message': 'Offres mises à jour avec succès'}), 201
    except ValidationError as ve:
        return make_response(jsonify({'message': 'Invalid data', 'errors': ve.messages}), 400)
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
    
@card_bp.route('/lastadded', methods=['GET'])
def get_last_added_cards():
    try:
        count = get_count_cards_created_today_service()
        cards = get_last_added_cards_service()
        return jsonify({ "cards": [card.json() for card in cards], "count" : count }), 201
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)

@card_bp.route('/<string:reference>/offers', methods=['GET'])
def get_card_with_offers(reference):
    try:
        # Récupérer la carte par référence
        card = get_card_by_reference_service(reference)
        if not card:
            return make_response(jsonify({'message': f'Card with reference {reference} not found'}), 404)

        # Récupérer les offres associées à la carte
        offers = get_offers_by_reference_service(reference)
        # Retourner la carte et ses offres
        return jsonify({
            "card": card.json(),
            "offers": [offer.json() for offer in offers]
        }), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)