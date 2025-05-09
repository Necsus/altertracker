import asyncio
import aiohttp
import time
from app import create_app
from app.models.card import Card
from app.extensions import db

# Créer l'application Flask
app = create_app()

# Démarrer le timer
start_time = time.time()


with app.app_context():
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

    async def fetch_cards(session, url, params):
        """Effectuer une requête HTTP asynchrone pour récupérer les cartes."""
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            print(f"Erreur lors de la requête : {e}")
            return None

    async def process_card(session, card, cardToInsert):
        """Traiter une carte spécifique."""
        tempCard = map_jsoncard_to_card(card)
        print(f"\rRécupération des stats de la carte {tempCard.reference}...", end="", flush=True)

        # Récupérer les détails de la carte
        detailsCard = await fetch_cards(session, f"https://api.altered.gg/cards/{tempCard.reference}", {"locale": "fr-fr"})
        if detailsCard:
            tempCard = map_effect_to_card(tempCard, detailsCard)

        # Ajouter la carte à la liste
        cardToInsert.append(tempCard)

    async def process_page(session, dbcard, set, mainCost, recallCost, page, cardToInsert):
        """Traiter une page entière de cartes."""
        base_url = "https://api.altered.gg/cards"
        params = {
            "page": page,
            "cardSet[]": set,
            "cardType[]": "CHARACTER",
            "factions[]": dbcard.faction,
            "mainCost[]": mainCost,
            "recallCost[]": recallCost,
            "rarity[]": "UNIQUE",
            "translations.name": dbcard.name_en,
            "itemsPerPage": 36,
            "locale": "fr-fr"
        }

        cards = await fetch_cards(session, base_url, params)
        if not cards or 'hydra:member' not in cards or not cards['hydra:member']:
            return False  # Indiquer qu'il n'y a plus de cartes à traiter

        tasks = []
        for card in cards['hydra:member']:
            tasks.append(process_card(session, card, cardToInsert))

        # Exécuter toutes les tâches pour les cartes en parallèle
        await asyncio.gather(*tasks)
        return True

    async def process_dbcard(session, dbcard, set, mainCost, recallCost, cardToInsert):
        """Traiter toutes les pages pour une combinaison spécifique."""
        page = 1
        while True:
            print(f"Récupération des cartes de la page {page}...")
            has_more = await process_page(session, dbcard, set, mainCost, recallCost, page, cardToInsert)
            if not has_more:
                break
            page += 1

    async def process_all_cards(existing_cards, sets, mainCosts, recallCosts):
        """Traiter toutes les cartes en parallèle."""
        cardToInsert = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for index, dbcard in enumerate(existing_cards.values(), start=1):
                print(f"--- CARDNAME : {dbcard.name}  FACTION : {dbcard.faction}  |  {index}/{len(existing_cards)}")
                for set in sets:
                    if dbcard.set == 'ALIZE' and set != 'ALIZE':
                        continue
                    for mainCost in mainCosts:
                        for recallCost in recallCosts:
                            tasks.append(process_dbcard(session, dbcard, set, mainCost, recallCost, cardToInsert))

            # Exécuter toutes les tâches en parallèle
            await asyncio.gather(*tasks)

        # Insérer les cartes dans la base de données
        if cardToInsert:
            insert_cards_into_db(cardToInsert)

    # Exemple d'appel
    async def main():
        sets = ['COREKS', 'CORE', 'ALIZE']
        mainCosts = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        recallCosts = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        existing_cards = {
            card.id: card
            for card in Card.query.filter(Card.rarity == 'RARE', Card.type == 'CHARACTER')
            .order_by(Card.name_en.asc())
            .all()
        }

        await process_all_cards(existing_cards, sets, mainCosts, recallCosts)
        # Fin du timer
        end_time = time.time()
        execution_time = end_time - start_time

        print(f"Temps d'exécution : {execution_time:.2f} secondes")

    # Exécuter la fonction principale
    asyncio.run(main())