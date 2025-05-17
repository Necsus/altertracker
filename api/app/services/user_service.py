from datetime import datetime
from app.data.user_data import (
  get_user_search_data,
  save_user_search,
  delete_user_search,
  get_user_count_data
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
    saved_search = save_user_search(mapped_data)
    return saved_search.json()

def delete_user_search_service(id_search: int) -> None:
    delete_user_search(id_search)