from datetime import datetime
from app.data.user_data import (
  get_user_search_data,
  save_user_search_data,
  delete_user_search_data,
  get_user_count_data,
  get_user_alert_data,
  get_user_alert_with_card_data,
  save_user_alert_data,
  delete_user_alert_data,
  edit_user_alert_data
)

from typing import List, Dict

def get_user_count_services() -> int:
    return get_user_count_data()

def get_user_search_service(id_user: int) -> List[Dict]:
    return [search.json() for search in get_user_search_data(id_user)]

def save_user_search_service(data: Dict) -> Dict:
    mapped_data = {
        "id_user": data.get("id_user"),
        "name_search": data.get("name_search"),
        "url_search": data.get("url_search"),
        "created_at": datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now()
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
        "mail_active": data.get("mail_active", False),
        "created_at": datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now()
    }
    saved_alert = save_user_alert_data(mapped_data)
    return saved_alert.json()



def delete_user_alert_service(id_alert: int) -> None:
    delete_user_alert_data(id_alert)


def edit_user_alert_service(id_alert: int, data: Dict) -> Dict:
    updated_alert = edit_user_alert_data(id_alert, data)
    return updated_alert.json()