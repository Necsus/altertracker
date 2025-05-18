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
    is_admin = db.Column(db.Boolean, default=False)
    is_email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)


    def __repr__(self):
        return f"<User {self.username}>"
    
    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'is_admin': self.is_admin,
        }
    
    def __init__(self, username, email, password_hash, created_at=None, edited_at=None, is_email_verified=False, email_verified_at=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at if created_at else datetime.datetime.now(datetime.timezone.utc)
        self.edited_at = edited_at if edited_at else datetime.datetime.now(datetime.timezone.utc)
        self.is_email_verified = is_email_verified
        self.email_verified_at = email_verified_at if email_verified_at else datetime.datetime.now(datetime.timezone.utc)
