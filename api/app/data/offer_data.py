from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.offer import Offer  # Assurez-vous que le modèle Offer est correctement importé
from typing import List, Optional
from app.extensions import db

def get_cards_in_market_count_data() -> int:
    return db.session.query(func.count(Offer.id)).scalar()

def insert_offers_bulk(offers: List[dict]) -> None:
    if not offers:
        return

    try:
        db.session.bulk_insert_mappings(Offer, offers)
        db.session.commit()
        print(f"{len(offers)} offres insérées avec succès.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erreur lors de l'insertion des offres : {e}")


def update_offers_bulk(offers: List[dict]) -> None:
    if not offers:
        return

    try:
        db.session.bulk_update_mappings(Offer, offers)
        db.session.commit()
        print(f"{len(offers)} offres mises à jour avec succès.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erreur lors de la mise à jour des offres : {e}")


def get_offer_by_reference(reference: str) -> Optional[Offer]:
    try:
        return db.session.query(Offer).filter_by(reference=reference).first()
    except Exception as e:
        print(f"Erreur lors de la récupération de l'offre avec la référence {reference} : {e}")
        return None


def get_offer_by_id(offer_id: int) -> Optional[Offer]:
    return db.session.query(Offer).filter_by(id=offer_id).first()


def update_offer_by_reference(reference: str, updates: dict) -> None:
    try:
        db.session.query(Offer).filter_by(reference=reference).update(updates)
        db.session.commit()
        print(f"Offre avec la référence {reference} mise à jour avec succès.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erreur lors de la mise à jour de l'offre avec la référence {reference} : {e}")


def update_offer_by_id(offer_id: int, updates: dict) -> None:
    try:
        db.session.query(Offer).filter_by(id=offer_id).update(updates)
        db.session.commit()
        print(f"Offre avec l'ID {offer_id} mise à jour avec succès.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erreur lors de la mise à jour de l'offre avec l'ID {offer_id} : {e}")


def select_offers_by_reference(reference: str) -> List[Offer]:
    return db.session.query(Offer).filter_by(reference=reference).all()


def select_offers_by_id(offer_id: int) -> List[Offer]:
    return db.session.query(Offer).filter_by(id=offer_id).all()