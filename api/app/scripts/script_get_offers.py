from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time
from typing import List
from sqlalchemy.orm import scoped_session, sessionmaker
from app.scripts import card_routine
from app.models.card import Card
from app.extensions import db, socketio
from app.services.card_service import post_offer_live_market_service

class ApiOffer:
    lowerPrice = 0
    lowerOfferId = 0
    reference = None

def run_script(faction=None, workers=3):
    # Démarrer le timer
    start_time = time.time()
    Session = scoped_session(sessionmaker(bind=db.engine))
    
    def insert_cards_into_db(cards, session):
        try:
            existing_references = {card.reference for card in session.query(Card.reference).all()}
            new_cards = [card for card in cards if card.reference not in existing_references]
            session.bulk_save_objects(new_cards)
            session.commit()
        except Exception as e:
            session.rollback()
            socketio.emit('script_output', {'data': f"\033[91mErreur lors de l'insertion des cartes : {e}\033[0m"})

    def split_list(data, n):
        """Divise une liste en `n` sous-listes de taille approximativement égale."""
        k, m = divmod(len(data), n)
        return [data[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

    def process_unique_cards(subset, mainCosts, recallCosts, start_index, count):
        """Traite un sous-ensemble de cartes pour la tâche `get_unique`."""
        session = Session()
        try:
            for index, dbcard in enumerate(subset, start=start_index):
                count += 1
                offers = []
                # Afficher la progression au format "1/34"
                socketio.emit('script_output', {'data': f"\033[94mProgression : {count}/{len(subset)}\033[0m"})  # En bleu pour plus de visibilité
                forestPowers = list(range(0, 11))
                filtered_mainCosts = [cost for cost in mainCosts if dbcard.MAIN_COST - 4 <= cost <= dbcard.MAIN_COST + 4]
                for mainCost in filtered_mainCosts:
                    filtered_recallCosts = [cost for cost in recallCosts if dbcard.RECALL_COST - 4 <= cost <= dbcard.RECALL_COST + 4]
                    for recallCost in filtered_recallCosts:
                        cardToInsert = []
                        goToForestPowerFilter = False
                        test_result = card_routine.get_unique_offers(
                            dbcard.name_en, dbcard.faction, dbcard.set, mainCost, recallCost, forestPowers, 1
                        )
                        if test_result and test_result.get('hydra:totalItems', 0) >= 1000:
                            socketio.emit('script_output', {'data': f"\033[91mATTENTION TROP DE RESULTATS MANQUE DES CARTES\033[0m"})
                            socketio.emit('script_output', {'data': f"\033[91mName: {dbcard.name_en} | faction: {dbcard.faction} | set: {dbcard.set} | mainCost: {mainCost} | recallCost: {recallCost} | forestPower: {forestPowers}\033[0m"})
                            goToForestPowerFilter = True
                            forestPowers = [mainCost]
                            test_result = card_routine.get_unique_offers(
                                dbcard.name_en, dbcard.faction, dbcard.set, mainCost, recallCost, forestPowers, 1
                            )
                            socketio.emit('script_output', {'data': f"\033[92mName: {dbcard.name_en} OK POUR forestPower: {forestPowers} results : {test_result.get('hydra:totalItems', 0)}\033[0m"})

                        if test_result and test_result.get('hydra:totalItems', 0) > 0:
                            page = 1
                            while True:
                                cards = card_routine.get_unique_offers(
                                    dbcard.name_en, dbcard.faction, dbcard.set, mainCost, recallCost, forestPowers, page
                                )

                                if not cards or 'hydra:member' not in cards or not cards['hydra:member']:
                                    break

                                for card in cards['hydra:member']:
                                    data = dict()
                                    data['price'] = card.get('lowerPrice')
                                    data['offerId'] = card.get('lowerOfferId')
                                    data['reference'] = card.get('@id').replace('/cards/', '')
                                    data['currency'] = "EUR"
                                    data['status'] = "available"
                                    offers.append(data)
                                page += 1
                            if goToForestPowerFilter:
                                page = 1
                                forestPowers = list(range(0, 11))
                                while True:
                                    
                                    cards = card_routine.get_unique_offers(
                                        dbcard.name_en, dbcard.faction, dbcard.set, mainCost, recallCost, [fp for fp in forestPowers if fp != mainCost], page
                                    )

                                    if not cards or 'hydra:member' not in cards or not cards['hydra:member']:
                                        break
                                    
                                    socketio.emit('script_output', {'data': f"\033[92mName: {dbcard.name_en} OK POUR forestPower: {[fp for fp in forestPowers if fp != mainCost]} results : {cards.get('hydra:totalItems', 0)}\033[0m"})

                                    for card in cards['hydra:member']:
                                        data = dict()
                                        data['price'] = card.get('lowerPrice')
                                        data['offerId'] = card.get('lowerOfferId')
                                        data['reference'] = card.get('@id').replace('/cards/', '')
                                        data['currency'] = "EUR"
                                        data['status'] = "available"
                                        offers.append(data)
                                    page += 1
                offers.append(addNoOffers(offers, dbcard.name_en, dbcard.faction))
                post_offer_live_market_service(offers)

        except Exception as e:
            socketio.emit('script_output', {'data': f"\033[91mError : {e}\033[0m"})
        finally:
            session.close()
    def addNoOffers(offers: List[dict], name_en: str, faction: str) -> List[dict]:
        session = Session()
        try:
            existing_references = [offer['reference'] for offer in offers]
            missing_cards = session.query(Card).filter(
                Card.name_en == name_en,
                Card.faction == faction,
                ~Card.reference.in_(existing_references)  # Condition NOT IN
            ).all()
            dataset = []
            for card in missing_cards:
                data = dict()
                data['price'] = None  # Pas de prix pour les cartes manquantes
                data['offerId'] = None  # Pas d'offre ID pour les cartes manquantes
                data['reference'] = card.reference
                data['currency'] = None
                data['status'] = "unavailable"  # Indiquer que la carte est manquante
                dataset.append(data)

            return dataset
        except Exception as e:
            socketio.emit('script_output', {'data': f"\033[91mError : {e}\033[0m"})
            return []
        finally:
            session.close()

    def get_unique():
        print("----------- GET UNIQUE -----------")
        socketio.emit('script_output', {'data': "----------- GET UNIQUE -----------"})
        # sets = ['COREKS', 'CORE', 'ALIZE', 'BISE']
        mainCosts = list(range(1, 11))
        recallCosts = list(range(1, 11))

        session = Session()
        try:
            query = session.query(Card).filter(Card.rarity == 'RARE', Card.type == 'CHARACTER')

            # Appliquer le filtre de faction si fourni
            if faction:
                socketio.emit('script_output', {'data': f"Filtrage des cartes pour la faction : {faction}"})
                query = query.filter(Card.faction == faction)

            existing_cards = {
                card.id: card
                for card in query.order_by(Card.name_en.asc()).all()
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
                futures.append(executor.submit(process_unique_cards, subset, mainCosts, recallCosts, start_index, count))

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
    print(f"GET UNIQUE terminé")
