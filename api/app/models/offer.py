import datetime
from app.extensions import db

class Offer(db.Model):
    __tablename__ = 'offers'

    id = db.Column(db.Integer, primary_key=True)
    reference_card = db.Column(db.String(200))
    id_offer = db.Column(db.String(200))
    price = db.Column(db.Float, default=None)
    currency = db.Column(db.String(20), default=None)
    status = db.Column(db.String(20), default=None)
    link_offer = db.Column(db.Text, default=None)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    deleted_at = db.Column(db.DateTime, default=None)
    user_altered = db.Column(db.Text, default=None)
    user_id = db.Column(db.Integer, default=None)
    previous_offer = db.Column(db.Integer, default=None)

    def __repr__(self):
        return f"<Offer {self.reference_card}>"
    
    def json(self):
        return {
            'id': self.id,
            'reference_card': self.reference_card,
            'id_offer': self.id_offer,
            'price': self.price,
            'currency': self.currency,
            'status': self.status,
            'link_offer': self.link_offer,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'user_altered': self.user_altered,
            'user_id': self.user_id,
            'previous_offer': self.previous_offer
        }
    
    def __init__(self, reference_card, id_offer, price, currency, status, link_offer, is_deleted=None, created_at=None, deleted_at=None, user_altered=None, user_id=None, previous_offer=None):
        self.reference_card = reference_card
        self.id_offer = id_offer
        self.price = price
        self.currency = currency
        self.status = status
        self.link_offer = link_offer
        self.is_deleted = is_deleted
        self.created_at = created_at
        self.deleted_at = deleted_at
        self.user_altered = user_altered
        self.user_id = user_id
        self.previous_offer = previous_offer



