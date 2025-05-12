from datetime import datetime
import time
from app import create_app
from app.scripts import card_routine
from app.models.card import Card
from app.models.offer import Offer
from app.extensions import db
from app.data.card_data import get_cards_count_data

# Créer l'application Flask
app = create_app()

# Démarrer le timer
start_time = time.time()

with app.app_context():  # Activer le contexte de l'application
    token = ""
    nb_offers = 0
    start_incremental_id = 2935
    print(f"----------- GET OFFRES -----------")
    # Récupérer toutes les cartes
    existing_cards = {
        card.id: card
        for card in Card.query.filter(Card.id  >= start_incremental_id)
        .order_by(Card.id)  # Trier par ordre alphabétique croissant sur name_en
        .all()
    }
    total_cards = get_cards_count_data()
    for index, dbcard in enumerate(existing_cards.values(), start=start_incremental_id):
        # Vérifier si la carte a une référence
        if dbcard.reference:
            # Récupérer l'offre de la carte
            try:
                print(f"\rRécupération de l'offre pour la carte {dbcard.reference}  |  {index}/{total_cards}....", end="", flush=True)
                offers = card_routine.get_offer_by_reference(dbcard.reference, token)
                
                # Vérifier si l'offre existe
                if offers:
                    if offers[0]['convertedPrice'] and offers[0]['status'] == 'available':
                        # Mettre à jour l'URL de l'offre dans la base de données
                        dbcard.url_offer = f'https://www.altered.gg/fr-fr/cards/{dbcard.reference}/offers'
                        dbcard.price = offers[0]['convertedPrice']
                        nb_offers += 1
                        dboffers = db.session.query(Offer).filter(Offer.reference_card==dbcard.reference).all()
                        for dboffer in dboffers:
                            if dboffer.id_offer is not offers[0]['offerId']:
                                dboffer.status = 'expired'
                                dboffer.is_edited = True
                                dboffer.edited_at = datetime.now()
                                dboffer.is_deleted = True
                                dboffer.deleted_at = datetime.now()
                            else:
                                if dboffer.price is not offers[0]['convertedPrice']:
                                  price=offers[0]['convertedPrice'],
                                  currency=offers[0]['convertedCurrency'],
                                  quantity=offers[0]['quantity'],
                                  status=offers[0]['status'],
                                  dboffer.is_edited = True
                                  dboffer.edited_at = datetime.now()
                        newoffer = Offer(
                            reference_card=dbcard.reference,
                            id_offer=offers[0]['offerId'],
                            price=offers[0]['convertedPrice'],
                            currency=offers[0]['convertedCurrency'],
                            quantity=offers[0]['quantity'],
                            status=offers[0]['status'],
                            link_offer=dbcard.url_offer,
                            created_at=datetime.now(),
                        )
                        db.session.add(newoffer)
                    else:
                        dbcard.url_offer = None
                        dbcard.price = None
                        dboffers = db.session.query(Offer).filter(Offer.reference_card==dbcard.reference).all()
                        for dboffer in dboffers:
                            dboffer.status = 'expired' if 'status' not in offers[0] else offers[0]['status']
                            dboffer.is_edited = True
                            dboffer.edited_at = datetime.now()
                            if 'status' not in offers[0]:
                              dboffer.is_deleted = True
                              dboffer.deleted_at = datetime.now()
                    dbcard.price_updated_at = datetime.now()
                    db.session.commit()
                else:
                    dbcard.url_offer = None
                    dbcard.price = None
                    dbcard.price_updated_at = datetime.now()
                    dboffers = db.session.query(Offer).filter(Offer.reference_card==dbcard.reference).all()
                    for dboffer in dboffers:
                        dboffer.status = 'expired'
                        dboffer.is_edited = True
                        dboffer.edited_at = datetime.now()
                        dboffer.is_deleted = True
                        dboffer.deleted_at = datetime.now()
                    db.session.commit()
            except Exception as e:
                print()
                print(f"\033[91m{e}\033[0m")
                print(f"\033[91mError get {dbcard.reference} at {dbcard.id}\033[0m")
                break
        else:
            print()
            print(f"\033[91mLa carte {dbcard.name} n'a pas de référence\033[0m")
    print()
    print(f"\033[92mNombre total d'offres : {nb_offers}\033[0m")

# Fin du timer
end_time = time.time()
execution_time = end_time - start_time

# Conversion en heures, minutes et secondes
hours, remainder = divmod(execution_time, 3600)
minutes, seconds = divmod(remainder, 60)

print(f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
