import os
from typing import List, Optional
import sib_api_v3_sdk
from app.models.user import User
from app.config import ConfigEnv
from app.utils.emails import render_template_with_data
from app.models.offer import Offer
from app.models.card import Card
from datetime import datetime, timezone
from app.extensions import db, mail_api, ApiException, socketio
from app.data.card_data import (
  get_card_by_reference_data,
  get_effect_data,
  search_cards_data,
  get_cards_count_data,
  get_last_added_cards_data,
  get_count_cards_created_today_data,
  get_card_by_reference_with_alert_data,
  update_card_data
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

def get_card_by_reference_with_alert_service(reference: str, user_id: int) -> Optional[Card]:
    return get_card_by_reference_with_alert_data(reference, user_id)

def get_card_by_reference_service(reference: str) -> Optional[Card]:
    return get_card_by_reference_data(reference)

def search_cards_service(name, rarity, faction, set, main_effect, main_effect_2, echo_effect, exclude_effect, main_cost_range, recall_cost_range,
    forest_cost_range, mountain_cost_range, ocean_cost_range, no_condition,
    in_market, price_range, en, dataset_type, user_id) -> List[dict]:
    return search_cards_data(name, rarity, faction, set, main_effect, main_effect_2, echo_effect, exclude_effect, 
        main_cost_range, recall_cost_range, forest_cost_range, mountain_cost_range, ocean_cost_range,
        no_condition, in_market, price_range, en, dataset_type, user_id)

def post_offer_live_market_service(data: List[dict]) -> None:
    """Optimisation de la gestion des offres pour réduire les appels à la base de données."""
    # Précharger les cartes et les offres existantes pour éviter des requêtes répétées
    references = [item['reference'] for item in data]
    existing_cards = {card.reference: card for card in db.session.query(Card).filter(Card.reference.in_(references)).all()}
    existing_offers = {offer.reference_card: offer for offer in db.session.query(Offer).filter(Offer.reference_card.in_(references), ~Offer.is_deleted).all()}

    # Liste temporaire pour les mises à jour des cartes
    cards_to_update = []

    for item in data:
        reference_card = item['reference']
        new_offer = Offer(
            reference_card=reference_card,
            id_offer=item.get('offerId'),
            price=item.get('price'),
            currency=item.get('currency'),
            status=item['status'],
            link_offer=None
        )

        existing_card = existing_cards.get(reference_card)
        if not existing_card:
            continue

        existing_offer = existing_offers.get(reference_card)

        if new_offer.status == 'available':
            if existing_offer and not existing_offer.is_deleted:
                if existing_offer.id_offer == new_offer.id_offer:
                    # Même offre, pas de mise à jour nécessaire
                    if existing_card.price == new_offer.price or existing_offer.currency != new_offer.currency:
                        cards_to_update.append(existing_card)
                        continue
                    else:
                        # Préparer la nouvelle offre
                        existing_offer.is_deleted = True
                        existing_offer.deleted_at = datetime.now(timezone.utc)
                        existing_offer.status = 'expired'

                        # Préparer la nouvelle offre
                        new_offer.link_offer = f"https://www.altered.gg/fr-fr/cards/{new_offer.reference_card}/offers"
                        new_offer.is_deleted = False
                        new_offer.created_at = datetime.now(timezone.utc)
                        new_offer.deleted_at = None
                        new_offer.user_altered = None
                        new_offer.user_id = None
                        new_offer.previous_offer = existing_offer.id if existing_offer else None
                        db.session.add(new_offer)

                        # Mettre à jour la carte
                        existing_card.price = new_offer.price
                        existing_card.url_offer = new_offer.link_offer
                        existing_card.price_currency = new_offer.currency
                        existing_card.price_updated_at = datetime.now(timezone.utc)
                        send_user_alert(existing_card, "edited" if existing_offer else "added")
                        continue
                else:
                    # Nouvelle offre, marquer l'ancienne comme expirée
                    existing_offer.is_deleted = True
                    existing_offer.deleted_at = datetime.now(timezone.utc)
                    existing_offer.status = 'expired'

            # Préparer la nouvelle offre
            new_offer.link_offer = f"https://www.altered.gg/fr-fr/cards/{new_offer.reference_card}/offers"
            new_offer.is_deleted = False
            new_offer.created_at = datetime.now(timezone.utc)
            new_offer.deleted_at = None
            new_offer.user_altered = None
            new_offer.user_id = None
            new_offer.previous_offer = existing_offer.id if existing_offer else None
            db.session.add(new_offer)

            # Mettre à jour la carte
            existing_card.price = new_offer.price
            existing_card.url_offer = new_offer.link_offer
            existing_card.price_currency = new_offer.currency
            existing_card.price_updated_at = datetime.now(timezone.utc)
            send_user_alert(existing_card, "edited" if existing_offer else "added")
        else:
            if existing_offer and not existing_offer.is_deleted:
                # Marquer l'offre existante comme expirée
                existing_offer.is_deleted = True
                existing_offer.deleted_at = datetime.now(timezone.utc)
                existing_offer.status = 'expired'

                # Mettre à jour la carte
                existing_card.price = None
                existing_card.price_currency = None
                existing_card.url_offer = None
                existing_card.price_updated_at = datetime.now(timezone.utc)
                send_user_alert(existing_card, "expired")
            else:
                # Pas d'offre existante, rien à faire pour cette carte
                existing_card.price = None
                existing_card.price_currency = None
                existing_card.url_offer = None
                existing_card.price_updated_at = datetime.now(timezone.utc)

    # Appliquer les mises à jour de `price_updated_at` en une seule fois
    now = datetime.now(timezone.utc)
    for card in cards_to_update:
        card.price_updated_at = now


    # Commit toutes les modifications en une seule fois
    db.session.commit()

def get_last_added_cards_service() -> List[dict]:
    return get_last_added_cards_data()

def get_count_cards_created_today_service() -> int:
    return get_count_cards_created_today_data()

def is_image_url_accessible(url: str) -> bool:
    try:
        response = requests.head(url, timeout=2)
        return response.status_code == 200
    except Exception:
        return False
    
def send_user_alert(card: Card, type_changement: str):
    alerts = get_user_alert_by_reference_card_data(card.reference)
    for alert in alerts:
        user = get_user_by_id_data(alert.id_user)
        if user and user.discord_id: 
            socketio.emit('script_output', {'data': f"discord alert send : {card.name_en} {card.reference} {user.username}"})
            print(f"discord alert send : {card.name_en} {card.reference} {user.username}")
            image_url = card.imagePath if is_image_url_accessible(card.imagePath) else "/static/img/cardback.webp"
            embed_message = {
                "username": user.username,
                "name_card": card.name,
                "reference": card.reference,
                "changement_type": type_changement,
                "price": f"{card.price} {card.price_currency}" if card.price and card.price_currency else "N/A",
                "date_effective": card.price_updated_at.strftime("%Y-%m-%d %H:%M:%S") if card.price_updated_at else "",
                "url_image_card": image_url,
                "lien_vers_alerts": f"https://altertracker.com/stats/{card.reference}"
            }
            response = requests.post(f"{ConfigEnv.DISCORD_BOT_URI}/sendalert", json={"discord_id": user.discord_id, "embed_message": embed_message})
            print(response)
        # else:
        #     if user:
        #         send_user_alert_mail(card, type_changement, user)

def send_user_alert_mail(card: Card, type_changement: str, user: User):
    socketio.emit('script_output', {'data': f"mail send : {card.name_en} {card.reference} {user.username}"})
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
            "LIEN_VERS_ALERTS": f"{ConfigEnv.ANGULAR_URL}/stats/{card.reference}",
            "YEAR": str(datetime.now(timezone.utc).year)
        }),
        sender={"name": "AlterTracker", "email": "noreply@altertracker.com"}
    )
    try:
        response = mail_api.send_transac_email(send_smtp_email)
        print(response)
    except ApiException as e:
        print("Exception lors de l'appel à l’API Sendinblue: %s\n" % e)

def update_card_service(data: dict) -> Optional[Card]:
    return update_card_data(data)

def get_effect_service(lang: str) -> List[dict]:
    return get_effect_data(lang)
