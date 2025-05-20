import os
from typing import List, Optional
import sib_api_v3_sdk
from app.config import ConfigEnv
from app.utils.emails import render_template_with_data
from app.models.offer import Offer
from app.models.card import Card
from datetime import datetime
from app.extensions import db
from app.extensions import mail_api, ApiException
from app.data.card_data import (
  get_card_by_reference_data,
  search_cards_data,
  get_cards_count_data,
  get_last_added_cards_data
)
from app.data.offer_data import (
  get_last_offer_by_reference_data,
  get_cards_in_market_count_data,
)
from app.data.user_data import (
  get_user_by_id_data,
  get_user_alert_by_reference_card_data
)
import requests

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
            price=item['price'] if item.get('price') is not None else None,
            currency=item['currency'] if item.get('currency') is not None else None,
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
                if existing_offer.id_offer == new_offer.id_offer:
                    # si l'id de l'offre est le même on test la meme offre donc on passe à la suite
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
                    db.session.add(new_offer)
                    card_to_update = get_card_by_reference_data(new_offer.reference_card)
                    if card_to_update:
                        # on met à jour la carte
                        card_to_update.price = new_offer.price
                        card_to_update.price_updated_at = datetime.now()
                        card_to_update.url_offer = new_offer.link_offer
                        card_to_update.price_currency = new_offer.currency
                        send_user_alert(card_to_update, "edited")
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
                db.session.add(new_offer)

                card_to_update = get_card_by_reference_data(new_offer.reference_card)
                if card_to_update:
                    # on met à jour la carte
                    card_to_update.price = new_offer.price
                    card_to_update.price_updated_at = datetime.now()
                    card_to_update.url_offer = new_offer.link_offer
                    card_to_update.price_currency = new_offer.currency
                    send_user_alert(card_to_update, "added")
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

                card_to_update = get_card_by_reference_data(new_offer.reference_card)
                if card_to_update:
                    # on met à jour la carte
                    card_to_update.price = None
                    card_to_update.price_updated_at = datetime.now()
                    card_to_update.price_currency = None
                    card_to_update.url_offer = None
                    send_user_alert(card_to_update, "expired")
                db.session.commit()
        
def get_last_added_cards_service() -> List[dict]:
    return get_last_added_cards_data()

def is_image_url_accessible(url: str) -> bool:
    try:
        response = requests.head(url, timeout=2)
        return response.status_code == 200
    except Exception:
        return False

def send_user_alert(card: Card, type_changement: str):
    alerts = get_user_alert_by_reference_card_data(card.reference)
    for alert in alerts:
        if alert.mail_active:
            user = get_user_by_id_data(alert.id_user)
            if user:
                print(f"{card.price} {card.price_currency}")
                # Vérification de l'image
                image_url = card.imagePath if is_image_url_accessible(card.imagePath) else "/static/img/cardback.webp"
                # Envoi de la notif de modif de prix
                template_path = os.path.join(os.path.dirname(__file__), '../templates/user-alert.html')
                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=[{"email": user.email, "name": user.username}],
                    subject= f"Changement de prix de votre favoris : {card.name}",
                    html_content=render_template_with_data(template_path, {
                        "USERNAME": user.username,
                        "CHANGEMENT_TYPE": type_changement,
                        "NAME_CARD": card.name,
                        "REFERENCE": card.reference,
                        "PRICE": f"{card.price} {card.price_currency}" if card.price and card.price_currency else "N/A",
                        "DATE_EFFECTIVE": card.price_updated_at.strftime("%d/%m/%Y %H:%M"),
                        "URL_IMAGE_CARD": image_url,
                        "LIEN_VERS_ALERTS": f"{ConfigEnv.ANGULAR_URL}/alerts",
                        "YEAR": str(datetime.now().year)
                    }),
                    sender={"name": "AlterTracker", "email": "noreply@altertracker.com"}
                )
                try:
                    response = mail_api.send_transac_email(send_smtp_email)
                    print(response)
                except ApiException as e:
                    print("Exception lors de l'appel à l’API Sendinblue: %s\n" % e)