from typing import Optional, List, Dict
from uuid import UUID
from app.models.deck import PlayerDeck, DeckArchetype
from app.models.card import Card
from app.extensions import db
from sqlalchemy import func


def get_deck_by_id_data(deck_id: UUID, include_cards: bool = True) -> Optional[Dict]:
    """
    Récupère un deck par son ID avec enrichissement des données des cartes
    """
    deck = PlayerDeck.query.filter_by(id=deck_id).first()
    
    if not deck:
        return None
    
    return deck.json(include_cards=include_cards)


def get_player_decks_data(player_id: UUID, season: Optional[int] = None, 
                          faction: Optional[str] = None, page: int = 1, 
                          limit: int = 50) -> Dict:
    """
    Récupère tous les decks d'un joueur avec pagination et filtres
    """
    query = PlayerDeck.query.filter_by(player_id=player_id)
    
    if season:
        query = query.filter_by(season=season)
    
    if faction:
        query = query.filter_by(faction=faction)
    
    # Trier par dernière utilisation
    query = query.order_by(PlayerDeck.last_used_at.desc())
    
    total = query.count()
    decks = query.limit(limit).offset((page - 1) * limit).all()
    
    return {
        'decks': [deck.json(include_cards=False) for deck in decks],
        'pagination': {
            'current_page': page,
            'total_pages': (total + limit - 1) // limit,
            'total_decks': total,
            'limit': limit
        }
    }


def get_archetype_by_id_data(archetype_id: UUID) -> Optional[Dict]:
    """
    Récupère un archétype avec des exemples de decks
    """
    archetype = DeckArchetype.query.filter_by(id=archetype_id).first()
    
    if not archetype:
        return None
    
    # Récupérer les decks de cet archétype
    decks = PlayerDeck.query.filter_by(archetype_id=archetype.id).limit(10).all()
    
    return {
        'archetype': archetype.json(),
        'sample_decks': [deck.json(include_cards=False) for deck in decks]
    }


def search_archetypes_data(faction: Optional[str] = None, hero: Optional[str] = None, 
                           min_games: int = 10) -> List[Dict]:
    """
    Recherche d'archétypes par faction/hero
    """
    query = DeckArchetype.query
    
    if faction:
        query = query.filter_by(faction=faction)
    
    if hero:
        query = query.filter_by(hero=hero)
    
    # Filtrer par nombre minimum de parties
    query = query.filter(DeckArchetype.total_games >= min_games)
    
    # Trier par popularité
    archetypes = query.order_by(DeckArchetype.total_games.desc()).limit(20).all()
    
    return [archetype.json() for archetype in archetypes]


def get_deck_stats_data(season: Optional[int] = None) -> Dict:
    """
    Statistiques globales sur les decks
    """
    query = PlayerDeck.query
    
    if season:
        query = query.filter_by(season=season)
    
    total_decks = query.count()
    unique_archetypes = db.session.query(DeckArchetype).count()
    
    # Top 5 factions
    faction_stats = db.session.query(
        PlayerDeck.faction,
        func.count(PlayerDeck.id).label('count')
    ).group_by(PlayerDeck.faction).order_by(db.text('count DESC')).limit(5).all()
    
    # Top 5 héros
    hero_stats = db.session.query(
        PlayerDeck.hero,
        func.count(PlayerDeck.id).label('count')
    ).group_by(PlayerDeck.hero).order_by(db.text('count DESC')).limit(5).all()
    
    return {
        'total_decks': total_decks,
        'unique_archetypes': unique_archetypes,
        'top_factions': [{'faction': f, 'count': c} for f, c in faction_stats],
        'top_heroes': [{'hero': h, 'count': c} for h, c in hero_stats]
    }
