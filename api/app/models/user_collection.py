import datetime
from app.extensions import db


class UserCollection(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, nullable=False)
    reference_card = db.Column(db.String(200), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False)

    def json(self):
        return {
            "id": self.id,
            'id_user': self.id_user,
            'reference_card': self.reference_card,
            'added_at': self.added_at.isoformat() if self.added_at else None,
        }

    def __init__(self, id_user, reference_card, added_at):
        self.id_user = id_user
        self.reference_card = reference_card
        self.added_at = added_at if added_at else datetime.datetime.now(datetime.timezone.utc)