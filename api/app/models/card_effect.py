from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index
from app.extensions import db
import datetime

class CardEffect(db.Model):
    __tablename__ = 'card_effects'
    
    id = Column(Integer, primary_key=True)
    reference_card = Column(String(50), nullable=False, index=True)
    
    # JSON minimal pour requêtage - liste d'effets parsés
    parsed_fr = Column(JSON)  # Array d'objets effect en français
    parsed_en = Column(JSON)  # Array d'objets effect en anglais
    
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    
    def __repr__(self):
        return f"<CardEffect(reference_card='{self.reference_card}')>"

# Index pour optimiser les requêtes fréquentes

# Index basiques
Index('idx_card_effects_reference', CardEffect.reference_card)