import datetime
from app.extensions import db

class OfferPurchase(db.Model):
    __tablename__ = 'offers_purchases'

    id = db.Column(db.Integer, primary_key=True)
    reference_card = db.Column(db.String(200))
    id_user = db.Column(db.Integer)
    price = db.Column(db.Float)
    currency = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    is_accepted = db.Column(db.Boolean, default=None)
    accepted_at = db.Column(db.DateTime, default=None)

    def __repr__(self):
        return f"<Card {self.name}>"
        
    def json(self):
        return {
            'id': self.id,
            'reference_card': self.reference_card,
            'id_user': self.id_user,
            'price': self.price,
            'currency': self.currency,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_accepted': self.is_accepted,
            'accepted_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __init__(self, reference_card, id_user, price, currency, created_at, is_accepted=None, accepted_at=None):
        self.reference_card = reference_card
        self.id_user = id_user
        self.price = price
        self.currency = currency
        self.created_at = created_at if created_at else datetime.datetime.now(datetime.timezone.utc)
        self.is_accepted = is_accepted
        self.accepted_at = accepted_at if accepted_at else None
