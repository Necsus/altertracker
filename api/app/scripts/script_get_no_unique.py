from datetime import datetime
import time
from app.scripts import card_routine
from app.models.card import Card
from app.extensions import db, socketio

def run_script():
    start_time = time.time()

    nb_cards = 0
    def map_jsoncard_to_card(jsonCard, name_en = None) -> Card:
        card = Card(
            id_card = jsonCard['id'],
            reference = jsonCard['reference'],
            name = jsonCard['name'],
            name_en = name_en,
            faction = jsonCard['mainFaction']['reference'],
            rarity = jsonCard['rarity']['reference'],
            type = jsonCard['cardType']['reference'],
            set = jsonCard['cardSet']['reference'],
            imagePath = jsonCard['imagePath'],
            isSuspended = jsonCard['isSuspended'],
            MAIN_COST = jsonCard['elements']['MAIN_COST'],
            RECALL_COST = jsonCard['elements']['RECALL_COST'],
            MOUNTAIN_POWER = None if jsonCard['cardType']['reference'] != "CHARACTER" else jsonCard['elements']['MOUNTAIN_POWER'],
            OCEAN_POWER = None if jsonCard['cardType']['reference'] != "CHARACTER" else jsonCard['elements']['OCEAN_POWER'],
            FOREST_POWER = None if jsonCard['cardType']['reference'] != "CHARACTER" else jsonCard['elements']['FOREST_POWER'],
            MAIN_EFFECT = None,
            ECHO_EFFECT = None,
        )
        return card

    def map_name_en(card: Card, jsonCard) -> Card:
        card.name_en = jsonCard['name']
        return card

    def map_effect_to_card(card: Card, jsonCard) -> Card:
        card.MAIN_EFFECT = None if 'MAIN_EFFECT' not in jsonCard['elements'] else jsonCard['elements']['MAIN_EFFECT'],
        card.ECHO_EFFECT = None if 'ECHO_EFFECT' not in jsonCard['elements'] else jsonCard['elements']['ECHO_EFFECT'],
        return card

    def map_names(card: Card, name_fr: str, name_en: str):
        card.name = name_fr
        card.name_en = name_en
        card.edited_at = datetime.now()
        if card.created_at is None:
            card.created_at = datetime.now()
        db.session.commit()

    def insert_cards_into_db(cards):
        global nb_cards
        try:
            edit_card_len = 0
            add_card_len = 0
            for card in cards:
                # Vérifier si une carte avec le même id existe déjà
                existing_card = db.session.query(Card).filter_by(id_card=card.id_card).first()
                if existing_card:
                    # Mettre à jour les champs de la carte existante
                    existing_card.reference = card.reference
                    existing_card.name = card.name
                    existing_card.name_en = card.name_en
                    existing_card.faction = card.faction
                    existing_card.rarity = card.rarity
                    existing_card.type = card.type
                    existing_card.set = card.set
                    existing_card.imagePath = card.imagePath
                    existing_card.isSuspended = card.isSuspended
                    existing_card.MAIN_COST = card.MAIN_COST
                    existing_card.RECALL_COST = card.RECALL_COST
                    existing_card.MOUNTAIN_POWER = card.MOUNTAIN_POWER
                    existing_card.OCEAN_POWER = card.OCEAN_POWER
                    existing_card.FOREST_POWER = card.FOREST_POWER
                    existing_card.MAIN_EFFECT = card.MAIN_EFFECT
                    existing_card.ECHO_EFFECT = card.ECHO_EFFECT
                    existing_card.edited_at = datetime.now()
                    edit_card_len += 1
                else:
                    # Ajouter une nouvelle carte si elle n'existe pas
                    card.created_at = datetime.now()
                    db.session.add(card)
                    add_card_len += 1
            # Valider la transaction
            db.session.commit()
            nb_cards += len(cards)
            socketio.emit('script_output', {'data': f"\033[92mCartes insérées : {add_card_len}\033[0m"})
            socketio.emit('script_output', {'data': f"\033[92mCartes modifiées : {edit_card_len}\033[0m"})
            socketio.emit('script_output', {'data': f"\033[92mNombre total de cartes : {nb_cards}\033[0m"})
            # print(f"\033[92mCartes insérées : {add_card_len}\033[0m")
            # print(f"\033[92mCartes modifiées : {edit_card_len}\033[0m")
            # print(f"\033[92mNombre total de cartes : {nb_cards}\033[0m")
        except Exception as e:
            # Gérer les erreurs et annuler la transaction en cas d'échec
            socketio.emit('script_error', {'data': f"\033[91mErreur lors de l'insertion ou de la mise à jour des cartes : {e}\033[0m"})
            # print(f"\033[91mErreur lors de l'insertion ou de la mise à jour des cartes : {e}\033[0m")
            try:
                db.session.rollback()
            except Exception as rollback_error:
                socketio.emit('script_error', {'data': f"\033[91mErreur lors du rollback : {rollback_error}\033[0m"})
                # print(f"\033[91mErreur lors du rollback : {rollback_error}\033[0m")

    def get_no_unique(rarity: str):
        socketio.emit('script_output', {'data': f"----------- GET {rarity} -----------"})
        print(f"----------- GET {rarity} -----------")
        page = 1
        cardToInsert = []
        while True:
            socketio.emit('script_output', {'data': f"Récupération des cartes de la page {page}..."})
            # print(f"Récupération des cartes de la page {page}...")
            cards = card_routine.get_cards(page, rarity)

            if cards and cards.get('hydra:totalItems', 0) >= 1000:
                socketio.emit('script_output', {'data': f"\033[91mATTENTION TROP DE RESULTATS MANQUE DES CARTES"})
                # print(f"\033[91mATTENTION TROP DE RESULTATS MANQUE DES CARTES")


            if not cards or 'hydra:member' not in cards or not cards['hydra:member']:
                break

            references = [card['reference'] for card in cards['hydra:member']]
            details = {ref: card_routine.get_card_by_reference(ref) for ref in references}

            for card in cards['hydra:member']:
                tempCard = map_jsoncard_to_card(card)
                card_to_update = db.session.query(Card).filter_by(reference=tempCard.reference).first()
                if card_to_update:
                    socketio.emit('script_output', {'data': f"\rCarte {tempCard.reference} déjà existante. Passage à la suivante.[flush=True]"})
                    # print(f"\rCarte {tempCard.reference} déjà existante. Passage à la suivante.", end="", flush=True)
                    # Initialiser un drapeau pour suivre les modifications
                    has_updated = False

                    # Vérifiez et mettez à jour uniquement si les valeurs sont différentes
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
                
                socketio.emit('script_output', {'data': f"\rRécupération des stats de la carte {tempCard.reference}...[flush=True]"})
                # print(f"\rRécupération des stats de la carte {tempCard.reference}...", end="", flush=True)
                detailsCard = card_routine.get_card_by_reference(tempCard.reference)
                tempCard = map_effect_to_card(tempCard, detailsCard)
                name_en = card_routine.get_card_by_reference(tempCard.reference, True)
                tempCard = map_name_en(tempCard, name_en)
                cardToInsert.append(tempCard)

            # print()
            page += 1

        if cardToInsert:
            insert_cards_into_db(cardToInsert)

    get_no_unique('COMMON')
    get_no_unique('RARE')

    socketio.emit('script_output', {'data': f"Fin de l'insertion des cartes."})
    socketio.emit('script_output', {'data': f"Cartes scannées : {nb_cards}"})
    # print(f"Fin de l'insertion des cartes.")
    # print(f"Cartes scannées : {nb_cards}")

    # Fin du timer
    end_time = time.time()
    execution_time = end_time - start_time

    # Conversion en heures, minutes et secondes
    hours, remainder = divmod(execution_time, 3600)
    minutes, seconds = divmod(remainder, 60)

    socketio.emit('script_output', {'data': f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}"})
    print(f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
    socketio.emit('script_finished', {'status': 'done'})
    print(f"GET UNIQUE terminé")

