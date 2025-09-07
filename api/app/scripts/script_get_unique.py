from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import time
from sqlalchemy import text
from sqlalchemy.orm import scoped_session, sessionmaker
from app.scripts import card_routine
from app.models.card import Card
from app.models.new_card import NewCard
from app.extensions import db, socketio

def run_script(faction=None, workers=3, forceUpdate=False):
    # Démarrer le timer
    start_time = time.time()
    Session = scoped_session(sessionmaker(bind=db.engine))
    def map_jsoncard_to_card(jsonCard, name_en=None) -> Card:
        return Card(
            id_card=jsonCard['id'],
            reference=jsonCard['reference'],
            name=jsonCard['name'],
            name_en=name_en,
            faction=jsonCard['mainFaction']['reference'],
            rarity=jsonCard['rarity']['reference'],
            type=jsonCard['cardType']['reference'],
            subtype=None,
            set=jsonCard['cardSet']['reference'],
            imagePath=jsonCard['imagePath'],
            image_path_en=None,
            isSuspended=jsonCard['isSuspended'],
            MAIN_COST=jsonCard['elements']['MAIN_COST'],
            RECALL_COST=jsonCard['elements']['RECALL_COST'],
            MOUNTAIN_POWER=None if jsonCard['cardType']['reference'] != "CHARACTER" else jsonCard['elements']['MOUNTAIN_POWER'],
            OCEAN_POWER=None if jsonCard['cardType']['reference'] != "CHARACTER" else jsonCard['elements']['OCEAN_POWER'],
            FOREST_POWER=None if jsonCard['cardType']['reference'] != "CHARACTER" else jsonCard['elements']['FOREST_POWER'],
            MAIN_EFFECT=None,
            main_effect_en=None,
            ECHO_EFFECT=None,
            echo_effect_en=None,
            price_updated_at=None,
            errated = jsonCard['isErrated']
        )

    def map_effect_to_card(card: Card, jsonCard) -> Card:
        card.MAIN_EFFECT = jsonCard['elements'].get('MAIN_EFFECT')
        card.ECHO_EFFECT = jsonCard['elements'].get('ECHO_EFFECT')
        card.subtype = ','.join([sub['reference'] for sub in jsonCard['cardSubTypes']]) if jsonCard.get('cardSubTypes') else None
        return card
    
    def map_jsoncard_to_card_en(card: Card, jsonCard) -> Card:
        if 'cardType' in jsonCard:
          card.image_path_en = jsonCard['imagePath'] if 'imagePath' in jsonCard else None
          card.main_effect_en = jsonCard['elements']['MAIN_EFFECT'] if 'MAIN_EFFECT' in jsonCard['elements'] else None
          card.echo_effect_en = jsonCard['elements']['ECHO_EFFECT'] if 'ECHO_EFFECT' in jsonCard['elements'] else None
        return card

    def insert_cards_into_db(cards, session):
        try:
            # existing_references = {card.reference for card in session.query(Card.reference).all()}
            # new_cards = [card for card in cards if card.reference not in existing_references]
            socketio.emit('script_output', {'data': f"Cartes insérées : {len(cards)}"})
            new_cards_objs = [NewCard(reference=card.reference) for card in cards]
            session.bulk_save_objects(cards)
            session.bulk_save_objects(new_cards_objs)
            session.commit()
        except Exception as e:
            session.rollback()
            socketio.emit('script_output', {'data': f"\033[91mErreur lors de l'insertion des cartes : {e}\033[0m"})

    def split_list(data, n):
        """Divise une liste en `n` sous-listes de taille approximativement égale."""
        k, m = divmod(len(data), n)
        return [data[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

    def process_unique_cards(subset, mainCosts, recallCosts, start_index, count, worker_id, forceUpdate=False):
        """Traite un sous-ensemble de cartes pour la tâche `get_unique`."""
        session = Session()
        try:
            for index, dbcard in enumerate(subset, start=start_index):
                count += 1
                # Afficher la progression au format "1/34"
                socketio.emit('script_output', {'data': f"\033[94mProgression {worker_id}: {count}/{len(subset)}\033[0m"})  # En bleu pour plus de visibilité
                forestPowers = list(range(0, 11))
                filtered_mainCosts = [cost for cost in mainCosts if dbcard.MAIN_COST - 3 <= cost <= dbcard.MAIN_COST + 3]
                for mainCost in filtered_mainCosts:
                    filtered_recallCosts = [cost for cost in recallCosts if dbcard.RECALL_COST - 3 <= cost <= dbcard.RECALL_COST + 3]
                    for recallCost in filtered_recallCosts:
                        cardToInsert = []
                        goToForestPowerFilter = False
                        time.sleep(0.2)
                        test_result = card_routine.get_unique_cards_name_faction(
                            dbcard.name_en, dbcard.faction, dbcard.set, mainCost, recallCost, forestPowers, 1
                        )

                        if test_result and test_result.get('hydra:totalItems', 0) >= 1000:
                            socketio.emit('script_output', {'data': f"\033[91mATTENTION TROP DE RESULTATS MANQUE DES CARTES\033[0m"})
                            socketio.emit('script_output', {'data': f"\033[91mName: {dbcard.name_en} | faction: {dbcard.faction} | set: {dbcard.set} | mainCost: {mainCost} | recallCost: {recallCost} | forestPower: {forestPowers}\033[0m"})
                            goToForestPowerFilter = True
                            forestPowers = [mainCost]
                            time.sleep(0.2)
                            test_result = card_routine.get_unique_cards_name_faction(
                                dbcard.name_en, dbcard.faction, dbcard.set, mainCost, recallCost, forestPowers, 1
                            )
                            socketio.emit('script_output', {'data': f"\033[92mName: {dbcard.name_en} OK POUR forestPower: {forestPowers} results : {test_result.get('hydra:totalItems', 0)}\033[0m"})

                        if test_result and test_result.get('hydra:totalItems', 0) > 0:
                            cards_to_update = session.query(Card).filter(
                                Card.name_en == dbcard.name_en,
                                Card.faction == dbcard.faction,
                                Card.set == dbcard.set,
                                Card.MAIN_COST == mainCost,
                                Card.RECALL_COST == recallCost,
                                Card.rarity == 'UNIQUE',
                                Card.type == 'CHARACTER'
                            ).all()
                            if len(cards_to_update) == int(test_result.get('hydra:totalItems')) and test_result.get('hydra:totalItems') < 1000 and not forceUpdate:
                                # socketio.emit('script_output', {'data': f"NO CHANGES SKIPPING"})
                                continue
                            # else:
                            #     socketio.emit('script_output', {'data': f"CHANGES NO SKIPPING"})
                            page = 1
                            while True:
                                cards = card_routine.get_unique_cards_name_faction(
                                    dbcard.name_en, dbcard.faction, dbcard.set, mainCost, recallCost, forestPowers, page
                                )

                                if not cards or 'hydra:member' not in cards or not cards['hydra:member']:
                                    break

                                for card in cards['hydra:member']:
                                    tempCard = map_jsoncard_to_card(card, dbcard.name_en)
                                    card_to_update = next((c for c in cards_to_update if c.reference == tempCard.reference), None)
                                    if card_to_update:
                                        has_updated = False

                                        # Vérifiez et mettez à jour uniquement si les valeurs sont différentes
                                        if str(card_to_update.name) != str(tempCard.name):
                                            card_to_update.name = tempCard.name
                                            has_updated = True
                                        if str(card_to_update.name_en) != str(tempCard.name_en) or card_to_update.name_en is None:
                                            card_to_update.name_en = tempCard.name_en
                                            has_updated = True
                                        if str(card_to_update.isSuspended).lower() != str(tempCard.isSuspended).lower():
                                            card_to_update.isSuspended = True if str(tempCard.isSuspended).lower() == 'true' else False
                                            has_updated = True
                                        if str(card_to_update.imagePath) != str(tempCard.imagePath):
                                            card_to_update.imagePath = tempCard.imagePath
                                            has_updated = True
                                        if tempCard.image_path_en is not None:
                                            if str(card_to_update.image_path_en) != str(tempCard.imagePath) or card_to_update.image_path_en is None:
                                                card_to_update.image_path_en = tempCard.image_path_en
                                                has_updated = True
                                        if str(card_to_update.MAIN_COST) != str(tempCard.MAIN_COST):
                                            card_to_update.MAIN_COST = tempCard.MAIN_COST
                                            has_updated = True
                                        if str(card_to_update.RECALL_COST) != str(tempCard.RECALL_COST):
                                            card_to_update.RECALL_COST = tempCard.RECALL_COST
                                            has_updated = True
                                        if str(card_to_update.MOUNTAIN_POWER) != str(tempCard.MOUNTAIN_POWER):
                                            card_to_update.MOUNTAIN_POWER = tempCard.MOUNTAIN_POWER
                                            has_updated = True
                                        if str(card_to_update.OCEAN_POWER) != str(tempCard.OCEAN_POWER):
                                            card_to_update.OCEAN_POWER = tempCard.OCEAN_POWER
                                            has_updated = True
                                        if str(card_to_update.FOREST_POWER) != str(tempCard.FOREST_POWER):
                                            card_to_update.FOREST_POWER = tempCard.FOREST_POWER
                                            has_updated = True
                                        if str(card_to_update.errated).lower() != str(tempCard.errated).lower():
                                            card_to_update.errated = True if str(tempCard.errated).lower() == 'true' else False
                                            has_updated = True
                                        if tempCard.main_effect_en is not None:
                                            if str(card_to_update.main_effect_en) != str(tempCard.main_effect_en) \
                                                or card_to_update.main_effect_en is None or tempCard.main_effect_en is None:
                                                card_to_update.main_effect_en = tempCard.main_effect_en
                                                has_updated = True
                                        if tempCard.echo_effect_en is not None:
                                            if str(card_to_update.echo_effect_en) != str(tempCard.echo_effect_en) \
                                                or card_to_update.echo_effect_en is None or tempCard.echo_effect_en is None:
                                                card_to_update.echo_effect_en = tempCard.echo_effect_en
                                                has_updated = True
                                        if card_to_update.created_at is None:
                                            card_to_update.created_at = datetime.now(timezone.utc)
                                            has_updated = True

                                        if card_to_update.MAIN_EFFECT is None and card_to_update.ECHO_EFFECT is None:
                                            detailsCard = card_routine.get_card_by_reference(tempCard.reference)
                                            if detailsCard:
                                                temp_card = map_effect_to_card(tempCard, detailsCard)
                                                card_to_update.MAIN_EFFECT = temp_card.MAIN_EFFECT
                                                card_to_update.ECHO_EFFECT = temp_card.ECHO_EFFECT
                                                card_to_update.subtype = temp_card.subtype
                                                has_updated = True

                                        if has_updated:
                                            socketio.emit('script_output', {'data': f"Mise à jour de la carte : {card_to_update.name_en} ({card_to_update.reference})"})
                                            card_to_update.edited_at = datetime.now(timezone.utc)
                                        continue
                                    detailsCard = card_routine.get_card_by_reference(tempCard.reference)
                                    if detailsCard:
                                        tempCard = map_effect_to_card(tempCard, detailsCard)
                                    cardToInsert.append(tempCard)
                                session.commit()
                                if len(cards['hydra:member']) < 36:
                                    break
                                page += 1

                            if goToForestPowerFilter:
                                page = 1
                                forestPowers = list(range(0, 11))
                                while True:
                                    cards = card_routine.get_unique_cards_name_faction(
                                        dbcard.name_en, dbcard.faction, dbcard.set, mainCost, recallCost, [fp for fp in forestPowers if fp != mainCost], page
                                    )

                                    if not cards or 'hydra:member' not in cards or not cards['hydra:member']:
                                        break
                                    
                                    socketio.emit('script_output', {'data': f"\033[92mName: {dbcard.name_en} OK POUR forestPower: {[fp for fp in forestPowers if fp != mainCost]} results : {cards.get('hydra:totalItems', 0)}\033[0m"})

                                    for card in cards['hydra:member']:
                                        tempCard = map_jsoncard_to_card(card, dbcard.name_en)
                                        card_to_update = next((c for c in cards_to_update if c.reference == tempCard.reference), None)
                                        if card_to_update:
                                            # Initialiser un drapeau pour suivre les modifications
                                            has_updated = False

                                            # Vérifiez et mettez à jour uniquement si les valeurs sont différentes
                                            if str(card_to_update.name) != str(tempCard.name):
                                                card_to_update.name = tempCard.name
                                                has_updated = True
                                            if str(card_to_update.name_en) != str(tempCard.name_en) or card_to_update.name_en is None:
                                                card_to_update.name_en = tempCard.name_en
                                                has_updated = True
                                            if str(card_to_update.isSuspended).lower() != str(tempCard.isSuspended).lower():
                                                card_to_update.isSuspended = True if str(tempCard.isSuspended).lower() == 'true' else False
                                                has_updated = True
                                            if str(card_to_update.imagePath) != str(tempCard.imagePath):
                                                card_to_update.imagePath = tempCard.imagePath
                                                has_updated = True
                                            if tempCard.image_path_en is not None:
                                                if str(card_to_update.image_path_en) != str(tempCard.imagePath) or card_to_update.image_path_en is None:
                                                    card_to_update.image_path_en = tempCard.image_path_en
                                                    has_updated = True
                                            if str(card_to_update.MAIN_COST) != str(tempCard.MAIN_COST):
                                                card_to_update.MAIN_COST = tempCard.MAIN_COST
                                                has_updated = True
                                            if str(card_to_update.RECALL_COST) != str(tempCard.RECALL_COST):
                                                card_to_update.RECALL_COST = tempCard.RECALL_COST
                                                has_updated = True
                                            if str(card_to_update.MOUNTAIN_POWER) != str(tempCard.MOUNTAIN_POWER):
                                                card_to_update.MOUNTAIN_POWER = tempCard.MOUNTAIN_POWER
                                                has_updated = True
                                            if str(card_to_update.OCEAN_POWER) != str(tempCard.OCEAN_POWER):
                                                card_to_update.OCEAN_POWER = tempCard.OCEAN_POWER
                                                has_updated = True
                                            if str(card_to_update.FOREST_POWER) != str(tempCard.FOREST_POWER):
                                                card_to_update.FOREST_POWER = tempCard.FOREST_POWER
                                                has_updated = True
                                            if str(card_to_update.errated).lower() != str(tempCard.errated).lower():
                                                card_to_update.errated = True if str(tempCard.errated).lower() == 'true' else False
                                                has_updated = True
                                            if tempCard.main_effect_en is not None:
                                                if str(card_to_update.main_effect_en) != str(tempCard.main_effect_en) \
                                                    or card_to_update.main_effect_en is None:
                                                    card_to_update.main_effect_en = tempCard.main_effect_en
                                                    has_updated = True
                                            if tempCard.echo_effect_en is not None:
                                                if str(card_to_update.echo_effect_en) != str(tempCard.echo_effect_en) \
                                                    or card_to_update.echo_effect_en is None or tempCard.echo_effect_en is None:
                                                    card_to_update.echo_effect_en = tempCard.echo_effect_en
                                                    has_updated = True
                                            if card_to_update.created_at is None:
                                                card_to_update.created_at = datetime.now(timezone.utc)
                                                has_updated = True
                                            if card_to_update.MAIN_EFFECT is None and card_to_update.ECHO_EFFECT is None:
                                                detailsCard = card_routine.get_card_by_reference(tempCard.reference)
                                                if detailsCard:
                                                    temp_card = map_effect_to_card(tempCard, detailsCard)
                                                    card_to_update.MAIN_EFFECT = temp_card.MAIN_EFFECT
                                                    card_to_update.ECHO_EFFECT = temp_card.ECHO_EFFECT
                                                    card_to_update.subtype = temp_card.subtype
                                                    has_updated = True

                                            # Si une modification a été effectuée, mettre à jour `edited_at`
                                            if has_updated:
                                                socketio.emit('script_output', {'data': f"Mise à jour de la carte : {card_to_update.name_en} ({card_to_update.reference})"})
                                                card_to_update.edited_at = datetime.now(timezone.utc)
                                                
                                            continue
                                        detailsCard = card_routine.get_card_by_reference(tempCard.reference)
                                        if detailsCard:
                                            tempCard = map_effect_to_card(tempCard, detailsCard)
                                        cardToInsert.append(tempCard)
                                    session.commit()
                                    if len(cards['hydra:member']) < 36:
                                        break
                                    page += 1

                        if cardToInsert:
                            insert_cards_into_db(cardToInsert, session)
        except Exception as e:
            socketio.emit('script_output', {'data': f"\033[91mError : {e}\033[0m"})
        finally:
            session.close()

    def get_unique():
        print("----------- GET UNIQUE -----------")
        socketio.emit('script_output', {'data': "----------- GET UNIQUE -----------"})
        mainCosts = list(range(1, 11))
        recallCosts = list(range(1, 11))

        session = Session()
        try:
            # session.execute(text("TRUNCATE TABLE new_cards;"))
            # session.commit()
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
                worker_id = f"worker-{i+1}"
                futures.append(executor.submit(process_unique_cards, subset, mainCosts, recallCosts, start_index, count, worker_id, forceUpdate))

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
