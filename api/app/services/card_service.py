from typing import List, Optional
from app.models.offer import Offer
from app.models.card import Card
from datetime import datetime
from app.extensions import db
from app.data.card_data import (
  get_card_by_reference_data,
  search_cards_data,
  get_cards_count_data,
  update_cards_bulk_data,
  get_last_added_cards_data
)
from app.data.offer_data import (
  get_last_offer_by_reference_data,
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
    for item in data:
        new_offer = Offer (
            reference_card=item['reference'],
            id_offer=item['offerId'] if item.get('offerId') is not None else None,
            price=item['convertedPrice'] if item.get('convertedPrice') is not None else None,
            currency=item['convertedCurrency'] if item.get('convertedCurrency') is not None else None,
            status=item['status'],
            link_offer=None
        )
        existing_offer = get_last_offer_by_reference_data(new_offer.reference_card)

        # si new_offre est disponible ca veut dire qu'on a un prix
        if new_offer.status == 'available':
            # si il existe une offre et que is_edited = false et que is_deleted = false
            if existing_offer and not existing_offer.is_deleted:
                # c'est que l'offre est l'offre actuelle
                # on test donc le prix
                if existing_offer.price == new_offer.price and existing_offer.id_offer == new_offer.id_offer:
                    # si le prix est le même et l'id de l'offre est le même on test la meme offre donc on passe à la suite
                    continue
                else:
                    # sinon ca veut dire qu'il ya une nouvelle offre
                    # on met à jour l'ancienne offre
                    existing_offer.is_deleted = True
                    existing_offer.deleted_at = datetime.now()
                    existing_offer.status = 'expired'

                    # on prepare la nouvelle offre à etre insérée
                    new_offer.link_offer = f"https://www.altered.gg/fr-fr/cards/{new_offer.reference_card}/offers"
                    new_offer.is_deleted = False
                    new_offer.created_at = datetime.now()
                    new_offer.deleted_at = None
                    new_offer.user_altered = None
                    new_offer.user_id = None
                    new_offer.previous_offer = existing_offer.id
                    print('add offer')
                    db.session.add(new_offer)
                    print('get_card_by_reference_data')
                    card_to_update = get_card_by_reference_data(new_offer.reference_card)
                    if card_to_update:
                        # on met à jour la carte
                        card_to_update.price = new_offer.price
                        card_to_update.price_updated_at = datetime.now()
                        card_to_update.url_offer = new_offer.link_offer
                    # sauvegarde de l'ancienne offre
                    # ajout de la nouvelle en lien de l'ancienne
                    # modification du prix de la carte
                    db.session.commit()
                    continue
            else:
                # on prepare la nouvelle offre à etre insérée
                new_offer.link_offer = f"https://www.altered.gg/fr-fr/cards/{new_offer.reference_card}/offers"
                new_offer.is_deleted = False
                new_offer.created_at = datetime.now()
                new_offer.deleted_at = None
                new_offer.user_altered = None
                new_offer.user_id = None
                if existing_offer:
                  new_offer.previous_offer = existing_offer.id
                print('add offer if not existing_offer or deleted')
                db.session.add(new_offer)

                card_to_update = get_card_by_reference_data(new_offer.reference_card)
                if card_to_update:
                    # on met à jour la carte
                    card_to_update.price = new_offer.price
                    card_to_update.price_updated_at = datetime.now()
                    card_to_update.url_offer = new_offer.link_offer
                # ajout de la nouvelle en lien de l'ancienne
                # modification du prix de la carte
                db.session.commit()
                continue
        else:
            if existing_offer:
                # si l'offre n'est pas disponible et qu'il existe une offre
                # on met à jour l'ancienne offre
                existing_offer.is_deleted = True
                existing_offer.deleted_at = datetime.now()
                existing_offer.status = 'expired'
                print('just delete offer')
                db.session.commit()
        
def get_last_added_cards_service() -> List[dict]:
    return get_last_added_cards_data()