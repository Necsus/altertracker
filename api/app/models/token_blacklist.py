from datetime import datetime
from app.extensions import db


class TokenBlacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
          return f"<TokenBlacklist {self.id}>"
      
    def json(self):
        return {
            'id': self.id,
            'jti': self.jti,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
      
    def __init__(self, jti, created_at=None):
        self.jti = jti
        self.created_at = created_at