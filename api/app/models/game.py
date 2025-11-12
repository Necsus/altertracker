import datetime
import uuid
from sqlalchemy import UUID
from app.extensions import db

class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_id = db.Column(db.Integer, unique=True, nullable=False)
    ranked = db.Column(db.Boolean, nullable=True)
    tournament_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tournaments.id'), nullable=True)

    # Joueurs
    player1_id = db.Column(UUID(as_uuid=True), db.ForeignKey('players.id'), nullable=False)
    player2_id = db.Column(UUID(as_uuid=True), db.ForeignKey('players.id'), nullable=False)
    
    # Decks utilisés (OPTIONNEL - peut être NULL si le deck n'est pas tracké)
    player1_deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('player_decks.id'), nullable=True)
    player2_deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('player_decks.id'), nullable=True)

    # ✅ TOUJOURS stocker faction/hero directement (plus fiable que les decks)
    player1_faction = db.Column(db.String(2), nullable=True)
    player2_faction = db.Column(db.String(2), nullable=True)
    player1_hero = db.Column(db.String(100), nullable=True)
    player2_hero = db.Column(db.String(100), nullable=True)

    # Stats de la partie
    player1_reflexion_time = db.Column(db.Integer, nullable=True)
    player2_reflexion_time = db.Column(db.Integer, nullable=True)
    player1_nb_turns = db.Column(db.Integer, nullable=True)
    player2_nb_turns = db.Column(db.Integer, nullable=True)
    player1_arena_point_win = db.Column(db.Float, nullable=True)
    player2_arena_point_win = db.Column(db.Float, nullable=True)
    player1_arena_point_after_game = db.Column(db.Float, nullable=True)
    player2_arena_point_after_game = db.Column(db.Float, nullable=True)
    
    # Résultat
    winner_id = db.Column(UUID(as_uuid=True), db.ForeignKey('players.id'), nullable=True)
    is_draw = db.Column(db.Boolean, default=False)

    season = db.Column(db.Integer, nullable=True)
    round = db.Column(db.Integer, nullable=True)
    game_format = db.Column(db.String(50), nullable=True)
    
    played_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    duration_minutes = db.Column(db.Integer, nullable=True)
    replay_url = db.Column(db.String(255), nullable=True)
    
    start = db.Column(db.DateTime, nullable=True)
    end = db.Column(db.DateTime, nullable=True)

    # Relations simplifiées
    player1 = db.relationship('Player', foreign_keys=[player1_id], backref='games_as_player1')
    player2 = db.relationship('Player', foreign_keys=[player2_id], backref='games_as_player2')
    winner = db.relationship('Player', foreign_keys=[winner_id], backref='won_games')
    tournament = db.relationship('Tournament', backref='games')
    
    # ✅ Relations vers les decks sans back_populates (évite les conflits)
    player1_deck = db.relationship('PlayerDeck', foreign_keys=[player1_deck_id])
    player2_deck = db.relationship('PlayerDeck', foreign_keys=[player2_deck_id])

    def __repr__(self):
        return f"<Game {self.id}: {self.player1_id} vs {self.player2_id}>"
    
    def json(self, include_players: bool = True, include_decks: bool = False, include_tournament: bool = False):
        data = {
            'id': str(self.id),
            'table_id': self.table_id,
            'ranked': self.ranked,
            
            # IDs des joueurs
            'player1_id': str(self.player1_id),
            'player2_id': str(self.player2_id),
            
            # Infos rapides des joueurs
            'player1_name': self.player1.name if self.player1 else None,
            'player1_country': self.player1.country if self.player1 else None,
            'player2_name': self.player2.name if self.player2 else None,
            'player2_country': self.player2.country if self.player2 else None,
            
            # Factions et héros
            'player1_faction': self.player1_faction,
            'player2_faction': self.player2_faction,
            'player1_hero': self.player1_hero,
            'player2_hero': self.player2_hero,
            
            # Decks
            'player1_deck_id': str(self.player1_deck_id) if self.player1_deck_id else None,
            'player2_deck_id': str(self.player2_deck_id) if self.player2_deck_id else None,

            'player1_reflexion_time': self.player1_reflexion_time,
            'player2_reflexion_time': self.player2_reflexion_time,

            'player1_nb_turns': self.player1_nb_turns,
            'player2_nb_turns': self.player2_nb_turns,

            'player1_arena_point_win': self.player1_arena_point_win,
            'player2_arena_point_win': self.player2_arena_point_win,

            'player1_arena_point_after_game': self.player1_arena_point_after_game,
            'player2_arena_point_after_game': self.player2_arena_point_after_game,
            
            # Résultat
            'winner_id': str(self.winner_id) if self.winner_id else None,
            'is_draw': self.is_draw,
            
            # Contexte
            'tournament_id': str(self.tournament_id) if self.tournament_id else None,
            'season': self.season,
            'round': self.round,
            'game_format': self.game_format,
            
            # Dates
            'played_at': self.played_at.isoformat() if self.played_at else None,
            'start': self.start.isoformat() if self.start else None,
            'end': self.end.isoformat() if self.end else None,
            'duration_minutes': self.duration_minutes,
            
            # Métadonnées
            'replay_url': self.replay_url
        }
        
        if include_players:
            data['player1'] = self.player1.json() if self.player1 else None
            data['player2'] = self.player2.json() if self.player2 else None
        
        if include_decks:
            data['player1_deck'] = self.player1_deck.json() if self.player1_deck else None
            data['player2_deck'] = self.player2_deck.json() if self.player2_deck else None

        if include_tournament and self.tournament:
            data['tournament'] = self.tournament.json()
        
        return data

