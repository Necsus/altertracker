from sqlalchemy import func
from app.models.card import Card
from app.models.user_alert import UserAlert
from app.models.user import User
from app.models.user_search import UserSearch
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError

def get_user_count_data() -> int:
    return db.session.query(func.count(User.id)).scalar()

def get_user_by_id_data(id_user: int) -> User:
    user = db.session.query(User).filter_by(id=id_user).first()
    if not user:
        raise Exception(f"Aucun utilisateur trouvé avec l'ID {id_user}")
    return user

def get_user_search_data(id_user: int) -> list[dict]:
    return db.session.query(UserSearch).filter_by(id_user=id_user).order_by(UserSearch.created_at.desc()).all()

def save_user_search_data(data: dict) -> UserSearch:
    try:
        user_search = UserSearch(**data)
        db.session.add(user_search)
        db.session.commit()
        return user_search
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Erreur lors de la sauvegarde de la recherche utilisateur : {str(e)}")

def delete_user_search_data(id_search: int) -> None:
    try:
        user_search = db.session.query(UserSearch).filter_by(id=id_search).first()
        if user_search:
            db.session.delete(user_search)
            db.session.commit()
        else:
            raise Exception(f"Aucune recherche trouvée avec l'ID {id_search}")
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Erreur lors de la suppression de la recherche utilisateur : {str(e)}")
    
def get_user_alert_data(id_user: int) -> list[dict]:
    return db.session.query(UserAlert).filter_by(id_user=id_user).all()

def get_user_alert_by_reference_card_data(reference_card: str) -> list[dict]:
    return db.session.query(UserAlert).filter_by(reference_card=reference_card).all()

def get_user_alert_with_card_data(id_user: int) -> list[dict]:
    try:
        # Jointure entre UserAlert et Card sur reference_card
        alerts = db.session.query(
            UserAlert,
            Card
        ).join(
            Card, UserAlert.reference_card == Card.reference
        ).filter(
            UserAlert.id_user == id_user
        ).order_by(UserAlert.created_at.desc()).all()

        # Transformation des résultats en JSON
        return [
            {
                **alert.json(),
                "card": card.json() if card else None  # Inclut les données de la carte si elle existe
            }
            for alert, card in alerts
        ]
    except SQLAlchemyError as e:
        raise Exception(f"Erreur lors de la récupération des alertes utilisateur : {str(e)}")

def save_user_alert_data(data: dict) -> UserAlert:
    try:
        user_alert = UserAlert(**data)
        db.session.add(user_alert)
        db.session.commit()
        return user_alert
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Erreur lors de la sauvegarde de l'alerte utilisateur : {str(e)}")

def delete_user_alert_data(id_alert: int) -> None:
    try:
        user_alert = db.session.query(UserAlert).filter_by(id=id_alert).first()
        if user_alert:
            db.session.delete(user_alert)
            db.session.commit()
        else:
            raise Exception(f"Aucune alerte trouvée avec l'ID {id_alert}")
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Erreur lors de la suppression de l'alerte utilisateur : {str(e)}")

def edit_user_alert_data(id_alert: int, data: dict) -> UserAlert:
    try:
        user_alert = db.session.query(UserAlert).filter_by(id=id_alert).first()
        if not user_alert:
            raise Exception(f"Aucune alerte trouvée avec l'ID {id_alert}")
        
        # Mise à jour des champs
        for key, value in data.items():
            if hasattr(user_alert, key):
                setattr(user_alert, key, value)
            else:
                raise Exception(f"Le champ '{key}' n'existe pas sur le modèle UserAlert")
        
        db.session.commit()
        return user_alert
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Erreur lors de la modification de l'alerte utilisateur : {str(e)}")

