from flask import Blueprint, jsonify, make_response, request
from app.services.player_service import search_players_service

player_bp = Blueprint('player', __name__)

@player_bp.route('/search', methods=['GET'])
def search_players_route():
    try:
        query = request.args.get('query', '', type=str)
        
        if not query or len(query) < 2:
            return jsonify({'message': 'Query must be at least 2 characters'}), 400
        
        players = search_players_service(query)
        return jsonify(players), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)