import datetime
import uuid
from sqlalchemy import UUID, Index
from sqlalchemy.dialects.postgresql import JSONB
from app.extensions import db

# ============================================================================
# TABLE 1 : DECK ARCHETYPE (pour grouper les decks similaires)
# ============================================================================
class DeckArchetype(db.Model):
    """
    Représente un archétype de deck (ex: "Sigismar Tokens", "Teija Boost")
    Permet de regrouper des decks similaires pour l'analyse méta
    """
    __tablename__ = 'deck_archetypes'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(200), nullable=False)  # "Sigismar Tokens"
    faction = db.Column(db.String(2), nullable=False)  # "OR", "MU", etc.
    hero = db.Column(db.String(100), nullable=False)  # "Sigismar"
    
    # Signature du deck (hash des effets normalisés)
    effect_signature = db.Column(db.String(64), nullable=False, index=True)
    
    # Métadonnées
    total_decks = db.Column(db.Integer, default=0)  # Nombre de decks associés
    total_games = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.0)
    
    # Stats par saison
    season_stats = db.Column(JSONB, default={})  # {season: {wins, losses, popularity}}
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    
    __table_args__ = (
        Index('idx_archetype_faction_hero', 'faction', 'hero'),
        Index('idx_archetype_signature', 'effect_signature'),
    )
    
    def update_stats_from_decks(self):
        """
        Recalcule les statistiques de l'archétype depuis tous les decks associés
        """
        # Récupérer tous les decks de cet archétype
        decks = PlayerDeck.query.filter_by(archetype_id=self.id).all()
        
        total_games = 0
        total_wins = 0
        total_losses = 0
        season_data = {}
        
        for deck in decks:
            total_games += deck.total_games
            total_wins += deck.total_wins
            total_losses += deck.total_losses
            
            # Agréger par saison
            if deck.season:
                season_key = str(deck.season)
                if season_key not in season_data:
                    season_data[season_key] = {
                        'games': 0,
                        'wins': 0,
                        'losses': 0,
                        'decks': 0
                    }
                
                season_data[season_key]['games'] += deck.total_games
                season_data[season_key]['wins'] += deck.total_wins
                season_data[season_key]['losses'] += deck.total_losses
                season_data[season_key]['decks'] += 1
        
        # Calculer les win rates par saison
        for season_key, stats in season_data.items():
            if stats['games'] > 0:
                stats['win_rate'] = round((stats['wins'] / stats['games']) * 100, 1)
            else:
                stats['win_rate'] = 0.0
        
        self.total_decks = len(decks)
        self.total_games = total_games
        self.win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0
        self.season_stats = season_data
        self.updated_at = datetime.datetime.now(datetime.timezone.utc)
        
        db.session.commit()
    
    def json(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'faction': self.faction,
            'hero': self.hero,
            'effect_signature': self.effect_signature,
            'total_decks': self.total_decks,
            'total_games': self.total_games,
            'win_rate': self.win_rate,
            'season_stats': self.season_stats,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# ============================================================================
# TABLE 2 : PLAYER DECK (deck spécifique d'un joueur)
# ============================================================================
class PlayerDeck(db.Model):
    """
    Représente un deck spécifique utilisé par un joueur
    Stockage optimisé avec normalisation des cartes
    """
    __tablename__ = 'player_decks'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identification
    player_id = db.Column(UUID(as_uuid=True), db.ForeignKey('players.id'), nullable=False)
    bga_deck_id = db.Column(db.String(50), nullable=True, index=True)  # ID BGA si disponible
    deck_name = db.Column(db.String(200), nullable=True)  # "Post LCQ"
    
    # Archétype associé
    archetype_id = db.Column(UUID(as_uuid=True), db.ForeignKey('deck_archetypes.id'), nullable=True)
    
    # Métadonnées du deck
    faction = db.Column(db.String(2), nullable=False, index=True)
    hero = db.Column(db.String(100), nullable=False, index=True)
    hero_uid = db.Column(db.String(100), nullable=False)  # "ALT_CORE_B_OR_01_C"
    
    # ✅ STOCKAGE OPTIMISÉ DES CARTES
    # Au lieu de stocker tout le JSON, on stocke seulement ce qui est nécessaire
    card_count = db.Column(db.Integer, default=39)  # Toujours 39 (+ 1 hero = 40)
    
    # Cartes normalisées par effet (comparable)
    cards_by_effect = db.Column(JSONB, nullable=False)
    # Format: {
    #   "effect_hash_1": {"count": 3, "uids": ["ALT_CORE_B_OR_05_R"], "rarity": "R"},
    #   "effect_hash_2": {"count": 2, "uids": ["ALT_CORE_B_MU_16_R"], "rarity": "R"},
    # }
    
    # Cartes par UID exact (pour les uniques et comparaison stricte)
    cards_by_uid = db.Column(JSONB, nullable=False)
    # Format: {
    #   "ALT_CORE_B_OR_05_R": 3,
    #   "ALT_CORE_B_MU_16_R": 2,
    # }
    
    # ✅ MÉTADONNÉES POUR L'ANALYSE
    unique_cards = db.Column(JSONB, default=[])  # Liste des UIDs uniques
    unique_count = db.Column(db.Integer, default=0)
    
    rare_count = db.Column(db.Integer, default=0)  # 15 normalement
    common_count = db.Column(db.Integer, default=0)
    
    # Signature du deck (hash basé sur les effets)
    deck_signature = db.Column(db.String(64), nullable=False, index=True)
    
    # Stats du deck
    total_games = db.Column(db.Integer, default=0)
    total_wins = db.Column(db.Integer, default=0)
    total_losses = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.0)
    
    # Dernière utilisation
    last_used_at = db.Column(db.DateTime, nullable=True)
    season = db.Column(db.Integer, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    
    # ✅ Relations avec back_populates (pas backref pour éviter les conflits)
    player = db.relationship('Player', back_populates='decks')
    archetype = db.relationship('DeckArchetype', backref='decks')
    
    __table_args__ = (
        Index('idx_deck_player_faction', 'player_id', 'faction'),
        Index('idx_deck_signature', 'deck_signature'),
        Index('idx_deck_archetype', 'archetype_id'),
    )
    
    def update_stats_from_games(self):
        """
        Recalcule les statistiques du deck depuis les parties associées
        """
        from app.models.game import Game
        
        # Récupérer toutes les parties où ce deck a été utilisé
        games_as_p1 = Game.query.filter_by(player1_deck_id=self.id).all()
        games_as_p2 = Game.query.filter_by(player2_deck_id=self.id).all()
        
        total_wins = 0
        total_losses = 0
        
        # Compter les victoires/défaites
        for game in games_as_p1:
            if game.winner_id == self.player_id:
                total_wins += 1
            elif game.winner_id is not None:  # Pas de nul
                total_losses += 1
        
        for game in games_as_p2:
            if game.winner_id == self.player_id:
                total_wins += 1
            elif game.winner_id is not None:
                total_losses += 1
        
        self.total_games = total_wins + total_losses
        self.total_wins = total_wins
        self.total_losses = total_losses
        self.win_rate = (total_wins / self.total_games * 100) if self.total_games > 0 else 0.0
        self.updated_at = datetime.datetime.now(datetime.timezone.utc)
        
        db.session.commit()
    
    def json(self, include_cards: bool = True, include_archetype: bool = False):
        data = {
            'id': str(self.id),
            'player_id': str(self.player_id),
            'bga_deck_id': self.bga_deck_id,
            'deck_name': self.deck_name,
            'faction': self.faction,
            'hero': self.hero,
            'hero_uid': self.hero_uid,
            'card_count': self.card_count,
            'unique_count': self.unique_count,
            'rare_count': self.rare_count,
            'common_count': self.common_count,
            'total_games': self.total_games,
            'total_wins': self.total_wins,
            'total_losses': self.total_losses,
            'win_rate': self.win_rate,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'season': self.season,
            'deck_signature': self.deck_signature,
            'archetype_id': str(self.archetype_id) if self.archetype_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Inclure l'archétype complet si demandé
        if include_archetype and self.archetype:
            data['archetype'] = self.archetype.json()
        
        if include_cards:
            data['cards_by_uid'] = self.cards_by_uid
            data['unique_cards'] = self.unique_cards
            
            # ✅ Enrichir avec le modèle Card complet
            from app.models.card import Card
            
            # Récupérer toutes les références de cartes
            all_card_refs = list(self.cards_by_uid.keys()) + (self.unique_cards or [])
            unique_refs = list(set(all_card_refs))
            
            if unique_refs:
                # Récupérer les cartes en une seule requête
                cards = Card.query.filter(Card.reference.in_(unique_refs)).all()
                
                # Créer un mapping reference -> modèle Card complet
                cards_data = {}
                for card in cards:
                    cards_data[card.reference] = card.json()
                
                data['cards_data'] = cards_data
        
        return data


# ============================================================================
# TABLE 3 : CARD EFFECT MAPPING (normalisation des effets)
# ============================================================================
class DeckCardEffect(db.Model):
    """
    Table de référence pour normaliser les cartes par leurs effets
    Permet de comparer des cartes avec différents designs mais mêmes effets
    """
    __tablename__ = 'deck_card_effects'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Hash de l'effet normalisé (pour comparaison rapide)
    effect_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    
    # Métadonnées
    card_name = db.Column(db.String(200), nullable=True)  # Nom principal
    card_type = db.Column(db.String(50), nullable=True)  # "character", "spell", etc.
    faction = db.Column(db.String(2), nullable=True)
    
    # Liste de tous les UIDs ayant cet effet
    variant_uids = db.Column(JSONB, default=[])
    # ["ALT_CORE_B_OR_05_R", "ALT_CORE_B_OR_05_C", "ALT_SPECIAL_B_OR_05_U"]
    
    # Effet normalisé (simplifié pour la comparaison)
    normalized_effect = db.Column(JSONB, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    
    __table_args__ = (
        Index('idx_effect_hash', 'effect_hash'),
        Index('idx_effect_faction', 'faction'),
    )


# ============================================================================
# HELPERS : Fonctions utilitaires
# ============================================================================
def compute_deck_signature(cards_by_effect: dict) -> str:
    """
    Calcule la signature d'un deck basée sur les effets (pas les UIDs)
    Permet de comparer des decks même avec des designs différents
    """
    import hashlib
    
    # Trier par effect_hash pour garantir la cohérence
    sorted_effects = sorted(cards_by_effect.items())
    
    # Créer une représentation textuelle
    signature_text = ""
    for effect_hash, card_data in sorted_effects:
        signature_text += f"{effect_hash}:{card_data['count']}|"
    
    # Hash SHA-256
    return hashlib.sha256(signature_text.encode()).hexdigest()


def normalize_card_effect(card_properties: dict) -> str:
    """
    Normalise l'effet d'une carte pour créer un hash comparable
    Ignore les détails cosmétiques (artiste, flavor text, etc.)
    """
    import hashlib
    import json
    
    # Extraire uniquement les propriétés mécaniques
    mechanical_properties = {
        'costHand': card_properties.get('costHand'),
        'costReserve': card_properties.get('costReserve'),
        'type': card_properties.get('type'),
        'subtypes': sorted(card_properties.get('subtypes', [])),
        'forest': card_properties.get('forest'),
        'mountain': card_properties.get('mountain'),
        'ocean': card_properties.get('ocean'),
        'effectDesc': card_properties.get('effectDesc'),
        'effectPlayed': card_properties.get('effectPlayed'),
        'effectPassive': card_properties.get('effectPassive'),
        'effectReserve': card_properties.get('effectReserve'),
        'effectHand': card_properties.get('effectHand'),
    }
    
    # Supprimer les None
    mechanical_properties = {k: v for k, v in mechanical_properties.items() if v is not None}
    
    # Créer un JSON stable (trié)
    json_text = json.dumps(mechanical_properties, sort_keys=True)
    
    # Hash SHA-256
    return hashlib.sha256(json_text.encode()).hexdigest()
