from concurrent.futures import ThreadPoolExecutor
import time
from typing import List
import requests
from sqlalchemy.orm import scoped_session, sessionmaker
from app.scripts import card_routine
from app.models.card import Card
from app.extensions import db, socketio
from app.config import ConfigEnv

class ApiOffer:
    lowerPrice = 0
    lowerOfferId = 0
    reference = None

def run_script(faction=None, workers=1):
    # Démarrer le timer
    start_time = time.time()
    Session = scoped_session(sessionmaker(bind=db.engine))

    def post_offer_live_market_service(data: List[dict]) -> None:
        try:
            if ConfigEnv.FLASK_ENV == 'production':
                api_url = "http://api.altertracker.svc.cluster.local:5001/api/card/offerlivemarket"
            else:
                api_url = "http://127.0.0.1:5001/api/card/offerlivemarket"

            payload = {
                'from_script': True,
                'offers': data  # data contient la liste des offres
            }

            # Effectuer la requête POST
            response = requests.post(api_url, json=payload)

            # Vérifier le statut de la réponse
            if response.status_code == 200 or response.status_code == 201:
                socketio.emit('script_output', {'data': f"\033[92mPOST réussi : {response.json()}\033[0m"})
            else:
                socketio.emit('script_output', {'data': f"\033[91mErreur POST : {response.status_code} - {response.text}\033[0m"})
        except Exception as e:
            socketio.emit('script_output', {'data': f"\033[91mErreur lors de la requête POST : {e}\033[0m"})

    def split_list(data, n):
        """Divise une liste en `n` sous-listes de taille approximativement égale."""
        k, m = divmod(len(data), n)
        return [data[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

    def process_unique_cards(subset, start_index, count):
        """Traite un sous-ensemble de cartes pour la tâche `get_unique`."""
        session = Session()
        try:
            for index, dbcard in enumerate(subset, start=start_index):
                count += 1
                socketio.emit('script_output', {'data': f"\033[94m{dbcard.name_en} {dbcard.faction} {dbcard.set} : {count}/{len(subset)}\033[0m"})
                offers = []
                page = 1
                cancelUpdate = False
                while True:
                    time.sleep(0.2)
                    cards = card_routine.get_unique_offers(
                        session, dbcard.name_en, dbcard.faction, dbcard.set, page
                    )
                    if not cards or 'hydra:member' not in cards or not cards['hydra:member']:
                        cancelUpdate = True
                        break

                    if 'hydra:totalItems' in cards and cards['hydra:totalItems'] >= 1000:
                        socketio.emit('script_output', {'data': f"\033[91mTROP DE RESULTATS pour {dbcard.name_en} ({dbcard.faction}) ({dbcard.set})\033[0m"})

                    socketio.emit('script_output', {'data': f"\033[92mpage : {page} pour {cards.get('hydra:totalItems', 0)} offres trouvées\033[0m"})

                    for card in cards['hydra:member']:
                        data = dict()
                        data['price'] = card.get('lowerPrice')
                        data['offerId'] = card.get('lowerOfferId')
                        data['reference'] = card.get('@id').replace('/cards/', '')
                        data['currency'] = "EUR"
                        data['status'] = "available"
                        offers.append(data)
                    if len(cards['hydra:member']) < 36:
                        break
                    page += 1
                socketio.emit('script_output', {'data': f"Nb cards avec offres : {len(offers)}"})
                offers += addNoOffers(offers, dbcard.name_en, dbcard.faction, dbcard.set)
                socketio.emit('script_output', {'data': f"Nb cards : {len(offers)} -> Go To post_offer_live_market_service"})
                if not cancelUpdate:
                    post_offer_live_market_service(offers)

        except Exception as e:
            socketio.emit('script_output', {'data': f"\033[91mError : {e}\033[0m"})
        finally:
            session.close()

    def addNoOffers(offers: List[dict], name_en: str, faction: str, set: str) -> List[dict]:
        session = Session()
        try:
            existing_references = [offer['reference'] for offer in offers]
            missing_cards = session.query(Card).filter(
                Card.name_en == name_en,
                Card.faction == faction,
                Card.set == set,
                Card.rarity == 'UNIQUE',
                ~Card.reference.in_(existing_references)  # Condition NOT IN
            ).all()
            dataset = []
            for card in missing_cards:
                data = dict()
                data['reference'] = card.reference
                data['status'] = "unavailable"  # Indiquer que la carte est manquante
                dataset.append(data)
            socketio.emit('script_output', {'data': f"Nb Cards sans offres : {len(missing_cards)}"})
            return dataset
        except Exception as e:
            socketio.emit('script_output', {'data': f"\033[91mError : {e}\033[0m"})
            return []
        finally:
            session.close()

    def get_unique():
        print("----------- GET UNIQUE OFFERS -----------")
        socketio.emit('script_output', {'data': "----------- GET UNIQUE OFFERS -----------"})

        session = Session()
        try:
            query = session.query(Card).filter(Card.rarity == 'RARE', Card.type == 'CHARACTER')

            # Appliquer le filtre de faction si fourni
            if faction:
                socketio.emit('script_output', {'data': f"Filtrage des cartes pour la faction : {faction}"})
                query = query.filter(Card.faction == faction)

            existing_cards = {
                card.id: card
                for card in query.all()
            }
        finally:
            session.close()

        # total_cards = len(existing_cards)
        subsets = split_list(list(existing_cards.values()), workers)

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for i, subset in enumerate(subsets):
                count = 0
                start_index = sum(len(subsets[j]) for j in range(i)) + 1
                futures.append(executor.submit(process_unique_cards, subset, start_index, count))

            for future in futures:
                future.result()  # Attendre que toutes les tâches soient terminées

    get_unique()

    # Fin du timer
    end_time = time.time()
    execution_time = end_time - start_time

    # Conversion en heures, minutes et secondes
    hours, remainder = divmod(execution_time, 3600)
    minutes, seconds = divmod(remainder, 60)


    print(f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
    socketio.emit('script_output', {'data': f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}"})
    print(f"GET UNIQUE OFFERS terminé")
