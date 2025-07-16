from flask import Blueprint, jsonify, make_response
from app.services.offer_service import (
  get_last_added_offers_service,
  get_last_edited_offers_service,
  get_last_deleted_offers_service,
  get_count_offers_deleted_today_service,
  get_count_offers_edited_today_service,
  get_count_offers_added_today_service
)
from app.extensions import cache

offer_bp = Blueprint('offer', __name__)

@offer_bp.route('/lastadded', methods=['GET'])
@cache.cached(timeout=3600, query_string=True)
def get_last_added_cards():
    try:
        count = get_count_offers_added_today_service()
        offers = get_last_added_offers_service()
        return {
            "count": count,
            "offers" :[
                {
                    
                    "offer": offer.json(),
                    "card": card.json()
                }
                for offer, card in offers
        ]}, 201
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
    
@offer_bp.route('/lastedited', methods=['GET'])
@cache.cached(timeout=3600, query_string=True)
def get_last_edited_cards():
    try:
        count = get_count_offers_edited_today_service()
        offers = get_last_edited_offers_service()
        return jsonify({"offers": offers, "count": count}), 201
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
    
@offer_bp.route('/lastdeleted', methods=['GET'])
@cache.cached(timeout=3600, query_string=True)
def get_last_deleted_cards():
    try:
        count = get_count_offers_deleted_today_service()
        offers = get_last_deleted_offers_service()
        return jsonify({"offers": offers, "count": count}), 201
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
