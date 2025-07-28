from datetime import datetime, timezone
from typing import List, Dict
from app.data.user_data import (
  get_user_search_data,
  save_user_search_data,
  delete_user_search_data,
  get_user_count_data,
  get_user_alert_data,
  get_user_alert_with_card_data,
  save_user_alert_data,
  delete_user_alert_data,
  edit_user_alert_data,
  put_user_password_data,
  get_user_by_username_data,
  put_user_username_data,
  get_user_by_id_data,
  delete_user_data,
  get_user_collections_data,
  save_user_collections_bulk,
  get_card_is_in_collection_data,
  update_user_search_alerts_data
)

def get_user_by_id_service(id_user: int) -> Dict:
    # Récupère l'utilisateur depuis la base de données
    user = get_user_by_id_data(id_user)
    return user.json() if user else None

def get_user_by_username_service(username: str) -> Dict:
    # Récupère l'utilisateur depuis la base de données
    user = get_user_by_username_data(username)
    # Transformation du résultat en JSON
    return user.json() if user else None

def put_username_service(id_user: int, username: str) -> None:
    # Met à jour le nom d'utilisateur de l'utilisateur
    put_user_username_data(id_user, username)

def put_user_password_service(id_user: int, hashed_password: str) -> None:
    # Met à jour le mot de passe de l'utilisateur
    put_user_password_data(id_user, hashed_password)
    
def delete_user_service(id_user: int) -> None:
    # Supprime l'utilisateur de la base de données
    delete_user_data(id_user)

def get_user_count_services() -> int:
    return get_user_count_data()

def get_user_search_service(id_user: int) -> List[Dict]:
    return [search.json() for search in get_user_search_data(id_user)]

def save_user_search_service(data: Dict) -> Dict:
    mapped_data = {
        "id_user": data.get("id_user"),
        "name_search": data.get("name_search"),
        "url_search": data.get("url_search"),
        "created_at": datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(timezone.utc)
    }
    saved_search = save_user_search_data(mapped_data)
    return saved_search.json()

def delete_user_search_service(id_search: int) -> None:
    delete_user_search_data(id_search)

def get_user_alert_with_card_service(id_user: int) -> List[Dict]:
    # Récupère les alertes utilisateur depuis la base de données
    return get_user_alert_with_card_data(id_user)

def get_user_alert_service(id_user: int) -> List[Dict]:
    # Récupère les alertes utilisateur depuis la base de données
    alerts = get_user_alert_data(id_user)
    
    # Transformation des résultats en JSON
    return [alert.json() for alert in alerts]

def save_user_alert_service(data: Dict) -> Dict:
    mapped_data = {
        "id_user": data.get("id_user"),
        "reference_card": data.get("reference_card"),
        "mail_active": True,
        "created_at": datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(timezone.utc)
    }
    saved_alert = save_user_alert_data(mapped_data)
    return saved_alert.json()

def delete_user_alert_service(id_alert: int) -> None:
    delete_user_alert_data(id_alert)

def edit_user_alert_service(id_alert: int, data: Dict) -> Dict:
    updated_alert = edit_user_alert_data(id_alert, data)
    return updated_alert.json()

def get_user_collections_service(id_user: int) -> List[Dict]:
    return get_user_collections_data(id_user)

def save_user_collections_service(id_user: int, data: List[Dict]) -> None:
    return save_user_collections_bulk(id_user, data)

def get_card_is_in_collection_service(id_user: int, reference: str) -> bool:
    return get_card_is_in_collection_data(id_user, reference)

def update_user_search_alerts_service(data: Dict) -> Dict:
    updated_search = update_user_search_alerts_data(data)
    return updated_search.json()
