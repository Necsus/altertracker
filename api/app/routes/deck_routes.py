from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.decorators.auth_decorator import active_bga_required
from app.services.deck_service import DeckService
from uuid import UUID

deck_bp = Blueprint('deck', __name__)


@deck_bp.route('/<string:deck_id>', methods=['GET'])
@jwt_required()
@active_bga_required
def get_deck_route(deck_id: str):
    """
    Récupère les détails d'un deck avec enrichissement automatique des cartes
    GET /api/decks/<deck_id>?include_cards=true
    """
    try:
        include_cards = request.args.get('include_cards', 'true').lower() == 'true'
        
        deck = DeckService.get_deck_by_id(UUID(deck_id), include_cards)
        
        if not deck:
            return jsonify({'message': 'Deck not found'}), 404
        
        return jsonify(deck), 200
        
    except ValueError:
        return jsonify({'message': 'Invalid deck ID format'}), 400
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500


@deck_bp.route('/player/<string:player_id>', methods=['GET'])
@jwt_required()
@active_bga_required
def get_player_decks_route(player_id: str):
    """
    Récupère tous les decks d'un joueur avec pagination
    GET /api/decks/player/<player_id>?season=2&faction=OR&page=1&limit=50
    """
    try:
        season = request.args.get('season', type=int)
        faction = request.args.get('faction', type=str)
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        result = DeckService.get_player_decks(
            UUID(player_id), 
            season=season, 
            faction=faction, 
            page=page, 
            limit=limit
        )
        
        return jsonify(result), 200
        
    except ValueError:
        return jsonify({'message': 'Invalid player ID format'}), 400
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500


@deck_bp.route('/compare', methods=['GET'])
@jwt_required()
@active_bga_required
def compare_decks_route():
    """
    Compare deux decks
    GET /api/decks/compare?deck1=<uuid>&deck2=<uuid>
    """
    try:
        deck1_id = request.args.get('deck1', type=str)
        deck2_id = request.args.get('deck2', type=str)
        
        if not deck1_id or not deck2_id:
            return jsonify({'message': 'Both deck1 and deck2 parameters are required'}), 400
        
        comparison = DeckService.compare_decks_by_id(UUID(deck1_id), UUID(deck2_id))
        
        if not comparison:
            return jsonify({'message': 'One or both decks not found'}), 404
        
        # Récupérer les decks pour l'affichage
        deck1 = DeckService.get_deck_by_id(UUID(deck1_id), include_cards=False)
        deck2 = DeckService.get_deck_by_id(UUID(deck2_id), include_cards=False)
        
        return jsonify({
            'deck1': deck1,
            'deck2': deck2,
            'comparison': comparison
        }), 200
        
    except ValueError:
        return jsonify({'message': 'Invalid deck ID format'}), 400
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500


@deck_bp.route('/archetype/<string:archetype_id>', methods=['GET'])
@jwt_required()
@active_bga_required
def get_archetype_route(archetype_id: str):
    """
    Récupère un archétype de deck avec des exemples de decks
    GET /api/decks/archetype/<archetype_id>
    """
    try:
        result = DeckService.get_archetype_by_id(UUID(archetype_id))
        
        if not result:
            return jsonify({'message': 'Archetype not found'}), 404
        
        return jsonify(result), 200
        
    except ValueError:
        return jsonify({'message': 'Invalid archetype ID format'}), 400
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500


@deck_bp.route('/meta/snapshot', methods=['GET'])
@jwt_required()
@active_bga_required
def get_meta_snapshot_route():
    """
    Récupère un snapshot du métagame (type HSReplay)
    GET /api/decks/meta/snapshot?season=2&faction=OR
    """
    try:
        season = request.args.get('season', type=int)
        faction = request.args.get('faction', type=str)
        
        if not season:
            return jsonify({'message': 'Season parameter is required'}), 400
        
        meta = DeckService.get_meta_snapshot(season, faction)
        
        return jsonify({
            'season': season,
            'faction': faction,
            'meta': meta
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500


@deck_bp.route('/archetype/search', methods=['GET'])
@jwt_required()
@active_bga_required
def search_archetypes_route():
    """
    Recherche d'archétypes par faction/hero
    GET /api/decks/archetype/search?faction=OR&hero=Sigismar&min_games=10
    """
    try:
        faction = request.args.get('faction', type=str)
        hero = request.args.get('hero', type=str)
        min_games = request.args.get('min_games', 10, type=int)
        
        archetypes = DeckService.search_archetypes(
            faction=faction, 
            hero=hero, 
            min_games=min_games
        )
        
        return jsonify({
            'archetypes': archetypes,
            'total': len(archetypes)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500


@deck_bp.route('/stats', methods=['GET'])
@jwt_required()
@active_bga_required
def get_deck_stats_route():
    """
    Statistiques globales sur les decks
    GET /api/decks/stats?season=2
    """
    try:
        season = request.args.get('season', type=int)
        
        stats = DeckService.get_deck_stats(season)
        
        return jsonify({
            'season': season,
            **stats
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500
