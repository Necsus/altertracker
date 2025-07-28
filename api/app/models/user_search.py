from datetime import datetime, timezone
from app.extensions import db


class UserSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, nullable=False)
    name_search = db.Column(db.String(300), nullable=False)
    url_search = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    active_notification = db.Column(db.Boolean, default=False, nullable=True)
    active_favorite = db.Column(db.Boolean, default=False, nullable=True)

    def __repr__(self):
          return f"<UserSearch {self.name_search}>"
      
    def json(self):
        return {
            'id': self.id,
            'id_user': self.id_user,
            'name_search': self.name_search,
            'url_search': self.url_search,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'active_notification': self.active_notification,
            'active_favorite': self.active_favorite
        }
      
    def __init__(self, id_user, name_search, url_search, created_at, active_notification=False, active_favorite=False):
        self.id_user = id_user
        self.name_search = name_search
        self.url_search = url_search
        self.created_at = created_at
        self.active_notification = active_notification
        self.active_favorite = active_favorite