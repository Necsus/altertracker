from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.card import Card
from app.models.offer import Offer  # Assurez-vous que le modèle Offer est correctement importé
from typing import List, Optional
from app.extensions import db
from datetime import datetime
from pytz import timezone

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
            Offer.previous_offer == None,  # Inclure uniquement les offres sans previous_offer
            Offer.is_deleted == False  # Exclure les offres supprimées
        ).order_by(
            Offer.created_at.desc()  # Trier par date de création décroissante
        ).limit(10).all()

def get_count_offers_added_today_data() -> int:
    paris_tz = timezone('Europe/Paris')
    today_paris = datetime.now(paris_tz).date()  # Obtenir la date actuelle dans le fuseau de Paris
    today_utc_start = datetime.combine(today_paris, datetime.min.time()).astimezone(timezone('UTC'))
    today_utc_end = datetime.combine(today_paris, datetime.max.time()).astimezone(timezone('UTC'))

    return db.session.query(func.count(Offer.id)).filter(
        Offer.created_at >= today_utc_start,
        Offer.created_at <= today_utc_end,
        Offer.is_deleted == False,
        Offer.previous_offer == None
    ).scalar()

# a revoir avec le 
def get_last_edited_offers_data() -> list[dict]:
    try:
        # Alias pour la jointure avec la previous_offer
        previous_offer_alias = db.aliased(Offer)

        # Requête principale
        results = db.session.query(
            Offer,  # Offre actuelle
            previous_offer_alias,  # Offre précédente
            Card  # Carte de référence
        ).join(
            Card, Offer.reference_card == Card.reference  # Jointure avec la carte
        ).outerjoin(
            previous_offer_alias, Offer.previous_offer == previous_offer_alias.id  # Jointure avec l'offre précédente
        ).filter(
            Offer.is_deleted == False,  # Exclure les offres supprimées
            Offer.previous_offer != None  # Inclure uniquement les offres avec une previous_offer
        ).order_by(
            Offer.created_at.desc()  # Trier par date de création décroissante
        ).limit(10).all()  # Limiter les résultats aux 10 dernières offres

        # Formater les résultats en liste de dictionnaires
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
    today_paris = datetime.now(paris_tz).date()  # Obtenir la date actuelle dans le fuseau de Paris
    today_utc_start = datetime.combine(today_paris, datetime.min.time()).astimezone(timezone('UTC'))
    today_utc_end = datetime.combine(today_paris, datetime.max.time()).astimezone(timezone('UTC'))

    return db.session.query(func.count(Offer.id)).filter(
        Offer.created_at >= today_utc_start,
        Offer.created_at <= today_utc_end,
        Offer.is_deleted == False,
        Offer.previous_offer != None
    ).scalar()

def get_last_deleted_offers_data() -> list[dict]:
    try:
        # Sous-requête pour récupérer les IDs présents dans previous_offer
        subquery = db.session.query(Offer.previous_offer).filter(Offer.previous_offer != None).subquery()
        # Requête principale
        results = db.session.query(Offer, Card).join(
            Card, Offer.reference_card == Card.reference
        ).filter(
            Offer.is_deleted == True,  # Vérifier que l'offre est supprimée
            ~Offer.id.in_(subquery)  # Vérifier que l'ID n'est pas dans previous_offer
        ).order_by(
            Offer.deleted_at.desc()  # Trier par date de suppression décroissante
        ).limit(10).all()  # Limiter les résultats aux 10 dernières offres

        # Formater les résultats en liste de dictionnaires
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
    today_paris = datetime.now(paris_tz).date()  # Obtenir la date actuelle dans le fuseau de Paris
    today_utc_start = datetime.combine(today_paris, datetime.min.time()).astimezone(timezone('UTC'))
    today_utc_end = datetime.combine(today_paris, datetime.max.time()).astimezone(timezone('UTC'))

    return db.session.query(func.count(Offer.id)).filter(
        Offer.deleted_at >= today_utc_start,
        Offer.deleted_at <= today_utc_end,
        Offer.is_deleted == True
    ).scalar()