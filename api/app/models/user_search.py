from datetime import datetime
from app.extensions import db


class UserSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, nullable=False)
    name_search = db.Column(db.String(300), nullable=False)
    url_search = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)

    def __repr__(self):
          return f"<UserSearch {self.name_search}>"
      
    def json(self):
        return {
            'id': self.id,
            'id_user': self.id_user,
            'name_search': self.name_search,
            'url_search': self.url_search,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
      
    def __init__(self, id_user, name_search, url_search, created_at):
        self.id_user = id_user
        self.name_search = name_search
        self.url_search = url_search
        self.created_at = created_at