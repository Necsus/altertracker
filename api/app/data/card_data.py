from typing import Optional
from app.models.card import Card

def get_card_by_reference_data(reference) -> Optional[Card]:
  return Card.query.filter_by(reference=reference).first()

def search_cards_data(name, effect, cost):
  query = Card.query

  if name:
    query = query.filter(Card.name.ilike(f'%{name}%'))

  if effect:
    query = query.filter(Card.MAIN_EFFECT.ilike(f'%{effect}%'))

  if cost:
    query = query.filter(Card.MAIN_COST == cost)

  return query.all()
