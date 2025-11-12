from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.card import Card
from app.models.offer import Offer
from typing import List, Optional
from app.extensions import db
from datetime import datetime
from pytz import timezone

def get_cards_in_market_count_data() -> int:
    return db.session.query(func.count(Offer.id)).filter(Offer.status == 'available').scalar()

def insert_offers_bulk(offers: List[dict]) -> None:
    if not offers:
        return

    try:
        db.session.bulk_insert_mappings(Offer, offers)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erreur lors de l'insertion des offres : {e}")


def update_offers_bulk(offers: List[dict]) -> None:
    if not offers:
        return

    try:
        db.session.bulk_update_mappings(Offer, offers)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erreur lors de la mise à jour des offres : {e}")


def get_last_offer_by_reference_data(reference: str) -> Optional[Offer]:
    try:
        return db.session.query(Offer).filter_by(reference_card=reference).order_by(Offer.created_at.desc()).first()
    except Exception as e:
        print(f"Erreur lors de la récupération de l'offre avec la référence {reference} : {e}")
        return None


def get_offer_by_id(offer_id: int) -> Optional[Offer]:
    return db.session.query(Offer).filter_by(id=offer_id).first()


def update_offer_by_reference(reference: str, updates: dict) -> None:
    try:
        db.session.query(Offer).filter_by(reference=reference).update(updates)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erreur lors de la mise à jour de l'offre avec la référence {reference} : {e}")


def update_offer_by_id(offer_id: int, updates: dict) -> None:
    try:
        db.session.query(Offer).filter_by(id=offer_id).update(updates)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erreur lors de la mise à jour de l'offre avec l'ID {offer_id} : {e}")


def get_offers_by_reference_data(reference: str) -> List[Offer]:
    return db.session.query(Offer).filter_by(reference_card=reference).order_by(Offer.created_at.desc()).all()


def select_offers_by_id(offer_id: int) -> List[Offer]:
    return db.session.query(Offer).filter_by(id=offer_id).all()

def get_last_added_offers_data() -> list[dict]:
    return db.session.query(Offer, Card).join(
            Card, Offer.reference_card == Card.reference
        ).filter(
            Offer.previous_offer == None,
            Offer.is_deleted == False
        ).order_by(
            Offer.created_at.desc()
        ).limit(10).all()

def get_count_offers_added_today_data() -> int:
    paris_tz = timezone('Europe/Paris')
    today_paris = datetime.now(paris_tz).date()
    today_utc_start = datetime.combine(today_paris, datetime.min.time()).astimezone(timezone('UTC'))
    today_utc_end = datetime.combine(today_paris, datetime.max.time()).astimezone(timezone('UTC'))

    return db.session.query(func.count(Offer.id)).filter(
        Offer.created_at >= today_utc_start,
        Offer.created_at <= today_utc_end,
        Offer.is_deleted == False,
        Offer.previous_offer == None
    ).scalar()

def get_last_edited_offers_data() -> list[dict]:
    try:
        previous_offer_alias = db.aliased(Offer)

        results = db.session.query(
            Offer,
            previous_offer_alias,
            Card
        ).join(
            Card, Offer.reference_card == Card.reference
        ).outerjoin(
            previous_offer_alias, Offer.previous_offer == previous_offer_alias.id
        ).filter(
            Offer.is_deleted == False,
            Offer.previous_offer != None
        ).order_by(
            Offer.created_at.desc()
        ).limit(10).all()

        return [
            {
                "offer": offer.json(),
                "previous_offer": previous_offer.json() if previous_offer else None,
                "card": card.json()
            }
            for offer, previous_offer, card in results
        ]
    except Exception as e:
        print(f"Erreur lors de la récupération des offres éditées : {e}")
        return []
    
def get_count_offers_edited_today_data() -> int:
    paris_tz = timezone('Europe/Paris')
    today_paris = datetime.now(paris_tz).date()
    today_utc_start = datetime.combine(today_paris, datetime.min.time()).astimezone(timezone('UTC'))
    today_utc_end = datetime.combine(today_paris, datetime.max.time()).astimezone(timezone('UTC'))

    return db.session.query(func.count(func.distinct(Offer.reference_card))).filter(
        Offer.created_at >= today_utc_start,
        Offer.created_at <= today_utc_end,
        Offer.status == 'available',
        Offer.is_deleted == False,
        Offer.previous_offer != None
    ).scalar()

def get_last_deleted_offers_data() -> list[dict]:
    try:
        # ✅ Version corrigée : Récupère les offres supprimées qui ne sont pas référencées par d'autres
        # Créer un alias pour la sous-requête
        referring_offers = db.aliased(Offer)
        
        results = db.session.query(Offer, Card).join(
            Card, Offer.reference_card == Card.reference
        ).outerjoin(
            referring_offers,
            referring_offers.previous_offer == Offer.id
        ).filter(
            Offer.is_deleted == True,
            referring_offers.id.is_(None)  # ✅ Aucune offre ne référence celle-ci
        ).order_by(
            Offer.deleted_at.desc()
        ).limit(10).all()

        return [
            {
                "offer": offer.json(),
                "card": card.json()
            }
            for offer, card in results
        ]
    except Exception as e:
        print(f"Erreur lors de la récupération des offres supprimées : {e}")
        return []
    
def get_count_offers_deleted_today_data() -> int:
    paris_tz = timezone('Europe/Paris')
    today_paris = datetime.now(paris_tz).date()
    today_utc_start = datetime.combine(today_paris, datetime.min.time()).astimezone(timezone('UTC'))
    today_utc_end = datetime.combine(today_paris, datetime.max.time()).astimezone(timezone('UTC'))

    # ✅ Sous-requête pour trouver les reference_card qui ont encore des offres disponibles
    available_references = select(Offer.reference_card).where(
        Offer.status == 'available'
    ).distinct().scalar_subquery()

    # ✅ Compter les reference_card uniques supprimées aujourd'hui qui n'ont plus d'offres disponibles
    return db.session.query(func.count(func.distinct(Offer.reference_card))).filter(
        Offer.deleted_at >= today_utc_start,
        Offer.deleted_at <= today_utc_end,
        Offer.is_deleted == True,
        ~Offer.reference_card.in_(available_references)
    ).scalar()