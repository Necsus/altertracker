from typing import List, Optional
from app.models.card import Card
from datetime import datetime
from app.data.card_data import (
  get_card_by_reference_data,
  search_cards_data,
  get_cards_count_data,
  update_cards_bulk_data,
  get_last_added_cards_data
)
from app.data.offer_data import (
  get_offer_by_reference,
  update_offers_bulk,
  insert_offers_bulk,
  get_cards_in_market_count_data,
)

def get_cards_count_service() -> int:
    return get_cards_count_data()

def get_cards_in_market_count_service() -> int:
    return get_cards_in_market_count_data()

def get_card_by_reference_service(reference) -> Optional[Card]:
    return get_card_by_reference_data(reference)

def search_cards_service(name, rarity, faction, set, main_effect, main_effect_2,
    echo_effect, main_cost, recall_cost, forest_cost, mountain_cost, ocean_cost,
    in_market, no_condition, user_id) -> List[dict]:
    return search_cards_data(name, rarity, faction, set, main_effect, main_effect_2,
        echo_effect, main_cost, recall_cost, forest_cost, mountain_cost, ocean_cost,
        in_market, no_condition, user_id)

def post_offer_live_market_service(data: List[dict]) -> None:
    # Vérification des données reçues
    if not isinstance(data, list) or not data:
        raise ValueError("Les données doivent être une liste non vide.")

    # Champs obligatoires définis dans OfferLiveMarketRequest
    required_fields = {'id', 'reference', 'status'}

    # Préparer les données pour la mise à jour
    sanitized_data = []
    new_offers = []
    updated_offers = []

    for item in data:
        # Vérification des champs obligatoires
        missing_fields = required_fields - item.keys()
        if missing_fields:
            raise ValueError(f"Champs manquants dans l'élément : {', '.join(missing_fields)}")

        # Validation et sanitization des données
        sanitized_item = {
            "reference": str(item['reference']).strip(),
            "price": float(item['convertedPrice']) if item.get('convertedPrice') is not None else None,
            "price_updated_at": datetime.now(),
            "url_offer": f"https://www.altered.gg/fr-fr/cards/{item['reference']}/offers" if item['status'] == "available" else None
        }
        sanitized_data.append(sanitized_item)
        if item['status'] == 'available' and sanitized_item['price'] is not None and item['offerId'] is not None:
            existing_offer = get_offer_by_reference(sanitized_item['reference'])
            if existing_offer:
                if existing_offer.id == item['offerId']:
                    continue
                else:
                    updated_offers.append({
                        "id": existing_offer.id,
                        "is_edited": True,
                        "edited_at": datetime.now()
                    })
            # Insérer une nouvelle offre pour conserver l'historique
            new_offers.append({
                "reference_card": sanitized_item['reference'],
                "id_offer": str(item['offerId']) if item.get('offerId') is not None else None,
                "price": sanitized_item['price'],
                "currency": str(item['convertedCurrency']) if item.get('convertedCurrency') is not None else None,
                "quantity": int(item['quantity']) if item.get('quantity') is not None else None,
                "status": str(item['status']),
                "link_offer": sanitized_item['url_offer'],
                "created_at": datetime.now(),
            })
        else:
            existing_offer = get_offer_by_reference(sanitized_item['reference'])
            if existing_offer:
                updated_offers.append({
                    "id": existing_offer.id,
                    "is_deleted": True,
                    "delelted_at": datetime.now(),
                    "status": 'expired'
                })

    # Mise à jour en masse des cartes
    try:
        update_cards_bulk_data(sanitized_data)
    except Exception as e:
        print(f"Erreur lors de la mise à jour des cartes : {e}")
        raise
    
    # Mise à jour des offres existantes
    if updated_offers:
        try:
            update_offers_bulk(updated_offers)
        except Exception as e:
            print(f"Erreur lors de la mise à jour des offres : {e}")
            raise

    # Insertion des nouvelles offres
    if new_offers:
        try:
            insert_offers_bulk(new_offers)
        except Exception as e:
            print(f"Erreur lors de l'insertion des nouvelles offres : {e}")
            raise
        
def get_last_added_cards_service() -> List[dict]:
    return get_last_added_cards_data()