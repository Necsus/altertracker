from flask import Blueprint, jsonify, make_response, request
from app.services.player_service import (
  get_all_seasons_service,
  get_ladder_by_season_service,
  get_player_by_id_service,
  get_player_history_service,
  get_player_overview_service,
  get_total_players_service,
  import_deck_service,
  import_player_bga_service,
  reload_player_service,
  search_players_bga_service,
  search_players_service,
  import_ladder_service
)
from flask_jwt_extended import jwt_required
from app.decorators.auth_decorator import active_bga_required, admin_required
from app.extensions import cache

player_bp = Blueprint('player', __name__)

@player_bp.route('/search', methods=['GET'])
@jwt_required()
def search_players_route():
    try:
        query = request.args.get('query', '', type=str)
        
        if not query or len(query) < 2:
            return jsonify({'message': 'Query must be at least 2 characters'}), 400
        
        players = search_players_service(query)
        return jsonify(players), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
    
@player_bp.route('/searchbga', methods=['GET'])
@jwt_required()
def search_players_bga_route():
    try:
        query = request.args.get('query', '', type=str)
        if not query or len(query) < 2:
            return jsonify({'message': 'Query must be at least 2 characters'}), 400
        bga_players = search_players_bga_service(query)
        if bga_players.get('status') != 1:
            return jsonify({
                'message': bga_players.get('error', 'BGA search failed'),
                'players': []
            }), 500
        return jsonify(bga_players['players']), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
    
@player_bp.route('/importbga/<int:bga_id>', methods=['GET'])
@jwt_required()
def get_player_route(bga_id: int):
    try:
        response = import_player_bga_service(bga_id)
        if response.get('status') != 1:
            return jsonify({'message': response.get('error', 'Import failed')}), 500
        player_id = response.get('player_id')
        return jsonify(player_id), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)

@player_bp.route('/<string:player_id>', methods=['GET'])
@jwt_required()
def get_player_by_id_route(player_id: str):
    try:
        player = get_player_by_id_service(player_id)
        
        if not player:
            return jsonify({'message': 'Player not found'}), 404
        
        return jsonify(player), 200
        
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return make_response(jsonify({'message': f'An error occurred: {str(e)}'}), 500)
    

@player_bp.route('/history/<string:player_id>', methods=['GET'])
@jwt_required()
def get_player_history_by_id_route(player_id: str):
    try:
        season = request.args.get('season', 0, type=int)
        history = get_player_history_service(player_id, season)

        if not history:
            return jsonify({'message': 'Player history not found'}), 404

        return jsonify(history), 200
        
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return make_response(jsonify({'message': f'An error occurred: {str(e)}'}), 500)
    
@player_bp.route('/importladder/<int:season>', methods=['GET'])
@jwt_required()
@admin_required
def import_ladder_route(season: int):
    try:
        result = import_ladder_service(season)
        
        if result.get('status') != 1:
            return jsonify({
                'message': result.get('error', 'Ladder import failed')
            }), 400
        
        return jsonify({
            'message': f"Ladder season {result.get('season')} imported successfully",
            'stats': result.get('stats')
        }), 201
        
    except Exception as e:
        return jsonify({
            'message': f'An error occurred: {str(e)}'
        }), 500
    
@player_bp.route('/ladder/<int:season>', methods=['GET'])
@cache.cached(timeout=900, query_string=True)
@jwt_required()
def get_ladder_by_season_route(season: int):
    try:
        # ✅ Paramètres de pagination
        include_player = request.args.get('include_player', 'true').lower() == 'true'
        hero = request.args.get('hero', None, type=str)
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        # ✅ Validation
        if page < 1:
            return jsonify({'message': 'Page must be >= 1'}), 400
        
        if limit < 1 or limit > 500:
            return jsonify({'message': 'Limit must be between 1 and 500'}), 400
        
        # ✅ Récupérer le ladder avec pagination
        ladder = get_ladder_by_season_service(
            season=season,
            hero=hero,
            include_player=include_player,
            page=page,
            limit=limit
        )
        
        return jsonify(ladder), 200

    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return make_response(jsonify({'message': f'An error occurred: {str(e)}'}), 500)

@player_bp.route('/infos', methods=['GET'])
@jwt_required()
def get_seasons_infos():
    try:
        return jsonify({
            'seasons': get_all_seasons_service(),
            'total_players': get_total_players_service()
        }), 200
    except Exception as e:
        return make_response(jsonify({'message': f'An error occurred: {str(e)}'}), 500)

@player_bp.route('/overview/<string:player_id>', methods=['GET'])
@jwt_required()
def get_player_overview_by_id_route(player_id: str):
    try:
        season = request.args.get('season', 0, type=int)
        overview = get_player_overview_service(player_id, season)

        if not overview:
            return jsonify({'message': 'Player overview not found'}), 404

        return jsonify(overview), 200

    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return make_response(jsonify({'message': f'An error occurred: {str(e)}'}), 500)

@player_bp.route('/reload/<string:player_id>', methods=['GET'])
@jwt_required()
def reload_player_route(player_id: str):
    try:
        result = reload_player_service(player_id)
        
        if result['status'] == 1:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)
    
@player_bp.route('/importtable/<int:table_id>', methods=['GET'])
@jwt_required()
@active_bga_required
def import_table_route(table_id: int):
    try:
        result = import_deck_service(table_id)
        if result.get('status', 0) != 1:
            return jsonify({'message': result.get('error', 'Import failed')}), 500
        return jsonify(result), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)