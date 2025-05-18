from flask import Blueprint, jsonify, make_response
from app.services.offer_service import (
  get_last_added_offers_service,
  get_last_edited_offers_service,
  get_last_deleted_offers_service
)

offer_bp = Blueprint('offer', __name__)

@offer_bp.route('/lastadded', methods=['GET'])
def get_last_added_cards():
    try:
        offers = get_last_added_offers_service()
        return [
            {
                "current_offer": offer.json(),
                "card": card.json()
            }
            for offer, card in offers
        ], 201
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
    
@offer_bp.route('/lastedited', methods=['GET'])
def get_last_edited_cards():
    try:
        offers = get_last_edited_offers_service()
        return jsonify(offers), 201
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
    
@offer_bp.route('/lastdeleted', methods=['GET'])
def get_last_deleted_cards():
    try:
        offers = get_last_deleted_offers_service()
        return [
            {
                "current_offer": offer.json(),
                "card": card.json()
            }
            for offer, card in offers
        ], 201
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
