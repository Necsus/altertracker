from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time
from sqlalchemy.orm import scoped_session, sessionmaker
from app import create_app
from app.scripts import card_routine
from app.models.card import Card
from app.extensions import db
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO, filename='script.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Création de l'application et configuration de SQLAlchemy
app = create_app()

# Démarrer le timer
start_time = time.time()
with app.app_context():
    Session = scoped_session(sessionmaker(bind=db.engine))
    def map_jsoncard_to_card(jsonCard, name_en=None) -> Card:
        """Mappe un JSON de carte à un objet Card."""
        return Card(
            id_card=jsonCard['id'],
            reference=jsonCard['reference'],
            name=jsonCard['name'],
            name_en=name_en,
            faction=jsonCard['mainFaction']['reference'],
            rarity=jsonCard['rarity']['reference'],
            type=jsonCard['cardType']['reference'],
            set=jsonCard['cardSet']['reference'],
            imagePath=jsonCard['imagePath'],
            isSuspended=jsonCard['isSuspended'],
            MAIN_COST=jsonCard['elements']['MAIN_COST'],
            RECALL_COST=jsonCard['elements']['RECALL_COST'],
            MOUNTAIN_POWER=None if jsonCard['cardType']['reference'] != "CHARACTER" else jsonCard['elements']['MOUNTAIN_POWER'],
            OCEAN_POWER=None if jsonCard['cardType']['reference'] != "CHARACTER" else jsonCard['elements']['OCEAN_POWER'],
            FOREST_POWER=None if jsonCard['cardType']['reference'] != "CHARACTER" else jsonCard['elements']['FOREST_POWER'],
            MAIN_EFFECT=None,
            ECHO_EFFECT=None,
        )

    def map_effect_to_card(card: Card, jsonCard) -> Card:
        """Mappe les effets d'une carte JSON à un objet Card."""
        card.MAIN_EFFECT = jsonCard['elements'].get('MAIN_EFFECT')
        card.ECHO_EFFECT = jsonCard['elements'].get('ECHO_EFFECT')
        return card

    def insert_cards_into_db(cards, session):
        """Insère ou met à jour des cartes dans la base de données."""
        try:
            existing_references = {card.reference for card in session.query(Card.reference).all()}
            new_cards = [card for card in cards if card.reference not in existing_references]
            session.bulk_save_objects(new_cards)
            session.commit()
            logging.info(f"{len(new_cards)} cartes insérées.")
        except Exception as e:
            session.rollback()
            logging.error(f"Erreur lors de l'insertion des cartes : {e}")

    def split_list(data, n):
        """Divise une liste en `n` sous-listes de taille approximativement égale."""
        k, m = divmod(len(data), n)
        return [data[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

    def process_unique_cards(subset, sets, mainCosts, recallCosts, forestPowers, total_cards, start_index):
        """Traite un sous-ensemble de cartes pour la tâche `get_unique`."""
        session = Session()
        try:
            for index, dbcard in enumerate(subset, start=start_index):
                for set in sets:
                    if dbcard.set == 'ALIZE' and set != 'ALIZE':
                        continue

                    filtered_mainCosts = [cost for cost in mainCosts if dbcard.MAIN_COST - 4 <= cost <= dbcard.MAIN_COST + 4]
                    for mainCost in filtered_mainCosts:
                        filtered_recallCosts = [cost for cost in recallCosts if dbcard.RECALL_COST - 4 <= cost <= dbcard.RECALL_COST + 4]
                        for recallCost in filtered_recallCosts:
                            cardToInsert = []
                            test_result = card_routine.get_unique_cards_name_faction(
                                dbcard.name_en, dbcard.faction, set, mainCost, recallCost, forestPowers, 1
                            )

                            if test_result and test_result.get('hydra:totalItems', 0) > 0:
                                logging.info(f"--- CARDNAME : {dbcard.name}  FACTION : {dbcard.faction}  SET : {set}  MAIN_COST : {mainCost}  RECALL_COST : {recallCost}  |  {index}/{total_cards}")
                                page = 1
                                while True:
                                    cards = card_routine.get_unique_cards_name_faction(
                                        dbcard.name_en, dbcard.faction, set, mainCost, recallCost, forestPowers, page
                                    )

                                    if not cards or 'hydra:member' not in cards or not cards['hydra:member']:
                                        break

                                    for card in cards['hydra:member']:
                                        tempCard = map_jsoncard_to_card(card, dbcard.name_en)
                                        card_to_update = session.query(Card).filter_by(reference=tempCard.reference).first()
                                        if card_to_update:
                                            # Initialiser un drapeau pour suivre les modifications
                                            has_updated = False

                                            # Vérifiez et mettez à jour uniquement si les valeurs sont différentes
                                            if card_to_update.name != tempCard.name:
                                                card_to_update.name = tempCard.name
                                                has_updated = True
                                            if card_to_update.name_en != tempCard.name_en:
                                                card_to_update.name_en = tempCard.name_en
                                                has_updated = True
                                            if card_to_update.isSuspended != tempCard.isSuspended:
                                                card_to_update.isSuspended = tempCard.isSuspended
                                                has_updated = True
                                            if card_to_update.imagePath != tempCard.imagePath:
                                                card_to_update.imagePath = tempCard.imagePath
                                                has_updated = True
                                            if card_to_update.MAIN_COST != tempCard.MAIN_COST:
                                                card_to_update.MAIN_COST = tempCard.MAIN_COST
                                                has_updated = True
                                            if card_to_update.RECALL_COST != tempCard.RECALL_COST:
                                                card_to_update.RECALL_COST = tempCard.RECALL_COST
                                                has_updated = True
                                            if card_to_update.MOUNTAIN_POWER != tempCard.MOUNTAIN_POWER:
                                                card_to_update.MOUNTAIN_POWER = tempCard.MOUNTAIN_POWER
                                                has_updated = True
                                            if card_to_update.OCEAN_POWER != tempCard.OCEAN_POWER:
                                                card_to_update.OCEAN_POWER = tempCard.OCEAN_POWER
                                                has_updated = True
                                            if card_to_update.FOREST_POWER != tempCard.FOREST_POWER:
                                                card_to_update.FOREST_POWER = tempCard.FOREST_POWER
                                                has_updated = True
                                            if card_to_update.created_at is None:
                                                card_to_update.created_at = datetime.now()
                                                has_updated = True

                                            # Si une modification a été effectuée, mettre à jour `edited_at`
                                            if has_updated:
                                                card_to_update.edited_at = datetime.now()
                                            continue

                                        detailsCard = card_routine.get_card_by_reference(tempCard.reference)
                                        tempCard = map_effect_to_card(tempCard, detailsCard)
                                        cardToInsert.append(tempCard)

                                    page += 1

                            if cardToInsert:
                                insert_cards_into_db(cardToInsert, session)
        finally:
            session.close()

    def get_unique():
        """Récupère les cartes uniques et les traite en parallèle."""
        logging.info("----------- GET UNIQUE -----------")
        sets = ['COREKS', 'CORE', 'ALIZE', 'BISE']
        mainCosts = list(range(1, 11))
        recallCosts = list(range(1, 11))
        forestPowers = list(range(0, 11))

        session = Session()
        try:
            existing_cards = {
                card.id: card
                for card in session.query(Card).filter(Card.rarity == 'RARE', Card.type == 'CHARACTER')
                .order_by(Card.name_en.asc())
                .all()
            }
        finally:
            session.close()

        total_cards = len(existing_cards)
        subsets = split_list(list(existing_cards.values()), 10)  # Divise en 5 sous-listes

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i, subset in enumerate(subsets):
                start_index = sum(len(subsets[j]) for j in range(i)) + 1
                futures.append(executor.submit(process_unique_cards, subset, sets, mainCosts, recallCosts, forestPowers, total_cards, start_index))

            for future in futures:
                future.result()  # Attendre que toutes les tâches soient terminées

    get_unique()

# Fin du timer
end_time = time.time()
execution_time = end_time - start_time

# Conversion en heures, minutes et secondes
hours, remainder = divmod(execution_time, 3600)
minutes, seconds = divmod(remainder, 60)

logging.info(f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}")