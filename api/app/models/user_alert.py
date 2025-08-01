import datetime
from app.extensions import db


class UserAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, nullable=False)
    id_search = db.Column(db.Integer, nullable=True)
    reference_card = db.Column(db.String(200), nullable=False)
    mail_active = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc), nullable=False)

    def __repr__(self):
          return f"<UserAlert {self.reference_card}>"
      
    def json(self):
        return {
            'id': self.id,
            'id_user': self.id_user,
            'id_search': self.id_search,
            'reference_card': self.reference_card,
            'mail_active': self.mail_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
      
    def __init__(self, id_user, id_search=None, reference_card, mail_active, created_at=None):
        self.id_user = id_user
        self.id_search = id_search
        self.reference_card = reference_card
        self.mail_active = mail_active
        self.created_at = created_at if created_at else datetime.datetime.now(datetime.timezone.utc)