import datetime
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from app.models.user_alert import UserAlert
from app.models.card import Card
from app.models.user import User
from app.extensions import db
from app.models.offer_purchase import OfferPurchase

def get_purchases_by_reference_data(reference: str) -> List[dict]:
    purchases = db.session.query(OfferPurchase).filter(
        OfferPurchase.reference_card == reference
    ).order_by(
        OfferPurchase.price.desc()  # Trier par prix descendant
    ).all()
    
    return [
        purchase.json()  # Retourner uniquement les données de l'offre d'achat
        for purchase in purchases
    ] if purchases else []

def get_purchases_by_user_data(user_id: int) -> List[dict]:
    purchases = db.session.query(
        OfferPurchase,
        Card,
        UserAlert.id.label("alert_id")
    ).join(
        Card, OfferPurchase.reference_card == Card.reference
    ).outerjoin(
        UserAlert, (UserAlert.reference_card == Card.reference) &
        (UserAlert.id_user == user_id) &
        (UserAlert.id_search.is_(None))
    ).filter(
        OfferPurchase.id_user == user_id
    ).order_by(
        OfferPurchase.created_at.desc()
    ).all()

    # Grouper les achats par carte
    cards_dict = {}
    for purchase, card, alert_id in purchases:
        ref = card.reference
        if ref not in cards_dict:
            cards_dict[ref] = {
                **card.json(), 
                "alert_id": alert_id,  # Ajouter l'alert_id à la carte
                "mine_purchase_offers": []
            }
        cards_dict[ref]["mine_purchase_offers"].append(purchase.json())

    return list(cards_dict.values())

def add_purchase_data(data: dict) -> Optional[OfferPurchase]:
    try:
        # Récupérer le username de l'utilisateur
        user = db.session.query(User).filter_by(id=data["id_user"]).first()
        if not user:
            print(f"Utilisateur avec l'ID {data['id_user']} introuvable.")
            return None
        data["created_at"] = data.get("created_at", datetime.datetime.now(datetime.timezone.utc))
        new_purchase = OfferPurchase(**data)
        db.session.add(new_purchase)
        db.session.commit()
        return {
            **new_purchase.json(),
            "username": user.username
        }
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erreur lors de l'ajout de l'offre d'achat : {e}")
        return None

def delete_purchase_data(purchase_id: int) -> bool:
    try:
        purchase = db.session.query(OfferPurchase).filter_by(id=purchase_id).first()
        if purchase:
            db.session.delete(purchase)
            db.session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erreur lors de la suppression de l'offre d'achat : {e}")
        return False

