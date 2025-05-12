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

    nb_offer = 0

    print(f"----------- GET OFFRES -----------")
    # Récupérer toutes les cartes
    existing_cards = db.session.query(Card).order_by(Card.incremental_id).all()
    total_cards = len(existing_cards)
    for index, dbcard in enumerate(existing_cards.values(), start=1):
        # Vérifier si la carte a une référence
        if dbcard.reference:
            # Récupérer l'offre de la carte
            print(f"Récupération de l'offre pour la carte {dbcard.reference}  |  {index}/{total_cards}", end="", flush=True)
            offer = card_routine.get_offer_by_reference(dbcard.reference, token)
            
            # Vérifier si l'offre existe
            if offer:
                # Mettre à jour l'URL de l'offre dans la base de données
                if offer[0]['convertedPrice'] and offer[0]['status'] == 'available':
                    dbcard.url_offer = f'https://www.altered.gg/fr-fr/cards/{dbcard.reference}/offers'
                    dbcard.price = offer[0]['convertedPrice']
                    nb_offer += 1
                    dboffer = Offer(
                        reference_card=dbcard.reference,
                        id_offer=offer[0]['offerId'],
                        card_id=dbcard.id,
                        price=dbcard.price,
                        currency=offer[0]['convertedCurrency'],
                        quantity=offer[0]['quantity'],
                        status=offer[0]['status'],
                        link_offer=f'https://www.altered.gg/fr-fr/cards/{dbcard.reference}/offers',
                        created_at=datetime.now(),
                    )
                    db.session.add(dboffer)
                else:
                    dbcard.url_offer = None
                    dbcard.price = None
                dbcard.price_updated_at = datetime.now()

                db.session.commit()


            else:
                print(f"\033[91mError get {dbcard.name}\033[0m")
        else:
            print(f"\033[91mLa carte {dbcard.name} n'a pas de référence\033[0m")
