import re
from typing import Optional
from app.models.offer import Offer
from app.models.card import Card
from sqlalchemy import func
from app.extensions import db

def get_cards_count_data() -> int:
    return db.session.query(func.count(Card.id)).scalar()

def get_card_by_reference_data(reference) -> Optional[Card]:
    return db.session.query(Card).filter_by(reference=reference).first()

def search_cards_data(name, rarity, faction, set, main_effect, echo_effect, main_cost, recall_cost, in_market, no_condition):
    try:
        query = Card.query

        if name:
            query = query.filter(Card.name.ilike(f'%{escape_special_chars(name)}%'))

        if rarity:
            query = query.filter(Card.rarity == rarity)

        if faction:
            query = query.filter(Card.faction == faction)

        if set:
            query = query.filter(Card.set == set)

        if main_effect:
            main_effect = strip(main_effect)
            query = query.filter(Card.MAIN_EFFECT.ilike(f'%{escape_special_chars(main_effect)}%'))

        if echo_effect:
            echo_effect = strip(echo_effect)
            query = query.filter(Card.ECHO_EFFECT.ilike(f'%{escape_special_chars(echo_effect)}%'))

        if main_cost:
            query = query.filter(Card.MAIN_COST == main_cost)

        if recall_cost:
            query = query.filter(Card.RECALL_COST == recall_cost)

        if in_market:
            query = query.filter(Card.price.isnot(None))

        if no_condition:
            query = query.filter(
                ~func.lower(Card.MAIN_EFFECT).like('% si %') &
                ~func.lower(Card.MAIN_EFFECT).like('% s\'il %')
            )

        return query.all()
    except Exception as e:
        print(f"Erreur lors de la recherche des cartes : {e}")
        return []

def insert_cards_bulk(cards: list[dict]) -> None:
    if not cards:
        return

    try:
        db.session.bulk_insert_mappings(Card, cards)
        db.session.commit()
        print(f"{len(cards)} cartes insérées avec succès.")
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de l'insertion des cartes : {e}")

def update_cards_bulk(cards: list[dict]) -> None:
    if not cards:
        return

    try:
        db.session.bulk_update_mappings(Card, cards)
        db.session.commit()
        print(f"{len(cards)} cartes mises à jour avec succès.")
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la mise à jour des cartes : {e}")

def strip(text: str) -> str:
  return text.strip()

def escape_special_chars(text) -> Optional[str]:
    if not text:
        return None
    # Remplacer les caractères spéciaux qui pourraient causer un problème dans SQL
    return re.sub(r'([%#:_{}—])', r'\\\1', text)
