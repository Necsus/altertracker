from app.data.offer_data import (
  get_last_added_offers_data,
  get_last_edited_offers_data,
  get_last_deleted_offers_data,
  get_count_offers_added_today_data,
  get_count_offers_edited_today_data,
  get_count_offers_deleted_today_data
)

def get_last_added_offers_service():
    return get_last_added_offers_data()

def get_last_edited_offers_service():
    return get_last_edited_offers_data()

def get_last_deleted_offers_service():
    return get_last_deleted_offers_data()

def get_count_offers_added_today_service() -> int:
    return get_count_offers_added_today_data()

def get_count_offers_edited_today_service() -> int:
    return get_count_offers_edited_today_data()

def get_count_offers_deleted_today_service() -> int:
    return get_count_offers_deleted_today_data()