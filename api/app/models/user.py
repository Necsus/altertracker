import datetime
from sqlalchemy import UUID, ForeignKey
from app.extensions import db
from sqlalchemy.orm import relationship
from app.models.player import Player

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    edited_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    is_admin = db.Column(db.Boolean, default=False)
    is_publisher = db.Column(db.Boolean, default=False)
    is_email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    is_banned = db.Column(db.Boolean, nullable=True)
    banned_at = db.Column(db.DateTime, nullable=True)
    discord_id = db.Column(db.String, nullable=True)

    # ✅ Clé étrangère vers Player (SET NULL au lieu de CASCADE)
    player_id = db.Column(
        UUID(as_uuid=True), 
        ForeignKey("players.id", ondelete="SET NULL"),  # ✅ SET NULL au lieu de CASCADE
        nullable=True
    )
    
    # ✅ Relation sans cascade (pas de delete-orphan)
    player = relationship(
        "Player", 
        back_populates="user",
        foreign_keys=[player_id]  # ✅ Spécifier explicitement la FK
    )

    def __repr__(self):
        return f"<User {self.username}>"
    
    def json(self):
        # ✅ Accès sécurisé au player
        player_data = {}
        try:
            if self.player:
                player_data = {
                    'player_id': str(self.player.id),
                    'player_name': self.player.name
                }
        except Exception:
            pass
        
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            # ❌ NE JAMAIS exposer password_hash !
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'is_admin': self.is_admin,
            'is_publisher': self.is_publisher,
            'is_email_verified': self.is_email_verified,
            'email_verified_at': self.email_verified_at.isoformat() if self.email_verified_at else None,
            'is_banned': self.is_banned,
            'banned_at': self.banned_at.isoformat() if self.banned_at else None,
            'discord_id': self.discord_id,
            **player_data  # ✅ Ajouter les infos du player
        }
    
    def __init__(self, username, email, password_hash, created_at=None, edited_at=None, 
                 is_email_verified=False, email_verified_at=None, is_banned=False, 
                 banned_at=None, discord_id=None, player_id=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at if created_at else datetime.datetime.now(datetime.timezone.utc)
        self.edited_at = edited_at
        self.is_email_verified = is_email_verified
        self.email_verified_at = email_verified_at
        self.is_banned = is_banned
        self.banned_at = banned_at
        self.discord_id = discord_id
        self.player_id = player_id
