from app.extensions import db

class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.String(200), primary_key=True)
    reference = db.Column(db.String(200))
    name = db.Column(db.String(200))
    faction = db.Column(db.String(2))
    rarity = db.Column(db.String(20))
    type = db.Column(db.String(20))
    set = db.Column(db.String(100))
    imagePath = db.Column(db.Text)
    isSuspended = db.Column(db.Boolean, default=False)
    MAIN_COST = db.Column(db.Integer, default=0)
    RECALL_COST = db.Column(db.Integer, default=0)
    MOUNTAIN_POWER = db.Column(db.Integer, default=0)
    OCEAN_POWER = db.Column(db.Integer, default=0)
    FOREST_POWER = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Card {self.name}>"