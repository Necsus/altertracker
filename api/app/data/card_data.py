from typing import Optional
from app.models.card import Card


def get_card_by_reference(reference) -> Optional[Card]:
  return Card.query.filter_by(reference=reference).first()
