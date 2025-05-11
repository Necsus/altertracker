from typing import Optional
from app.models.card import Card
from sqlalchemy import func
from app.extensions import db

def get_cards_count_data() -> int:
  return db.session.query(func.count(Card.id)).scalar()

def get_card_by_reference_data(reference) -> Optional[Card]:
  return Card.query.filter_by(reference=reference).first()

def search_cards_data(name, rarity, faction, set, main_effect, echo_effect, main_cost, recall_cost):
  query = Card.query

  if name:
    query = query.filter(Card.name.ilike(f'%{name}%'))

  if rarity:
    query = query.filter(Card.rarity == rarity)

  if faction:
    query = query.filter(Card.faction == faction)

  if set:
    query = query.filter(Card.set == set)

  if main_effect:
    query = query.filter(Card.MAIN_EFFECT.ilike(f'%{main_effect}%'))

  if echo_effect:
    query = query.filter(Card.ECHO_EFFECT.ilike(f'%{echo_effect}%'))

  if main_cost:
    query = query.filter(Card.MAIN_COST == main_cost)

  if recall_cost:
    query = query.filter(Card.RECALL_COST == recall_cost)

  return query.all()
