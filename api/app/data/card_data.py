import re
from typing import Optional
from app.models.user_alert import UserAlert
from app.models.card import Card
from sqlalchemy import func
from app.extensions import db
from datetime import datetime, timezone

def get_cards_count_data() -> int:
    return db.session.query(func.count(Card.id)).scalar()

def get_card_by_reference_data(reference) -> Optional[Card]:
    return db.session.query(Card).filter_by(reference=reference).first()

def search_cards_data(name, rarity, faction, set, main_effect, main_effect_2,
    echo_effect, main_cost, recall_cost, forest_power, mountain_power, ocean_power,
    in_market, no_condition, user_id):
    # Vérifier si le nom correspond à la regexp ^ALT_
    if name and re.match(r'^ALT_', name):
        query = db.session.query(Card) if not user_id else db.session.query(
            Card,
            UserAlert.id.label("alert_id")
        )
        
        # Jointure conditionnelle avec UserAlert si l'utilisateur est authentifié
        if user_id:
            query = query.outerjoin(UserAlert, (UserAlert.reference_card == Card.reference) & (UserAlert.id_user == user_id))
        
        # Rechercher directement par référence
        query = query.filter(Card.reference == name)
        
        # Exécution de la requête
        results = query.all()
        
        # Transformation des résultats en JSON
        if user_id:
            return [
                {
                    **card.json(),
                    "alert_id": alert_id
                }
                for card, alert_id in results
            ]
        return [
            card.json()
            for card in results
        ]

    query = db.session.query(Card) if not user_id else db.session.query(
        Card,
        UserAlert.id.label("alert_id")  # Ajoute une colonne booléenne pour indiquer si une alerte est activée
    )

    # Jointure conditionnelle avec UserAlert si l'utilisateur est authentifié
    if user_id:
        query = query.outerjoin(UserAlert, (UserAlert.reference_card == Card.reference) & (UserAlert.id_user == user_id))

    if name:
        name = lower_strip(name)
        query = query.filter(func.lower(Card.name).like(f'%{prepare_like_query(name)}%', escape='\\'))

    if rarity:
        query = query.filter(Card.rarity == rarity)

    if faction:
        query = query.filter(Card.faction == faction)

    if set:
        query = query.filter(Card.set == set)

    if main_effect and not main_effect_2:
        # Si seulement main_effect est fourni
        main_effect = lower_strip(main_effect)
        query = query.filter(func.lower(Card.MAIN_EFFECT).like(f'%{prepare_like_query(main_effect)}%', escape='\\'))

    if main_effect and main_effect_2:
        # Si main_effect et main_effect_2 sont fournis
        main_effect = lower_strip(main_effect)
        main_effect_2 = lower_strip(main_effect_2)
        # Échapper les caractères spéciaux pour la regex
        main_effect_regex = re.escape(main_effect)
        main_effect_2_regex = re.escape(main_effect_2)
        query = query.filter(
            func.lower(Card.MAIN_EFFECT).like(f'%{prepare_like_query(main_effect)}%', escape='\\'),
            func.regexp_replace(func.lower(Card.MAIN_EFFECT), main_effect_regex, '', 1).like(f'%{prepare_like_query(main_effect_2)}%', escape='\\')
        )

    if echo_effect:
        echo_effect = lower_strip(echo_effect)
        query = query.filter(func.lower(Card.ECHO_EFFECT).like(f'%{prepare_like_query(echo_effect)}%', escape='\\'))

    if main_cost:
        query = query.filter(Card.MAIN_COST == main_cost)

    if recall_cost:
        query = query.filter(Card.RECALL_COST == recall_cost)

    if forest_power:
        query = query.filter(Card.FOREST_POWER == forest_power)

    if mountain_power:
        query = query.filter(Card.MOUNTAIN_POWER == mountain_power)

    if ocean_power:
        query = query.filter(Card.OCEAN_POWER == ocean_power)

    if in_market:
        query = query.filter(Card.price.isnot(None))

    if no_condition:
        query = query.filter(
            ~func.lower(Card.MAIN_EFFECT).like('% si %') &
            ~func.lower(Card.MAIN_EFFECT).like('% s\'il %')
        )

    # Exécution de la requête
    results = query.all()

    # Transformation des résultats en JSON
    if user_id:
      return [
          {
              **card.json(),
              "alert_id": alert_id
          }
          for card, alert_id in results
      ]
    return [
        card.json()
        for card in results]

def insert_cards_bulk_data(cards: list[dict]) -> None:
    if not cards:
        return

    try:
        db.session.bulk_insert_mappings(Card, cards)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de l'insertion des cartes : {e}")

def update_cards_bulk_data(cards: list[dict]) -> None:
    if not cards:
        return
    try:
        db.session.bulk_update_mappings(Card, cards)
        db.session.commit()
        print(f"{len(cards)} cartes mises à jour avec succès.")
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la mise à jour des cartes : {e}")


def lower_strip(text: str) -> str:
    return str.lower(text.strip())

def escape_special_chars(text) -> str:
    if not text:
        return None
    # Remplacer les caractères spéciaux qui pourraient causer un problème dans SQL
    return text.replace('#', '\\#') \
          .replace(':', '\\:') \
          .replace('_', '\\_') \
          .replace('{', '\\{') \
          .replace('}', '\\}') \
          .replace('—', '\\—')

def prepare_like_query(text: str) -> str:
    if not text:
        return ""
    text = escape_special_chars(text)
    # Remplacer les espaces insécables par un espace normal
    return text.replace(' ', '_')

def get_count_cards_created_today_data() -> int:
    today_utc = datetime.now(timezone.utc).date()
    return db.session.query(func.count(Card.id)).filter(
        func.date(Card.created_at) == today_utc
    ).scalar()

def get_last_added_cards_data() -> list[dict]:
    return db.session.query(Card).order_by(Card.created_at.desc()).limit(20).all()
