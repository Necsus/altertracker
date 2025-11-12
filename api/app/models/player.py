import datetime
import uuid
from sqlalchemy import UUID
from app.extensions import db
from sqlalchemy.orm import relationship

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bga_id = db.Column(db.Integer, unique=True, nullable=False)
    bga_banned = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(3), nullable=True)
    team_id = db.Column(UUID(as_uuid=True), db.ForeignKey('teams.id'), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    
    # Stats globales
    total_points = db.Column(db.Integer, default=0)
    total_wins = db.Column(db.Integer, default=0)
    total_losses = db.Column(db.Integer, default=0)
    total_draws = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.0)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    last_game_at = db.Column(db.DateTime, nullable=True)

    # ✅ Relation inverse vers User (back_populates au lieu de backref)
    user = relationship("User", back_populates="player", uselist=False, passive_deletes=True)
    
    # Relations
    team = relationship('Team', backref='members', foreign_keys=[team_id])
    decks = relationship('PlayerDeck', back_populates='player', cascade='all, delete-orphan')
    season_stats = relationship('PlayerSeasonStats', back_populates='player', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Player {self.name}>"
    
    def json(self):
        # ✅ Accès sécurisé à la relation user
        user_data = {}
        try:
            if self.user:
                user_data = {
                    'user_id': self.user.id,
                    'username': self.user.username,
                }
        except Exception:
            pass
        
        return {
            'id': str(self.id),  # ✅ Convertir UUID en string pour JSON
            'bga_banned': self.bga_banned,
            'name': self.name,
            'country': self.country,
            'team_id': str(self.team_id) if self.team_id else None,  # ✅ UUID en string
            'team_name': self.team.name if self.team else None,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'total_points': self.total_points,
            'total_wins': self.total_wins,
            'total_losses': self.total_losses,
            'total_draws': self.total_draws,
            'win_rate': self.win_rate,
            'total_games': self.total_wins + self.total_losses + self.total_draws,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'last_game_at': self.last_game_at.isoformat() if self.last_game_at else None,
            **user_data  # ✅ Ajouter les données utilisateur si disponibles
        }
    
    def calculate_win_rate(self):
        total_games = self.total_wins + self.total_losses + self.total_draws
        if total_games > 0:
            self.win_rate = (self.total_wins / total_games) * 100
        else:
            self.win_rate = 0.0


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # ✅ UUID
    name = db.Column(db.String(100), unique=True, nullable=False)
    tag = db.Column(db.String(10), unique=True, nullable=False)
    logo_url = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    country = db.Column(db.String(3), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    discord_url = db.Column(db.String(255), nullable=True)
    
    # Stats d'équipe
    total_points = db.Column(db.Integer, default=0)
    total_wins = db.Column(db.Integer, default=0)
    total_losses = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Team {self.name}>"
    
    def json(self):
        member_count = len(self.members) if self.members else 0
        return {
            'id': str(self.id),  # ✅ UUID en string
            'name': self.name,
            'tag': self.tag,
            'logo_url': self.logo_url,
            'description': self.description,
            'country': self.country,
            'website': self.website,
            'discord_url': self.discord_url,
            'total_points': self.total_points,
            'total_wins': self.total_wins,
            'total_losses': self.total_losses,
            'member_count': member_count,
            'avg_points': self.total_points / member_count if member_count > 0 else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
        }


class PlayerDeck(db.Model):
    __tablename__ = 'player_decks'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # ✅ UUID
    player_id = db.Column(UUID(as_uuid=True), db.ForeignKey('players.id'), nullable=False)  # ✅ UUID
    name = db.Column(db.String(100), nullable=False)
    faction = db.Column(db.String(50), nullable=False)
    hero_reference = db.Column(db.String(50), nullable=False)
    
    deck_list = db.Column(db.JSON, nullable=False)
    
    # Stats du deck
    games_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    last_used_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=False)
    
    # Relations
    player = db.relationship('Player', back_populates='decks')
    # ✅ Relations corrigées avec viewonly pour éviter les conflits
    games_as_player1 = db.relationship('Game', foreign_keys='Game.player1_deck_id', back_populates='player1_deck', lazy='dynamic', viewonly=True)
    games_as_player2 = db.relationship('Game', foreign_keys='Game.player2_deck_id', back_populates='player2_deck', lazy='dynamic', viewonly=True)

    def __repr__(self):
        return f"<PlayerDeck {self.name} - {self.faction}>"
    
    def json(self):
        return {
            'id': str(self.id),  # ✅ UUID en string
            'player_id': str(self.player_id),  # ✅ UUID en string
            'name': self.name,
            'faction': self.faction,
            'hero_reference': self.hero_reference,
            'deck_list': self.deck_list,
            'games_played': self.games_played,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': self.win_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'is_active': self.is_active,
            'is_public': self.is_public,
        }
    
    def calculate_win_rate(self):
        if self.games_played > 0:
            self.win_rate = (self.wins / self.games_played) * 100
        else:
            self.win_rate = 0.0

class Tournament(db.Model):
    __tablename__ = 'tournaments'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bga_id = db.Column(db.Integer, unique=True, nullable=True)
    name = db.Column(db.Text, nullable=True)
    championship_name = db.Column(db.Text, nullable=True)

    # start_date = db.Column(db.DateTime, nullable=False)
    # end_date = db.Column(db.DateTime, nullable=True)
    # registration_deadline = db.Column(db.DateTime, nullable=True)
    
    # country = db.Column(db.String(3), nullable=True)
    # city = db.Column(db.String(100), nullable=True)
    # venue = db.Column(db.String(200), nullable=True)
    # is_online = db.Column(db.Boolean, default=False)
    
    # max_players = db.Column(db.Integer, nullable=True)
    # prize_pool = db.Column(db.String(100), nullable=True)
    # organizer = db.Column(db.String(100), nullable=True)
    # website = db.Column(db.String(255), nullable=True)
    # stream_url = db.Column(db.String(255), nullable=True)
    
    # status = db.Column(db.String(20), default='upcoming')
    
    # created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    # updated_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    
    participants = db.relationship('TournamentParticipant', back_populates='tournament', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Tournament {self.name}>"
    
    def json(self):
        return {
            'id': str(self.id),  # ✅ UUID en string
            'name': self.name,
            'championship_name': self.description,
            'bga_id': self.bga_id,
            # 'tournament_type': self.tournament_type,
            # 'format': self.format,
            # 'season': self.season,
            # 'start_date': self.start_date.isoformat() if self.start_date else None,
            # 'end_date': self.end_date.isoformat() if self.end_date else None,
            # 'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            # 'country': self.country,
            # 'city': self.city,
            # 'venue': self.venue,
            # 'is_online': self.is_online,
            # 'max_players': self.max_players,
            # 'prize_pool': self.prize_pool,
            # 'organizer': self.organizer,
            # 'website': self.website,
            # 'stream_url': self.stream_url,
            # 'status': self.status,
            'participant_count': len(self.participants) if self.participants else 0,
        }


class TournamentParticipant(db.Model):
    __tablename__ = 'tournament_participants'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # ✅ UUID
    tournament_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tournaments.id'), nullable=False)  # ✅ UUID
    player_id = db.Column(UUID(as_uuid=True), db.ForeignKey('players.id'), nullable=False)  # ✅ UUID
    deck_id = db.Column(UUID(as_uuid=True), db.ForeignKey('player_decks.id'), nullable=True)  # ✅ UUID
    
    final_rank = db.Column(db.Integer, nullable=True)
    points = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    
    is_checked_in = db.Column(db.Boolean, default=False)
    dropped_at_round = db.Column(db.Integer, nullable=True)
    
    registered_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    
    tournament = db.relationship('Tournament', back_populates='participants')
    player = db.relationship('Player', backref='tournament_participations')
    deck = db.relationship('PlayerDeck', backref='tournament_uses')

    def __repr__(self):
        return f"<TournamentParticipant T{self.tournament_id} P{self.player_id}>"
    
    def json(self):
        return {
            'id': str(self.id),  # ✅ UUID en string
            'tournament_id': str(self.tournament_id),  # ✅ UUID en string
            'player_id': str(self.player_id),  # ✅ UUID en string
            'player_name': self.player.name if self.player else None,
            'deck_id': str(self.deck_id) if self.deck_id else None,
            'final_rank': self.final_rank,
            'points': self.points,
            'wins': self.wins,
            'losses': self.losses,
            'draws': self.draws,
            'is_checked_in': self.is_checked_in,
            'dropped_at_round': self.dropped_at_round,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None,
        }


class PlayerSeasonStats(db.Model):
    __tablename__ = 'player_season_stats'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # ✅ UUID
    player_id = db.Column(UUID(as_uuid=True), db.ForeignKey('players.id'), nullable=False)  # ✅ UUID
    season = db.Column(db.String(20), nullable=False)
    
    points = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.0)
    
    rank = db.Column(db.Integer, nullable=True)
    highest_rank = db.Column(db.Integer, nullable=True)
    
    tournaments_played = db.Column(db.Integer, default=0)
    tournaments_won = db.Column(db.Integer, default=0)
    
    # ✅ Nouvelles colonnes pour les stats par faction
    most_played_faction = db.Column(db.String(2), nullable=True)
    most_played_hero = db.Column(db.String(100), nullable=True)
    faction_stats = db.Column(db.JSON, nullable=True)  # {'AX': {'wins': 5, 'losses': 2, 'games': 7}, ...}
    hero_stats = db.Column(db.JSON, nullable=True)     # {'Sigismar & Wingspan': {'wins': 3, 'losses': 1}, ...}
    
    # Stats de temps
    total_reflexion_time = db.Column(db.Integer, nullable=True)  # Total en secondes
    total_turns = db.Column(db.Integer, nullable=True)  # Total de tours joués
    fastest_game_minutes = db.Column(db.Integer, nullable=True)
    slowest_game_minutes = db.Column(db.Integer, nullable=True)
    
    # Streaks
    current_streak = db.Column(db.Integer, default=0)
    best_win_streak = db.Column(db.Integer, default=0)
    worst_loss_streak = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    
    player = db.relationship('Player', back_populates='season_stats')
    
    __table_args__ = (db.UniqueConstraint('player_id', 'season', name='unique_player_season'),)

    def __repr__(self):
        return f"<PlayerSeasonStats P{self.player_id} {self.season}>"
    
    def json(self, include_player: bool = True):
        data = {
            'id': str(self.id),
            'player_id': str(self.player_id),
            'season': self.season,
            'points': self.points,
            'wins': self.wins,
            'losses': self.losses,
            'draws': self.draws,
            'win_rate': round(self.win_rate, 2),
            'total_games': self.wins + self.losses + self.draws,
            'rank': self.rank,
            'highest_rank': self.highest_rank,
            
            'most_played_faction': self.most_played_faction,
            'most_played_hero': self.most_played_hero,
            'faction_stats': self.faction_stats or {},
            'hero_stats': self.hero_stats or {},
            
            'total_reflexion_time': self.total_reflexion_time,
            'total_turns': self.total_turns,  # ✅ NOUVEAU
            'fastest_game_minutes': self.fastest_game_minutes,
            'slowest_game_minutes': self.slowest_game_minutes,
            
            'current_streak': self.current_streak,
            'best_win_streak': self.best_win_streak,
            'worst_loss_streak': self.worst_loss_streak,
            
            'tournaments_played': self.tournaments_played,
            'tournaments_won': self.tournaments_won,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_player and self.player:
            data['player'] = self.player.json()
        
        return data
    
    def calculate_win_rate(self):
        total_games = self.wins + self.losses + self.draws
        if total_games > 0:
            self.win_rate = (self.wins / total_games) * 100
        else:
            self.win_rate = 0.0