import datetime
from typing import Optional
from sqlalchemy import func
from app.models.user_collection import UserCollection
from app.models.card import Card
from app.models.user_alert import UserAlert
from app.models.user import User
from app.models.user_search import UserSearch
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError

def get_user_count_data() -> int:
    return db.session.query(func.count(User.id)).scalar()

def get_user_by_id_data(id_user: int) -> Optional[User]:
    return db.session.query(User).filter_by(id=id_user).first()

def get_user_by_username_data(username: str) -> Optional[User]:
    return db.session.query(User).filter_by(username=username).first()

def put_user_username_data(user_id: int, username: str):
    # Met à jour le nom d'utilisateur de l'utilisateur dans la base de données
    user = db.session.query(User).filter_by(id=user_id).first()
    if user:
        user.username = username
        db.session.commit()

def put_user_password_data(user_id: int, hashed_password: str) -> None:
    # Met à jour le mot de passe de l'utilisateur dans la base de données
    user = db.session.query(User).filter_by(id=user_id).first()
    if user:
        user.password_hash = hashed_password
        db.session.commit()

def delete_user_data(user_id) -> None:
    # Supprime l'utilisateur de la base de données
    user = db.session.query(User).filter_by(id=user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()

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

def get_user_collections_data(id_user: int) -> list[dict]:
    try:
        # Jointure entre UserCollection et Card sur reference_card
        collections = db.session.query(
            UserCollection,
            Card
        ).join(
            Card, UserCollection.reference_card == Card.reference
        ).filter(
            UserCollection.id_user == id_user
        ).all()

        # Transformation des résultats en JSON
        return [
            {
                **collection.json(),
                "card": card.json() if card else None  # Inclut les données de la carte si elle existe
            }
            for collection, card in collections
        ]
    except SQLAlchemyError as e:
        raise Exception(f"Erreur lors de la récupération des collections utilisateur : {str(e)}")

def save_user_collections_bulk(id_user: int, collections: list[str]) -> list[dict]:
    try:
        # Supprimer les collections existantes pour cet utilisateur
        db.session.query(UserCollection).filter_by(id_user=id_user).delete()
        # Préparer les objets UserCollection pour l'insertion
        user_collections = [
            UserCollection(id_user=id_user, reference_card=reference_card, added_at = datetime.datetime.now(datetime.timezone.utc))
            for reference_card in collections
        ]
        # Ajouter les objets à la session
        db.session.bulk_save_objects(user_collections)
        db.session.commit()
        # Récupérer les collections insérées avec les informations des cartes
        inserted_collections = db.session.query(
            UserCollection,
            Card
        ).join(
            Card, UserCollection.reference_card == Card.reference
        ).filter(
            UserCollection.id_user == id_user
        ).all()

        # Transformation des résultats en JSON
        return [
            {
                **collection.json(),
                "card": card.json() if card else None  # Inclut les données de la carte si elle existe
            }
            for collection, card in inserted_collections
        ]
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Erreur lors de la sauvegarde des collections utilisateur : {str(e)}")

