from datetime import datetime, timezone
import time
from app.models.offer import Offer
from app.scripts import card_routine
from app.models.card import Card
from app.extensions import db, socketio
from sqlalchemy.orm import scoped_session, sessionmaker
from concurrent.futures import ThreadPoolExecutor

def run_script(workers: int):
    # Démarrer le timer
    start_time = time.time()
    Session = scoped_session(sessionmaker(bind=db.engine))

    def split_list(data, n):
        k, m = divmod(len(data), n)
        return [data[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]
    
    def process_currency(subset, start_index):
        """Traite un sous-ensemble de cartes pour la tâche `get_unique`."""
        session = Session()
        try:
            socketio.emit('script_output', {'data': f"\033[94mNb Offers : {len(subset)}\033[0m"})
            for index, dboffer in enumerate(subset, start=start_index):
                dboffer_in_session = session.query(Offer).get(dboffer.id)
                socketio.emit('script_output', {'data': f"Update Offer : {dboffer_in_session.reference_card} ({index}/{len(subset)})"})
                time.sleep(0.1)
                offer = card_routine.get_offer_by_reference(session, dboffer_in_session.reference_card)
                if offer and len(offer) > 0:
                    dboffer_in_session.currency = offer[0]['currency']
                    dboffer_in_session.price = offer[0]['price']
                    card_to_update = session.query(Card).filter_by(reference=dboffer_in_session.reference_card).first()
                    if card_to_update:
                        if dboffer_in_session.currency != card_to_update.price_currency or dboffer_in_session.price != card_to_update.price:
                            card_to_update.price_currency = dboffer_in_session.currency
                            card_to_update.price = dboffer_in_session.price
                            session.commit()

        except Exception as e:
            socketio.emit('script_output', {'data': f"\033[91mError : {e}\033[0m"})
        finally:
            session.close()

    def get_currency():
        print("----------- GET CURRENCY -----------")
        socketio.emit('script_output', {'data': "----------- GET CURRENCY -----------"})
        session = Session()
        try:
            query = session.query(Offer).filter(Offer.status == 'available', Offer.currency != 'USD')

            # Appliquer le filtre de faction si fourni
            existing_offers = {
                offer.id: offer
                for offer in query.order_by(Offer.id.asc()).all()
            }
        finally:
            session.close()

        # total_cards = len(existing_cards)
        subsets = split_list(list(existing_offers.values()), workers)

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for i, subset in enumerate(subsets):
                start_index = sum(len(subsets[j]) for j in range(i)) + 1
                futures.append(executor.submit(process_currency, subset, start_index))

            for future in futures:
                future.result()  # Attendre que toutes les tâches soient terminées


    get_currency()

    # Fin du timer
    end_time = time.time()
    execution_time = end_time - start_time

    # Conversion en heures, minutes et secondes
    hours, remainder = divmod(execution_time, 3600)
    minutes, seconds = divmod(remainder, 60)


    print(f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
    socketio.emit('script_output', {'data': f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}"})
    print(f"GET CURRENCY terminé")