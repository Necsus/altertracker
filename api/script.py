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

    def map_jsoncard_to_card(jsonCard) -> Card:
        card = Card(
            id = jsonCard['id'],
            reference = jsonCard['reference'],
            name = jsonCard['name'],
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
                existing_card = db.session.get(Card, card.id)
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
                    edit_card_len += 1
                else:
                    add_card_len += 1
                    # Ajouter une nouvelle carte si elle n'existe pas
                    db.session.add(card)
            # Valider la transaction
            db.session.commit()
            nb_cards += len(cards)
            print(f"Cartes insérées : {add_card_len}")
            print(f"Cartes modifiées : {edit_card_len}")
            print(f"Nombre total de cartes : {len(cards)}")
        except Exception as e:
            # Gérer les erreurs et annuler la transaction en cas d'échec
            print(f"Erreur lors de l'insertion ou de la mise à jour des cartes : {e}")
            try:
                db.session.rollback()
            except Exception as rollback_error:
                print(f"Erreur lors du rollback : {rollback_error}")

    def get_communes():
        print(f"----------- GET COMMUNES -----------")
        page = 1
        cardToInsert = []
        while True:  # Boucle infinie, on sortira avec un break
            # Récupérer les données pour la page actuelle
            print(f"Récupération des cartes de la page {page}...")
            cards = card_routine.get_cards(page, 'COMMON')
            
            # Vérifier si communes est vide ou None
            if not cards or 'hydra:member' not in cards or not cards['hydra:member']:
                break  # Sortir de la boucle si aucune donnée n'est retournée

            # Ajouter les cartes à la liste
            for card in cards['hydra:member']:
                tempCard = map_jsoncard_to_card(card)
                print(f"\rRécupération des stats de la carte {tempCard.reference}...", end="", flush=True)
                detailsCard = card_routine.get_card_by_id(tempCard.reference)
                tempCard = map_effect_to_card(tempCard, detailsCard)
                name_en = card_routine.get_card_by_id(tempCard.reference, en=True)
                tempCard = map_name_en(tempCard, name_en)
                cardToInsert.append(tempCard)
            print()
            
            # Passer à la page suivante
            page += 1
        # Isnérer dans la db
        insert_cards_into_db(cardToInsert)

    def get_rare():
        print(f"----------- GET RARES -----------")
        page = 1
        cardToInsert = []
        while True:  # Boucle infinie, on sortira avec un break
            # Récupérer les données pour la page actuelle
            print(f"Récupération des cartes de la page {page}...")
            cards = card_routine.get_cards(page, 'RARE')
            
            # Vérifier si communes est vide ou None
            if not cards or 'hydra:member' not in cards or not cards['hydra:member']:
                break  # Sortir de la boucle si aucune donnée n'est retournée

            # Ajouter les cartes à la liste
            for card in cards['hydra:member']:
                tempCard = map_jsoncard_to_card(card)
                print(f"\rRécupération des stats de la carte {tempCard.reference}...", end="", flush=True)
                detailsCard = card_routine.get_card_by_id(tempCard.reference)
                tempCard = map_effect_to_card(tempCard, detailsCard)
                name_en = card_routine.get_card_by_id(tempCard.reference, True)
                tempCard = map_name_en(tempCard, name_en)
                cardToInsert.append(tempCard)
            print()

            # Passer à la page suivante
            page += 1


        # Insérer dans la db
        insert_cards_into_db(cardToInsert)

    def get_unique():
        print(f"----------- GET UNIQUE -----------")
        sets = ['COREKS', 'CORE', 'ALIZE']
        mainCosts = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        recallCosts = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        existing_cards = {
            card.id: card
            for card in Card.query.filter(Card.rarity == 'RARE', Card.type == 'CHARACTER')
            .order_by(Card.name_en.asc())  # Trier par ordre alphabétique croissant sur name_en
            .all()
        }
        for dbcard in existing_cards.values():
            print(f"--- CARDNAME : {dbcard.name}  FACTION : {dbcard.faction}")
            for set in sets:
                if dbcard.set == 'ALIZE' and set != 'ALIZE':
                    continue
                print(f"--- SET : {set}...")
                for mainCost in mainCosts:
                    print(f"--- MAIN_COST : {mainCost}")
                    for recallCost in recallCosts:
                        print(f"--- RECALL_COST : {recallCost}")
                        page = 1
                        cardToInsert = []
                        while True:  # Boucle infinie, on sortira avec un break
                            # Récupérer les données pour la page actuelle
                            print(f"Récupération des cartes de la page {page}...")
                            cards = card_routine.get_unique_cards_name_faction(dbcard.name_en, dbcard.faction, set, mainCost, recallCost, page)
                            
                            # Vérifier si communes est vide ou None
                            if not cards or 'hydra:member' not in cards or not cards['hydra:member']:
                                break  # Sortir de la boucle si aucune donnée n'est retournée

                            # Ajouter les cartes à la liste
                            for card in cards['hydra:member']:
                                tempCard = map_jsoncard_to_card(card)
                                existing_card = db.session.get(Card, tempCard.id)
                                if existing_card:
                                    print(f"\rCarte {tempCard.reference} déjà existante. Passage à la suivante.", end="", flush=True)
                                    continue  # Passer à l'itération suivante si la carte n'est pas trouvée
                                print(f"\rRécupération des stats de la carte {tempCard.reference}...", end="", flush=True)
                                detailsCard = card_routine.get_card_by_id(tempCard.reference)
                                tempCard = map_effect_to_card(tempCard, detailsCard)
                                cardToInsert.append(tempCard)
                            print()

                            # Passer à la page suivante
                            page += 1

                        # Insérer dans la db
                        insert_cards_into_db(cardToInsert)

    # get_communes()
    # get_rare()
    get_unique()

    print(f"Fin de l'insertion des cartes.")
    print(f"Cartes scannées : {nb_cards}")

# Fin du timer
end_time = time.time()
execution_time = end_time - start_time

print(f"Temps d'exécution : {execution_time:.2f} secondes")