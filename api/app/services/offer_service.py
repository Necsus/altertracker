from app.data.offer_data import (
  get_last_added_offers_data,
  get_last_edited_offers_data,
  get_last_deleted_offers_data
)

def get_last_added_offers_service():
    return get_last_added_offers_data()

def get_last_edited_offers_service():
    return get_last_edited_offers_data()

def get_last_deleted_offers_service():
    return get_last_deleted_offers_data()
