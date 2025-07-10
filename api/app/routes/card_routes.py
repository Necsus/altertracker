from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import Schema, fields, ValidationError
from app.services.card_service import (
  get_card_by_reference_service,
  get_effect_service,
  search_cards_service,
  get_cards_count_service,
  get_cards_in_market_count_service,
  post_offer_live_market_service,
  get_last_added_cards_service,
  get_count_cards_created_today_service,
  get_card_by_reference_with_alert_service,
  update_card_service
)
from app.services.offer_service import get_offers_by_reference_service
from app.services.purchase_service import get_purchases_by_reference_service
from app.services.user_service import get_card_is_in_collection_service
from app.extensions import cache


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
    
@card_bp.route('/search', methods=['POST'])
@jwt_required(optional=True)
def search_cards_route():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        name = data.get('name')
        rarity = data.get('rarity')
        faction = data.get('faction')
        set = data.get('set')
        main_effect = data.get('main_effect')
        main_effect_2 = data.get('main_effect_2')
        echo_effect = data.get('echo_effect')
        exclude_effect = data.get('exclude_effect')
        main_cost_range = data.get('main_cost_range')
        recall_cost_range = data.get('recall_cost_range')
        forest_power_range = data.get('forest_power_range')
        mountain_power_range = data.get('mountain_power_range')
        ocean_power_range = data.get('ocean_power_range')
        no_condition = data.get('no_condition')
        in_market = data.get('in_market')
        price_range = data.get('price_range')
        en = data.get('en', False)
        dataset_type = data.get('dataset_type')
        cards = search_cards_service(
            name, rarity, faction, set, main_effect, main_effect_2, echo_effect, exclude_effect,
            main_cost_range, recall_cost_range, forest_power_range, mountain_power_range, ocean_power_range,
            no_condition, in_market, price_range, en, dataset_type, user_id
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
        post_offer_live_market_service(validated_data)
        return jsonify({'success': 'ok'}), 201
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
@jwt_required(optional=True)
def get_card_with_offers(reference):
    try:
        user_id = get_jwt_identity()
        
        # Récupérer la carte par référence
        card = get_card_by_reference_with_alert_service(reference, user_id)
        if not card:
            return make_response(jsonify({'message': f'Card with reference {reference} not found'}), 404)

        # Récupérer les offres associées à la carte
        offers = get_offers_by_reference_service(reference)

        # Récupérer les offres d'achats associées à la carte
        purchases = get_purchases_by_reference_service(reference)

        # Si l'utilisateur est authentifié, verifier que la carte est presente dans sa collection
        is_in_collection = False
        if user_id:
            is_in_collection = get_card_is_in_collection_service(user_id, reference)

        # Retourner la carte et ses offres
        return jsonify({
            "card": card,  # Pas besoin d'appeler .json() ici, car `card` est déjà un dictionnaire
            "offers": [offer.json() for offer in offers],
            "purchases": purchases,
            "is_mine": is_in_collection
        }), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
    
@card_bp.route('/<string:reference>', methods=['PUT'])
def update_card(reference: str):
    try:
        data = request.get_json()
        card_data = data.get('card')
        if card_data:
            if card_data['reference'] not in reference:
                return make_response(jsonify({'message': 'Reference mismatch'}), 400)
            if not card_data:
                return make_response(jsonify({'message': 'Card is required'}), 400)
            update_card_service(card_data)
        return jsonify({'message': 'Carte mise à jour avec succès'}), 201
    except ValidationError as ve:
        return make_response(jsonify({'message': 'Invalid data', 'errors': ve.messages}), 400)
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
    
@card_bp.route('/effect/<string:lang>', methods=['GET'])
@cache.cached(timeout=3600, query_string=True)
def get_effect(lang: str):
    try:
        effects = get_effect_service(lang)
        return jsonify([effect.json() for effect in effects]), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)