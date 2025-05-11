from typing import Optional
from app.models.card import Card
from app.data.card_data import (
  get_card_by_reference_data,
  search_cards_data
)

def get_card_by_reference_service(reference) -> Optional[Card]:
    return get_card_by_reference_data(reference)

def search_cards_service(name, faction, set, main_effect, echo_effect, main_cost, recall_cost) -> Optional[list[Card]]:
    return search_cards_data(name, faction, set, main_effect, echo_effect, main_cost, recall_cost)