import datetime
from app.extensions import db

class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.String(200), primary_key=True)
    incremental_id = db.Column(db.Integer, autoincrement=True, unique=True, nullable=True)
    reference = db.Column(db.String(200))
    name = db.Column(db.String(200))
    name_en = db.Column(db.String(200), default=None)
    faction = db.Column(db.String(2))
    rarity = db.Column(db.String(20))
    type = db.Column(db.String(20))
    set = db.Column(db.String(100))
    imagePath = db.Column(db.Text)
    isSuspended = db.Column(db.Boolean, default=False)
    MAIN_COST = db.Column(db.Integer, default=0)
    RECALL_COST = db.Column(db.Integer, default=0)
    MOUNTAIN_POWER = db.Column(db.Integer, default=None)
    OCEAN_POWER = db.Column(db.Integer, default=None)
    FOREST_POWER = db.Column(db.Integer, default=None)
    MAIN_EFFECT = db.Column(db.Text, default=None)
    ECHO_EFFECT = db.Column(db.Text, default=None)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    edited_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    price = db.Column(db.Float, default=None)
    price_updated_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    url_offer = db.Column(db.Text, default=None)

    def __repr__(self):
        return f"<Card {self.name}>"
    
    def json(self):
        return {
            'id': self.id,
            'incremental_id': self.incremental_id,
            'reference': self.reference,
            'name': self.name,
            'name_en': self.name_en,
            'faction': self.faction,
            'rarity': self.rarity,
            'type': self.type,
            'set': self.set,
            'imagePath': self.imagePath,
            'isSuspended': self.isSuspended,
            'MAIN_COST': self.MAIN_COST,
            'RECALL_COST': self.RECALL_COST,
            'MOUNTAIN_POWER': self.MOUNTAIN_POWER,
            'OCEAN_POWER': self.OCEAN_POWER,
            'FOREST_POWER': self.FOREST_POWER,
            'MAIN_EFFECT': self.MAIN_EFFECT,
            'ECHO_EFFECT': self.ECHO_EFFECT,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'price': self.price,
            'price_updated_at': self.price_updated_at.isoformat() if self.price_updated_at else None,
            'url_offer': self.url_offer
        }
    
    def __init__(self, id, incremental_id, reference, name, name_en, faction, rarity, type, set, imagePath, isSuspended, MAIN_COST, RECALL_COST, MOUNTAIN_POWER, OCEAN_POWER, FOREST_POWER, MAIN_EFFECT, ECHO_EFFECT, created_at=None, edited_at=None, price=None, price_updated_at=None, url_offer=None):
        self.id = id
        self.incremental_id = incremental_id
        self.reference = reference
        self.name = name
        self.name_en = name_en
        self.faction = faction
        self.rarity = rarity
        self.type = type
        self.set = set
        self.imagePath = imagePath
        self.isSuspended = isSuspended
        self.MAIN_COST = MAIN_COST
        self.RECALL_COST = RECALL_COST
        self.MOUNTAIN_POWER = MOUNTAIN_POWER
        self.OCEAN_POWER = OCEAN_POWER
        self.FOREST_POWER = FOREST_POWER
        self.MAIN_EFFECT = MAIN_EFFECT
        self.ECHO_EFFECT = ECHO_EFFECT
        self.created_at = created_at if created_at else datetime.datetime.now(datetime.timezone.utc)
        self.edited_at = edited_at if edited_at else datetime.datetime.now(datetime.timezone.utc)
        self.price = price
        self.price_updated_at = price_updated_at if price_updated_at else datetime.datetime.now(datetime.timezone.utc)
        self.url_offer = url_offer