import datetime
from app.extensions import db

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Optionnel si lié à un compte
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(3), nullable=True)  # Code pays ISO 3166-1 alpha-2
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    discord_username = db.Column(db.String(100), nullable=True)
    
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
    
    # Relations
    user = db.relationship('User', backref='player_profile', foreign_keys=[user_id])
    team = db.relationship('Team', backref='members', foreign_keys=[team_id])
    decks = db.relationship('PlayerDeck', back_populates='player', cascade='all, delete-orphan')
    games = db.relationship('Game', foreign_keys='Game.player1_id', backref='player1_games', lazy='dynamic')
    season_stats = db.relationship('PlayerSeasonStats', back_populates='player', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Player {self.name}>"
    
    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'country': self.country,
            'team_id': self.team_id,
            'team_name': self.team.name if self.team else None,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'discord_username': self.discord_username,
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
        }
    
    def calculate_win_rate(self):
        total_games = self.total_wins + self.total_losses + self.total_draws
        if total_games > 0:
            self.win_rate = (self.total_wins / total_games) * 100
        else:
            self.win_rate = 0.0


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    tag = db.Column(db.String(10), unique=True, nullable=False)  # Abréviation
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
            'id': self.id,
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

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    faction = db.Column(db.String(50), nullable=False)
    hero_reference = db.Column(db.String(50), nullable=False)  # Référence de la carte héros
    
    # Composition du deck (peut être JSON ou relation vers une table de cartes)
    deck_list = db.Column(db.JSON, nullable=False)  # Liste des références de cartes
    
    # Stats du deck
    games_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.0)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    last_used_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=False)  # Visible par les autres joueurs
    
    # Relations
    player = db.relationship('Player', back_populates='decks')
    games = db.relationship('Game', foreign_keys='Game.player1_deck_id', backref='deck1_games', lazy='dynamic')

    def __repr__(self):
        return f"<PlayerDeck {self.name} - {self.faction}>"
    
    def json(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
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


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    
    # Joueurs
    player1_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    
    # Decks utilisés
    player1_deck_id = db.Column(db.Integer, db.ForeignKey('player_decks.id'), nullable=True)
    player2_deck_id = db.Column(db.Integer, db.ForeignKey('player_decks.id'), nullable=True)
    
    # Résultat
    winner_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=True)  # NULL pour match nul
    player1_score = db.Column(db.Integer, nullable=True)
    player2_score = db.Column(db.Integer, nullable=True)
    is_draw = db.Column(db.Boolean, default=False)
    
    # Contexte
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=True)
    season = db.Column(db.String(20), nullable=True)  # Ex: "2025-1"
    round = db.Column(db.Integer, nullable=True)  # Tour du tournoi
    game_format = db.Column(db.String(50), nullable=True)  # "Standard", "Draft", etc.
    
    # Métadonnées
    played_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    duration_minutes = db.Column(db.Integer, nullable=True)
    replay_url = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Validation
    is_verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    # Relations
    player2 = db.relationship('Player', foreign_keys=[player2_id], backref='player2_games')
    player2_deck = db.relationship('PlayerDeck', foreign_keys=[player2_deck_id], backref='deck2_games')
    winner = db.relationship('Player', foreign_keys=[winner_id], backref='won_games')
    tournament = db.relationship('Tournament', backref='games')

    def __repr__(self):
        return f"<Game {self.id}: Player{self.player1_id} vs Player{self.player2_id}>"
    
    def json(self):
        return {
            'id': self.id,
            'player1_id': self.player1_id,
            'player1_name': self.player1_games.name if self.player1_games else None,
            'player2_id': self.player2_id,
            'player2_name': self.player2.name if self.player2 else None,
            'player1_deck_id': self.player1_deck_id,
            'player2_deck_id': self.player2_deck_id,
            'winner_id': self.winner_id,
            'player1_score': self.player1_score,
            'player2_score': self.player2_score,
            'is_draw': self.is_draw,
            'tournament_id': self.tournament_id,
            'season': self.season,
            'round': self.round,
            'game_format': self.game_format,
            'played_at': self.played_at.isoformat() if self.played_at else None,
            'duration_minutes': self.duration_minutes,
            'replay_url': self.replay_url,
            'notes': self.notes,
            'is_verified': self.is_verified,
        }


