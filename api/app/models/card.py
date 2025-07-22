import datetime
from app.extensions import db

class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    id_card = db.Column(db.String(200))
    reference = db.Column(db.String(200))
    name = db.Column(db.String(200))
    name_en = db.Column(db.String(200), default=None)
    faction = db.Column(db.String(2))
    rarity = db.Column(db.String(20))
    type = db.Column(db.String(20))
    subtype = db.Column(db.String(80))
    set = db.Column(db.String(100))
    imagePath = db.Column(db.Text)
    image_path_en = db.Column(db.Text, default=None)
    isSuspended = db.Column(db.Boolean, default=False)
    MAIN_COST = db.Column(db.Integer, default=0)
    RECALL_COST = db.Column(db.Integer, default=0)
    MOUNTAIN_POWER = db.Column(db.Integer, default=None)
    OCEAN_POWER = db.Column(db.Integer, default=None)
    FOREST_POWER = db.Column(db.Integer, default=None)
    MAIN_EFFECT = db.Column(db.Text, default=None)
    main_effect_en = db.Column(db.Text, default=None)
    ECHO_EFFECT = db.Column(db.Text, default=None)
    echo_effect_en = db.Column(db.Text, default=None)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    edited_at = db.Column(db.DateTime, default=None)
    price = db.Column(db.Float, default=None)
    price_currency = db.Column(db.String(10), default=None)
    price_updated_at = db.Column(db.DateTime, default=None)
    url_offer = db.Column(db.Text, default=None)

    def __repr__(self):
        return f"<Card {self.name}>"
    
    def json(self):
        return {
            'id': self.id,
            'id_card': self.id_card,
            'reference': self.reference,
            'name': self.name,
            'name_en': self.name_en,
            'faction': self.faction,
            'rarity': self.rarity,
            'type': self.type,
            'subtype': self.subtype,
            'set': self.set,
            'imagePath': self.imagePath,
            'image_path_en': self.image_path_en,
            'isSuspended': self.isSuspended,
            'MAIN_COST': self.MAIN_COST,
            'RECALL_COST': self.RECALL_COST,
            'MOUNTAIN_POWER': self.MOUNTAIN_POWER,
            'OCEAN_POWER': self.OCEAN_POWER,
            'FOREST_POWER': self.FOREST_POWER,
            'MAIN_EFFECT': self.MAIN_EFFECT,
            'main_effect_en': self.main_effect_en,
            'ECHO_EFFECT': self.ECHO_EFFECT,
            'echo_effect_en': self.echo_effect_en,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'price': self.price,
            'price_currency': self.price_currency,
            'price_updated_at': self.price_updated_at.isoformat() if self.price_updated_at else None,
            'url_offer': self.url_offer
        }
    
    def __init__(self, id_card, reference, name, name_en, faction, rarity, type, subtype, set, imagePath,
                image_path_en, isSuspended, MAIN_COST, RECALL_COST, MOUNTAIN_POWER, OCEAN_POWER, FOREST_POWER,
                MAIN_EFFECT, main_effect_en, ECHO_EFFECT, echo_effect_en, created_at=None, edited_at=None,
                price=None, price_currency=None, price_updated_at=None, url_offer=None):
        self.id_card = id_card
        self.reference = reference
        self.name = name
        self.name_en = name_en
        self.faction = faction
        self.rarity = rarity
        self.type = type
        self.subtype = subtype
        self.set = set
        self.imagePath = imagePath
        self.image_path_en = image_path_en
        self.isSuspended = isSuspended
        self.MAIN_COST = MAIN_COST
        self.RECALL_COST = RECALL_COST
        self.MOUNTAIN_POWER = MOUNTAIN_POWER
        self.OCEAN_POWER = OCEAN_POWER
        self.FOREST_POWER = FOREST_POWER
        self.MAIN_EFFECT = MAIN_EFFECT
        self.main_effect_en = main_effect_en
        self.ECHO_EFFECT = ECHO_EFFECT
        self.echo_effect_en = echo_effect_en
        self.created_at = created_at if created_at else datetime.datetime.now(datetime.timezone.utc)
        self.edited_at = edited_at if edited_at else datetime.datetime.now(datetime.timezone.utc)
        self.price = price
        self.price_currency = price_currency
        self.price_updated_at = price_updated_at if price_updated_at else datetime.datetime.now(datetime.timezone.utc)
        self.url_offer = url_offer
