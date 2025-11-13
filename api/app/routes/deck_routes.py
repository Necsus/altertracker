from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.decorators.auth_decorator import active_bga_required
from app.services.deck_service import DeckService
from app.models.deck import PlayerDeck, DeckArchetype
from app.extensions import db
from uuid import UUID

deck_bp = Blueprint('deck', __name__)


@deck_bp.route('/<string:deck_id>', methods=['GET'])
@jwt_required()
@active_bga_required
def get_deck_route(deck_id: str):
    """
    Récupère les détails d'un deck
    GET /api/decks/<deck_id>
    """
    try:
        deck = PlayerDeck.query.filter_by(id=UUID(deck_id)).first()
        
        if not deck:
            return jsonify({'message': 'Deck not found'}), 404
        
        include_cards = request.args.get('include_cards', 'true').lower() == 'true'
        
        return jsonify(deck.json(include_cards=include_cards)), 200
        
    except ValueError:
        return jsonify({'message': 'Invalid deck ID format'}), 400
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500


@deck_bp.route('/player/<string:player_id>', methods=['GET'])
@jwt_required()
@active_bga_required
def get_player_decks_route(player_id: str):
    """
    Récupère tous les decks d'un joueur
    GET /api/decks/player/<player_id>?season=2&faction=OR
    """
    try:
        season = request.args.get('season', type=int)
        faction = request.args.get('faction', type=str)
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        query = PlayerDeck.query.filter_by(player_id=UUID(player_id))
        
        if season:
            query = query.filter_by(season=season)
        
        if faction:
            query = query.filter_by(faction=faction)
        
        # Trier par dernière utilisation
        query = query.order_by(PlayerDeck.last_used_at.desc())
        
        total = query.count()
        decks = query.limit(limit).offset((page - 1) * limit).all()
        
        return jsonify({
            'decks': [deck.json(include_cards=False) for deck in decks],
            'pagination': {
                'current_page': page,
                'total_pages': (total + limit - 1) // limit,
                'total_decks': total,
                'limit': limit
            }
        }), 200
        
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
        
        deck1 = PlayerDeck.query.filter_by(id=UUID(deck1_id)).first()
        deck2 = PlayerDeck.query.filter_by(id=UUID(deck2_id)).first()
        
        if not deck1 or not deck2:
            return jsonify({'message': 'One or both decks not found'}), 404
        
        comparison = DeckService.compare_decks(deck1, deck2)
        
        return jsonify({
            'deck1': deck1.json(include_cards=False),
            'deck2': deck2.json(include_cards=False),
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
    Récupère un archétype de deck avec tous ses decks
    GET /api/decks/archetype/<archetype_id>
    """
    try:
        archetype = DeckArchetype.query.filter_by(id=UUID(archetype_id)).first()
        
        if not archetype:
            return jsonify({'message': 'Archetype not found'}), 404
        
        # Récupérer les decks de cet archétype
        decks = PlayerDeck.query.filter_by(archetype_id=archetype.id).limit(10).all()
        
        return jsonify({
            'archetype': archetype.json(),
            'sample_decks': [deck.json(include_cards=False) for deck in decks]
        }), 200
        
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
    GET /api/decks/archetype/search?faction=OR&hero=Sigismar
    """
    try:
        faction = request.args.get('faction', type=str)
        hero = request.args.get('hero', type=str)
        min_games = request.args.get('min_games', 10, type=int)
        
        query = DeckArchetype.query
        
        if faction:
            query = query.filter_by(faction=faction)
        
        if hero:
            query = query.filter_by(hero=hero)
        
        # Filtrer par nombre minimum de parties
        query = query.filter(DeckArchetype.total_games >= min_games)
        
        # Trier par popularité
        archetypes = query.order_by(DeckArchetype.total_games.desc()).limit(20).all()
        
        return jsonify({
            'archetypes': [archetype.json() for archetype in archetypes],
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
        
        query = PlayerDeck.query
        
        if season:
            query = query.filter_by(season=season)
        
        total_decks = query.count()
        unique_archetypes = db.session.query(DeckArchetype).count()
        
        # Top 5 factions
        faction_stats = db.session.query(
            PlayerDeck.faction,
            db.func.count(PlayerDeck.id).label('count')
        ).group_by(PlayerDeck.faction).order_by(db.text('count DESC')).limit(5).all()
        
        # Top 5 héros
        hero_stats = db.session.query(
            PlayerDeck.hero,
            db.func.count(PlayerDeck.id).label('count')
        ).group_by(PlayerDeck.hero).order_by(db.text('count DESC')).limit(5).all()
        
        return jsonify({
            'season': season,
            'total_decks': total_decks,
            'unique_archetypes': unique_archetypes,
            'top_factions': [{'faction': f, 'count': c} for f, c in faction_stats],
            'top_heroes': [{'hero': h, 'count': c} for h, c in hero_stats]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500
