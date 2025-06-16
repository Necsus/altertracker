from app.extensions import db
from sqlalchemy.dialects.postgresql import JSON

class CardEmbedding(db.Model):
    __tablename__ = 'card_embeddings'

    id = db.Column(db.Integer, primary_key=True)
    reference_card = db.Column(db.String(200), unique=True)

    declencheur = db.Column(JSON, nullable=True)
    condition = db.Column(JSON, nullable=True)
    effet = db.Column(JSON, nullable=True)

    main_cost = db.Column(db.Integer, nullable=False)
    reserve_cost = db.Column(db.Integer, nullable=False)
    forest = db.Column(db.Integer, nullable=False)
    mountain = db.Column(db.Integer, nullable=False)
    ocean = db.Column(db.Integer, nullable=False)