class Tournament(db.Model):
    __tablename__ = 'tournaments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tournament_type = db.Column(db.String(50), nullable=False)  # "Online", "In-Person", "Nationals", etc.
    format = db.Column(db.String(50), nullable=False)  # "Standard", "Draft", etc.
    season = db.Column(db.String(20), nullable=True)
    
    # Dates
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    registration_deadline = db.Column(db.DateTime, nullable=True)
    
    # Localisation
    country = db.Column(db.String(3), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    venue = db.Column(db.String(200), nullable=True)
    is_online = db.Column(db.Boolean, default=False)
    
    # Infos
    max_players = db.Column(db.Integer, nullable=True)
    prize_pool = db.Column(db.String(100), nullable=True)
    organizer = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    stream_url = db.Column(db.String(255), nullable=True)
    
    # Statut
    status = db.Column(db.String(20), default='upcoming')  # upcoming, ongoing, completed, cancelled
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    
    # Relations
    participants = db.relationship('TournamentParticipant', back_populates='tournament', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Tournament {self.name}>"
    
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'tournament_type': self.tournament_type,
            'format': self.format,
            'season': self.season,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            'country': self.country,
            'city': self.city,
            'venue': self.venue,
            'is_online': self.is_online,
            'max_players': self.max_players,
            'prize_pool': self.prize_pool,
            'organizer': self.organizer,
            'website': self.website,
            'stream_url': self.stream_url,
            'status': self.status,
            'participant_count': len(self.participants) if self.participants else 0,
        }


class TournamentParticipant(db.Model):
    __tablename__ = 'tournament_participants'

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('player_decks.id'), nullable=True)
    
    # Résultats
    final_rank = db.Column(db.Integer, nullable=True)
    points = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    
    # Statut
    is_checked_in = db.Column(db.Boolean, default=False)
    dropped_at_round = db.Column(db.Integer, nullable=True)
    
    registered_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    
    # Relations
    tournament = db.relationship('Tournament', back_populates='participants')
    player = db.relationship('Player', backref='tournament_participations')
    deck = db.relationship('PlayerDeck', backref='tournament_uses')

    def __repr__(self):
        return f"<TournamentParticipant T{self.tournament_id} P{self.player_id}>"
    
    def json(self):
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            'player_id': self.player_id,
            'player_name': self.player.name if self.player else None,
            'deck_id': self.deck_id,
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

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    season = db.Column(db.String(20), nullable=False)  # Ex: "2025-1"
    
    # Stats de la saison
    points = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.0)
    
    # Classement
    rank = db.Column(db.Integer, nullable=True)
    highest_rank = db.Column(db.Integer, nullable=True)
    
    # Tournois
    tournaments_played = db.Column(db.Integer, default=0)
    tournaments_won = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    
    # Relations
    player = db.relationship('Player', back_populates='season_stats')
    
    # Contrainte unique pour éviter les doublons
    __table_args__ = (db.UniqueConstraint('player_id', 'season', name='unique_player_season'),)

    def __repr__(self):
        return f"<PlayerSeasonStats P{self.player_id} {self.season}>"
    
    def json(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'season': self.season,
            'points': self.points,
            'wins': self.wins,
            'losses': self.losses,
            'draws': self.draws,
            'win_rate': self.win_rate,
            'total_games': self.wins + self.losses + self.draws,
            'rank': self.rank,
            'highest_rank': self.highest_rank,
            'tournaments_played': self.tournaments_played,
            'tournaments_won': self.tournaments_won,
        }
    
    def calculate_win_rate(self):
        total_games = self.wins + self.losses + self.draws
        if total_games > 0:
            self.win_rate = (self.wins / total_games) * 100
        else:
            self.win_rate = 0.0