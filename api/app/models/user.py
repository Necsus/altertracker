import datetime
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime,  default=datetime.datetime.now(datetime.timezone.utc))
    edited_at = db.Column(db.DateTime,  default=datetime.datetime.now(datetime.timezone.utc))

    def __repr__(self):
        return f"<User {self.username}>"
    
    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
        }
    
    def __init__(self, username, email, password_hash, created_at=None, edited_at=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at if created_at else datetime.datetime.now(datetime.timezone.utc)
        self.edited_at = edited_at if edited_at else datetime.datetime.now(datetime.timezone.utc)
