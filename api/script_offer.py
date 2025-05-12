from datetime import datetime
import time
from app import create_app
from app.scripts import card_routine
from app.models.card import Card
from app.models.offer import Offer
from app.extensions import db

# Créer l'application Flask
app = create_app()

# Démarrer le timer
start_time = time.time()

with app.app_context():  # Activer le contexte de l'application
    token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJDMFo0V3JVWE1xT2JtMy1CTU8xRFV5YktidFA2bldLb2VvWmE1UGJuZHhZIn0.eyJleHAiOjE3NDcwNDExNjIsImlhdCI6MTc0NzAzMzk2MiwiYXV0aF90aW1lIjoxNzQ2NzA2MTk4LCJqdGkiOiJkMTZiNWQyZi0zYjMwLTRhZjItOGMwNS1jOTlkNGNmMzBiNGEiLCJpc3MiOiJodHRwczovL2F1dGguYWx0ZXJlZC5nZy9yZWFsbXMvcGxheWVycyIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiI0Zjc4ZWI5MC01NTRlLTQwYjQtODgzNS01MmYyNjQ3YTgxNzciLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ3ZWIiLCJzaWQiOiIyZWVkZDU5NC00YjQxLTRhMTQtYjBjYi0yZDA2ODZjNTY5OTIiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vYXV0aC5hbHRlcmVkLmdnIiwiaHR0cHM6Ly93d3cuYWx0ZXJlZC5nZyJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib3RwX2VtYWlsIiwiZGVmYXVsdC1yb2xlcy1wbGF5ZXJzIiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIHByb2ZpbGUgZW1haWwiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicHJlZmVycmVkX3VzZXJuYW1lIjoianVsaWVuLm1hbGlnZUBob3RtYWlsLmZyIiwiZW1haWwiOiJqdWxpZW4ubWFsaWdlQGhvdG1haWwuZnIifQ.0VP2o8BR-DCup7A1bZ8DNGxRO-Onz0tMYHsMa9ni2VZd4Yrt4cLimTq0kFjFmI_jPaA7vb0M1jwqqYM9y7TpmeO-2cSE6Y5CsinZrG1fl1r-B5gep8rFLaahb_5Vn9U3YLPQHJIsL_Jsh0P_0Jk5_8dYBSMamgcRtMi9Sdqsst-oWZOoVXNHZT2rcUkkSZQ0U4u0BYZoQUU429Ghe55IxgeR1lbmeqZ1nyH16-i_T-v8PWgfq7iKnRWHfL76fXWSiD23_59UrCKlEQeypY_PNXWsGEHxad0qCg5Rk1CBKd3hNGxoeX3tyuzAPDXOqQGXBVfvza908Tk7NMC0izlGbQ"
    nb_offers = 0
    start_incremental_id = 1
    print(f"----------- GET OFFRES -----------")
    # Récupérer toutes les cartes
    existing_cards = db.session.query(Card).filter(Card.id >= start_incremental_id).order_by(Card.id).all()
    total_cards = len(existing_cards)
    for index, dbcard in enumerate(existing_cards.values(), start=1):
        # Vérifier si la carte a une référence
        if dbcard.reference:
            # Récupérer l'offre de la carte
            print(f"Récupération de l'offre pour la carte {dbcard.reference}  |  {index}/{total_cards}", end="", flush=True)
            offers = card_routine.get_offer_by_reference(dbcard.reference, token)
            
            # Vérifier si l'offre existe
            if offer:
                if offers[0]['convertedPrice'] and offer['status'] == 'available':
                    # Mettre à jour l'URL de l'offre dans la base de données
                    dbcard.url_offer = f'https://www.altered.gg/fr-fr/cards/{dbcard.reference}/offers'
                    dbcard.price = offers[0]['convertedPrice']
                    for offer in offers:
                        if offer['convertedPrice'] and offer['status'] == 'available':
                            nb_offers += 1
                            dboffers = db.session.query(Offer).filter(Offer.reference_card==dbcard.reference).all()
                            for dboffer in dboffers:
                                if dboffer.id_offer is not offer['offerId']:
                                    dboffer.status = 'expired'
                                    dboffer.is_edited = True
                                    dboffer.edited_at = datetime.now()
                                    dboffer.is_deleted = True
                                    dboffer.deleted_at = datetime.now()
                                else:
                                    price=offer['convertedPrice'],
                                    currency=offer['convertedCurrency'],
                                    quantity=offer['quantity'],
                                    status=offer['status'],
                                    dboffer.is_edited = True
                                    dboffer.edited_at = datetime.now()
                            newoffer = Offer(
                                reference_card=dbcard.reference,
                                id_offer=offer['offerId'],
                                price=offer['convertedPrice'],
                                currency=offer['convertedCurrency'],
                                quantity=offer['quantity'],
                                status=offer['status'],
                                link_offer=dbcard.url_offer,
                                created_at=datetime.now(),
                            )
                            db.session.add(newoffer)
                else:
                    dbcard.url_offer = None
                    dbcard.price = None
                dbcard.price_updated_at = datetime.now()
                db.session.commit()
            else:
                print(f"\033[91mError get {dbcard.name} at {dbcard.incremental_id}\033[0m")
                break
        else:
            print(f"\033[91mLa carte {dbcard.name} n'a pas de référence\033[0m")
    print(f"\033[92mNombre total d'offres : {nb_offers}\033[0m")

# Fin du timer
end_time = time.time()
execution_time = end_time - start_time

# Conversion en heures, minutes et secondes
hours, remainder = divmod(execution_time, 3600)
minutes, seconds = divmod(remainder, 60)

print(f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
