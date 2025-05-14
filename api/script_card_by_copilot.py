from datetime import datetime
import time
from app import create_app
from app.scripts import auth, card_routine
from app.models.card import Card
from app.extensions import db

# Créer l'application Flask
app = create_app()

# Démarrer le timer
start_time = time.time()

with app.app_context():  # Activer le contexte de l'application
    token = auth.get_token()

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
            print(f"\033[92mCartes insérées : {add_card_len}\033[0m")
            print(f"\033[92mCartes modifiées : {edit_card_len}\033[0m")
            print(f"\033[92mNombre total de cartes : {nb_cards}\033[0m")
        except Exception as e:
            # Gérer les erreurs et annuler la transaction en cas d'échec
            print(f"\033[91mErreur lors de l'insertion ou de la mise à jour des cartes : {e}\033[0m")
            try:
                db.session.rollback()
            except Exception as rollback_error:
                print(f"\033[91mErreur lors du rollback : {rollback_error}\033[0m")

    def get_no_unique(rarity: str):
        print(f"----------- GET {rarity} -----------")
        page = 1
        cardToInsert = []
        while True:
            print(f"Récupération des cartes de la page {page}...")
            cards = card_routine.get_cards(page, rarity)

            if not cards or 'hydra:member' not in cards or not cards['hydra:member']:
                break

            references = [card['reference'] for card in cards['hydra:member']]
            details = {ref: card_routine.get_card_by_reference(ref) for ref in references}

            for card in cards['hydra:member']:
                tempCard = map_jsoncard_to_card(card)
                if db.session.query(Card.id_card).filter_by(id_card=tempCard.id_card).first():
                    print(f"\rCarte {tempCard.reference} déjà existante. Passage à la suivante.", end="", flush=True)
                    continue

                print(f"\rRécupération des stats de la carte {tempCard.reference}...", end="", flush=True)
                tempCard = map_effect_to_card(tempCard, details[tempCard.reference])
                cardToInsert.append(tempCard)

            print()
            page += 1

        if cardToInsert:
            insert_cards_into_db(cardToInsert)

    def get_unique():
        print(f"----------- GET UNIQUE -----------")
        sets = ['COREKS', 'CORE', 'ALIZE', 'BISE']
        mainCosts = list(range(1, 11))
        recallCosts = list(range(1, 11))
        forestPowers = list(range(0, 11))

        existing_cards = {
            card.id: card
            for card in Card.query.filter(Card.rarity == 'RARE', Card.type == 'CHARACTER')
            .order_by(Card.name_en.asc())
            .all()
        }

        total_cards = len(existing_cards)
        for index, dbcard in enumerate(existing_cards.values(), start=1):
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
                            print(f"--- CARDNAME : {dbcard.name}  FACTION : {dbcard.faction}  SET : {set}  MAIN_COST : {mainCost}  RECALL_COST : {recallCost}  |  {index}/{total_cards}")
                            page = 1
                            while True:
                                print(f"Récupération des cartes de la page {page}...")
                                cards = card_routine.get_unique_cards_name_faction(
                                    dbcard.name_en, dbcard.faction, set, mainCost, recallCost, forestPowers, page
                                )

                                if not cards or 'hydra:member' not in cards or not cards['hydra:member']:
                                    break

                                for card in cards['hydra:member']:
                                    tempCard = map_jsoncard_to_card(card, dbcard.name_en)
                                    if db.session.query(Card.id_card).filter_by(id_card=tempCard.id_card).first():
                                        print(f"\rCarte {tempCard.reference} déjà existante. Passage à la suivante.", end="", flush=True)
                                        continue

                                    print(f"\rRécupération des stats de la carte {tempCard.reference}...", end="", flush=True)
                                    detailsCard = card_routine.get_card_by_reference(tempCard.reference)
                                    tempCard = map_effect_to_card(tempCard, detailsCard)
                                    cardToInsert.append(tempCard)

                                print()
                                page += 1

                        if cardToInsert:
                            insert_cards_into_db(cardToInsert)

    get_no_unique('COMMON')
    get_no_unique('RARE')
    get_unique()

    print(f"Fin de l'insertion des cartes.")
    print(f"Cartes scannées : {nb_cards}")

# Fin du timer
end_time = time.time()
execution_time = end_time - start_time

# Conversion en heures, minutes et secondes
hours, remainder = divmod(execution_time, 3600)
minutes, seconds = divmod(remainder, 60)

print(f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}")