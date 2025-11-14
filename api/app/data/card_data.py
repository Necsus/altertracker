import re
from typing import Optional
from app.models.offer import Offer
from app.models.effect import Effect
from app.models.user_alert import UserAlert
from app.models.card import Card
from sqlalchemy import func
from app.extensions import db
from datetime import datetime, timedelta
from pytz import timezone

def get_cards_count_data() -> int:
    return db.session.query(func.count(Card.id)).scalar()

def get_card_by_reference_with_alert_data(reference: str, user_id: int) -> Optional[dict]:
    query = db.session.query(
        Card,
        UserAlert.id.label("alert_id")  # Ajoute l'alert_id si une alerte existe
    ).outerjoin(
        UserAlert, (UserAlert.reference_card == Card.reference) &
        (UserAlert.id_user == user_id) &
        (UserAlert.id_search.is_(None))
    ).filter(
        Card.reference == reference
    )

    result = query.first()

    if result:
        card, alert_id = result
        return {
            **card.json(),
            "alert_id": alert_id
        }
    return None

def get_card_by_reference_data(reference: str) -> Optional[dict]:
    return db.session.query(Card).filter_by(reference=reference).first()

def search_cards_data(name, rarity, faction, set, subtype, main_effect, main_effect_2, echo_effect, exclude_effect,
    main_cost_range, recall_cost_range, forest_power_range, mountain_power_range, ocean_power_range, zero_power,
    no_condition, in_market, price_range, en, dataset_type, user_id):
    # Vérifier si le nom correspond à la regexp ^ALT_
    if name and re.match(r'^ALT_', name):
        query = db.session.query(Card) if not user_id else db.session.query(
            Card,
            UserAlert.id.label("alert_id")
        )
        
        # Jointure conditionnelle avec UserAlert si l'utilisateur est authentifié
        if user_id:
            query = query.outerjoin(UserAlert,
                                    (UserAlert.reference_card == Card.reference) &
                                    (UserAlert.id_user == user_id) &
                                    (UserAlert.id_search.is_(None)))
        
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

    # Filtrer sur les cartes créées aujourd'hui si demandé
    if dataset_type == "new_cards":
        paris_tz = timezone('Europe/Paris')
        today_paris = datetime.now(paris_tz).date()
        today_utc_start = datetime.combine(today_paris, datetime.min.time()).astimezone(timezone('UTC'))
        today_utc_end = datetime.combine(today_paris, datetime.max.time()).astimezone(timezone('UTC'))
        query = query.filter(
            Card.created_at >= today_utc_start,
            Card.created_at <= today_utc_end
        )

    if dataset_type == "new_offers":
        paris_tz = timezone('Europe/Paris')
        today_paris = datetime.now(paris_tz).date()
        today_utc_start = datetime.combine(today_paris, datetime.min.time()).astimezone(timezone('UTC'))
        today_utc_end = datetime.combine(today_paris, datetime.max.time()).astimezone(timezone('UTC'))
        # Filtrer les cartes qui ont AU MOINS une offre ajoutée aujourd'hui (non supprimée, sans previous_offer)
        query = query.join(
            Offer, Offer.reference_card == Card.reference
        ).filter(
            Offer.created_at >= today_utc_start,
            Offer.created_at <= today_utc_end,
            Offer.is_deleted == False,
            Offer.previous_offer == None
        )

    if dataset_type == "edit_offers":
        paris_tz = timezone('Europe/Paris')
        today_paris = datetime.now(paris_tz).date()
        today_utc_start = datetime.combine(today_paris, datetime.min.time()).astimezone(timezone('UTC'))
        today_utc_end = datetime.combine(today_paris, datetime.max.time()).astimezone(timezone('UTC'))
        query = query.join(
            Offer, Offer.reference_card == Card.reference
        ).filter(
            Offer.created_at >= today_utc_start,
            Offer.created_at <= today_utc_end,
            Offer.status == 'available',  # Filtrer les offres disponibles
            Offer.is_deleted == False,
            Offer.previous_offer != None
        )

    if dataset_type == "deleted_offers":
        paris_tz = timezone('Europe/Paris')
        today_paris = datetime.now(paris_tz).date()
        today_utc_start = datetime.combine(today_paris, datetime.min.time()).astimezone(timezone('UTC'))
        today_utc_end = datetime.combine(today_paris, datetime.max.time()).astimezone(timezone('UTC'))
        # Sous-requête pour récupérer les IDs présents dans previous_offer
        available_subq = db.session.query(Offer.reference_card).filter(Offer.status == 'available').subquery()
        query = query.join(
            Offer, Offer.reference_card == Card.reference
        ).filter(
            Offer.deleted_at >= today_utc_start,
            Offer.deleted_at <= today_utc_end,
            Offer.is_deleted == True,
            ~Offer.reference_card.in_(available_subq)
        )

    # Jointure conditionnelle avec UserAlert si l'utilisateur est authentifié
    if user_id:
        query = query.outerjoin(UserAlert,
                                (UserAlert.reference_card == Card.reference) &
                                (UserAlert.id_user == user_id) &
                                (UserAlert.id_search.is_(None)))

    # Utiliser les colonnes en anglais si en=True
    name_column = Card.name_en if en else Card.name
    main_effect_column = Card.main_effect_en if en else Card.MAIN_EFFECT
    echo_effect_column = Card.echo_effect_en if en else Card.ECHO_EFFECT

    if name:
        name = lower_strip(name)
        query = query.filter(func.lower(name_column).like(f'%{prepare_like_query(name)}%', escape='\\'))

    if rarity:
        if isinstance(rarity, str):
            rarity_list = [r.strip() for r in rarity.split(',') if r.strip()]
            query = query.filter(Card.rarity.in_(rarity_list))
        elif isinstance(rarity, list):
            query = query.filter(Card.rarity.in_(rarity))
        else:
            query = query.filter(Card.rarity == rarity)

    if faction:
        if isinstance(faction, str):
            faction_list = [f.strip() for f in faction.split(',') if f.strip()]
            query = query.filter(Card.faction.in_(faction_list))
        elif isinstance(faction, list):
            query = query.filter(Card.faction.in_(faction))
        else:
            query = query.filter(Card.faction == faction)

    if set:
        query = query.filter(Card.set == set)

    if subtype:
        query = query.filter(
            func.concat(',', Card.subtype, ',').like(f'%,{subtype},%')
        )

    if main_effect and not main_effect_2:
        # Si seulement main_effect est fourni
        main_effect = lower_strip(main_effect)
        query = query.filter(func.lower(main_effect_column).like(f'%{prepare_like_query(main_effect)}%', escape='\\'))

    if main_effect and main_effect_2:
        # Si main_effect et main_effect_2 sont fournis
        main_effect = lower_strip(main_effect)
        main_effect_2 = lower_strip(main_effect_2)
        # Échapper les caractères spéciaux pour la regex
        main_effect_regex = re.escape(main_effect)
        main_effect_2_regex = re.escape(main_effect_2)
        query = query.filter(
            func.lower(main_effect_column).like(f'%{prepare_like_query(main_effect)}%', escape='\\'),
            func.regexp_replace(func.lower(main_effect_column), main_effect_regex, '', 1).like(f'%{prepare_like_query(main_effect_2)}%', escape='\\')
        )

    if exclude_effect:
        # Si exclude_effect est fourni, on l'utilise pour exclure les cartes
        # Supporter plusieurs termes séparés par des virgules
        exclude_terms = [term.strip() for term in exclude_effect.split(',') if term.strip()]
        
        for term in exclude_terms:
            term = lower_strip(term)
            query = query.filter(~func.lower(main_effect_column).like(f'%{prepare_like_query(term)}%', escape='\\'))

    if echo_effect:
        echo_effect = lower_strip(echo_effect)
        query = query.filter(func.lower(echo_effect_column).like(f'%{prepare_like_query(echo_effect)}%', escape='\\'))

    # Recherche par plage pour main_cost
    if main_cost_range:
        if 'min' in main_cost_range and 'max' in main_cost_range and main_cost_range['min'] == main_cost_range['max']:
            query = query.filter(Card.MAIN_COST == main_cost_range['min'])
        if 'min' in main_cost_range:
            query = query.filter(Card.MAIN_COST >= main_cost_range['min'])
        if 'max' in main_cost_range:
            query = query.filter(Card.MAIN_COST <= main_cost_range['max'])

    # Recherche par plage pour recall_cost
    if recall_cost_range:
        if 'min' in recall_cost_range and 'max' in recall_cost_range and recall_cost_range['min'] == recall_cost_range['max']:
            query = query.filter(Card.RECALL_COST == recall_cost_range['min'])
        else:
            if 'min' in recall_cost_range:
                query = query.filter(Card.RECALL_COST >= recall_cost_range['min'])
            if 'max' in recall_cost_range:
                query = query.filter(Card.RECALL_COST <= recall_cost_range['max'])

    # Recherche par plage pour forest_power
    if forest_power_range and zero_power is not True:
        if 'min' in forest_power_range and 'max' in forest_power_range and forest_power_range['min'] == forest_power_range['max']:
            query = query.filter(Card.FOREST_POWER == forest_power_range['min'])
        else:
            if 'min' in forest_power_range:
                query = query.filter(Card.FOREST_POWER >= forest_power_range['min'])
            if 'max' in forest_power_range:
                query = query.filter(Card.FOREST_POWER <= forest_power_range['max'])

    # Recherche par plage pour mountain_power
    if mountain_power_range and zero_power is not True:
        if 'min' in mountain_power_range and 'max' in mountain_power_range and mountain_power_range['min'] == mountain_power_range['max']:
            query = query.filter(Card.MOUNTAIN_POWER == mountain_power_range['min'])
        else:
            if 'min' in mountain_power_range:
                query = query.filter(Card.MOUNTAIN_POWER >= mountain_power_range['min'])
            if 'max' in mountain_power_range:
                query = query.filter(Card.MOUNTAIN_POWER <= mountain_power_range['max'])

    # Recherche par plage pour ocean_power
    if ocean_power_range and zero_power is not True:
        if 'min' in ocean_power_range and 'max' in ocean_power_range and ocean_power_range['min'] == ocean_power_range['max']:
            query = query.filter(Card.OCEAN_POWER == ocean_power_range['min'])
        else:
            if 'min' in ocean_power_range:
                query = query.filter(Card.OCEAN_POWER >= ocean_power_range['min'])
            if 'max' in ocean_power_range:
                query = query.filter(Card.OCEAN_POWER <= ocean_power_range['max'])
    
    if zero_power is True:
        query = query.filter(
            (Card.FOREST_POWER == 0) | 
            (Card.MOUNTAIN_POWER == 0) | 
            (Card.OCEAN_POWER == 0)
        )

    if in_market:
        query = query.filter(Card.price.isnot(None))
        if price_range:
            if 'min' in price_range and 'max' in price_range and price_range['min'] == price_range['max']:
                query = query.filter(Card.price == price_range['min'])
            else:
                if 'min' in price_range:
                    query = query.filter(Card.price >= price_range['min'])
                if 'max' in price_range:
                    query = query.filter(Card.price <= price_range['max'])

    if no_condition:
        if not en:
            query = query.filter(
                ~func.lower(Card.MAIN_EFFECT).like('% si %') &
                ~func.lower(Card.MAIN_EFFECT).like('% s\'il %')
            )
        else:
            query = query.filter(
                ~func.lower(Card.MAIN_EFFECT).like('% if %') &
                ~func.lower(Card.MAIN_EFFECT).like('% when %')
            )

    # Limiter à 10 000 résultats
    query = query.limit(10000)

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

