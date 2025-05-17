from app.models.user_search import UserSearch
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError

def get_user_search_data(id_user: int) -> list[dict]:
    return db.session.query(UserSearch).filter_by(id_user=id_user).all()

def save_user_search(data: dict) -> UserSearch:
    try:
        user_search = UserSearch(**data)
        db.session.add(user_search)
        db.session.commit()
        return user_search
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Erreur lors de la sauvegarde de la recherche utilisateur : {str(e)}")

def delete_user_search(id_search: int) -> None:
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

