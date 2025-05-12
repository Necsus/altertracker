from typing import Optional
from app.models.card import Card
from app.data.card_data import (
  get_card_by_reference_data,
  search_cards_data,
  get_cards_count_data,
  get_cards_in_market_count_data
)

def get_cards_count_service() -> int:
    return get_cards_count_data()

def get_cards_in_market_count_service() -> int:
    return get_cards_in_market_count_data()

def get_card_by_reference_service(reference) -> Optional[Card]:
    return get_card_by_reference_data(reference)

def search_cards_service(name, rarity, faction, set, main_effect, echo_effect, main_cost, recall_cost, in_market, no_condition) -> Optional[list[Card]]:
    return search_cards_data(name, rarity, faction, set, main_effect, echo_effect, main_cost, recall_cost, in_market, no_condition)