def update_card_data(card: dict) -> None:
    if not card:
        return
    try:
        existing_card = db.session.query(Card).filter_by(reference=card.get('reference')).first()
        if existing_card:
            for key, value in card.items():
                if key == 'image_path_en':
                    if 'en_EN' in getattr(existing_card, key, None):
                        setattr(existing_card, key, value)
                if getattr(existing_card, key, None) is None:
                    setattr(existing_card, key, value)
            db.session.commit()
        else:
            print(f"Carte avec la référence {card['reference']} introuvable.")
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la mise à jour de la carte : {e}")


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
    paris_tz = timezone('Europe/Paris')
    # Obtenir la date actuelle dans le fuseau horaire de Paris
    today_paris = datetime.now(paris_tz).date()
    # Convertir la date de Paris en UTC pour la comparaison avec les données stockées
    today_utc_start = datetime.combine(today_paris, datetime.min.time()).astimezone(timezone('UTC'))
    today_utc_end = datetime.combine(today_paris, datetime.max.time()).astimezone(timezone('UTC'))

    # Filtrer les cartes créées aujourd'hui en UTC
    return db.session.query(func.count(Card.id)).filter(
        Card.created_at >= today_utc_start,
        Card.created_at <= today_utc_end
    ).scalar()

def get_last_added_cards_data() -> list[dict]:
    paris_tz = timezone('Europe/Paris')
    today_paris = datetime.now(paris_tz).date()
    today_utc_start = datetime.combine(today_paris, datetime.min.time()).astimezone(timezone('UTC'))
    today_utc_end = datetime.combine(today_paris, datetime.max.time()).astimezone(timezone('UTC'))
    
    # Essayer d'abord avec les cartes d'aujourd'hui
    today_cards = db.session.query(Card).filter(
        Card.created_at >= today_utc_start,
        Card.created_at <= today_utc_end
    ).order_by(func.random()).limit(10).all()
    
    # Si on a des cartes aujourd'hui, les retourner
    if today_cards:
        return today_cards
    
    # Sinon, prendre celles de la veille
    yesterday_paris = today_paris - timedelta(days=1)
    yesterday_utc_start = datetime.combine(yesterday_paris, datetime.min.time()).astimezone(timezone('UTC'))
    yesterday_utc_end = datetime.combine(yesterday_paris, datetime.max.time()).astimezone(timezone('UTC'))
    
    yesterday_cards = db.session.query(Card).filter(
        Card.created_at >= yesterday_utc_start,
        Card.created_at <= yesterday_utc_end
    ).order_by(func.random()).limit(10).all()
    
    return yesterday_cards

def get_effect_data(lang: str) -> list[dict]:
    return db.session.query(Effect).filter(Effect.language == lang).all()

def get_cards_batch_data(references: list[str]) -> list[dict]:
    """
    Récupère plusieurs cartes en une seule requête optimisée
    Retourne uniquement les données essentielles pour l'affichage
    """
    cards = db.session.query(Card).filter(Card.reference.in_(references)).all()
    return [
        {
            'reference': card.reference,
            'imagePath': card.imagePath,
            'name': card.name,
            'name_en': card.name_en,
            'rarity': card.rarity
        }
        for card in cards
    ]