from flask import Blueprint, jsonify
from api.app.services.card_service import CardService

card_bp = Blueprint('card', __name__)
card_service = CardService()

@card_bp.route('/api/card/<string:reference>', methods=['GET'])
def get_card_by_reference(reference):
    return jsonify(card_service.get_card_by_reference(reference))