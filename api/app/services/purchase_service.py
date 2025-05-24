from typing import List, Optional
from app.models.offer_purchase import OfferPurchase
from app.data.purchase_data import (
  add_purchase_data,
  delete_purchase_data,
  get_purchases_by_reference_data,
  get_purchases_by_user_data
)

def get_purchases_by_reference_service(reference: str) -> List[dict]:
    return get_purchases_by_reference_data(reference)

def get_purchases_by_user_service(user_id: int) -> List[dict]:
    return get_purchases_by_user_data(user_id)

def add_purchase_offer_service(data: dict) -> Optional[OfferPurchase]:
    return add_purchase_data(data)

def delete_purchase_offer_service(purchase_id: int) -> bool:
    return delete_purchase_data(purchase_id)
