from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.card import Card
from app.models.offer import Offer  # Assurez-vous que le modèle Offer est correctement importé
from typing import List, Optional
from app.extensions import db
from datetime import datetime, timezone

def get_cards_in_market_count_data() -> int:
    return db.session.query(func.count(Offer.id)).filter(Offer.is_deleted == False).scalar()

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


def get_offer_by_reference(reference: str) -> Optional[Offer]:
    try:
        return db.session.query(Offer).filter_by(reference_card=reference).first()
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


def select_offers_by_reference(reference: str) -> List[Offer]:
    return db.session.query(Offer).filter_by(reference=reference).all()


def select_offers_by_id(offer_id: int) -> List[Offer]:
    return db.session.query(Offer).filter_by(id=offer_id).all()

def get_last_added_offers_data() -> list[dict]:
    today_utc = datetime.now(timezone.utc).date()
    return db.session.query(Offer, Card).join(
        Card, Offer.reference_card == Card.reference
    ).filter(
        func.date(Offer.created_at) == today_utc,
        Offer.is_edited == False,
        Offer.is_deleted == False
    )

def get_last_edited_offers_data() -> list[dict]:
    today_utc = datetime.now(timezone.utc).date()
    return db.session.query(Offer, Card).join(
        Card, Offer.reference_card == Card.reference
    ).filter(
        func.date(Offer.edited_at) == today_utc,
        Offer.is_edited == True,
        Offer.is_deleted == False
    )

def get_last_deleted_offers_data() -> list[dict]:
    today_utc = datetime.now(timezone.utc).date()
    return db.session.query(Offer, Card).join(
        Card, Offer.reference_card == Card.reference
    ).filter(
        func.date(Offer.deleted_at) == today_utc,
        Offer.is_deleted == True
    )