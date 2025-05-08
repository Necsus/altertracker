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

    def map_effect_to_cards(card: Card, jsonCard) -> Card:
        card.MAIN_EFFECT = None if 'MAIN_EFFECT' not in jsonCard['elements'] else jsonCard['elements']['MAIN_EFFECT'],
        card.ECHO_EFFECT = None if 'ECHO_EFFECT' not in jsonCard['elements'] else jsonCard['elements']['ECHO_EFFECT'],
        return card

    def insert_cards_into_db(cards):
        try:
            for card in cards:
                # Vérifier si une carte avec le même id existe déjà
                existing_card = Card.query.get(card.id)
                if existing_card:
                    # Mettre à jour les champs de la carte existante
                    existing_card.reference = card.reference
                    existing_card.name = card.name
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
                else:
                    # Ajouter une nouvelle carte si elle n'existe pas
                    db.session.add(card)
                # Valider la transaction
                db.session.commit()
                print(f"{len(cards)} cartes insérées avec succès dans la base de données.")
        except Exception as e:
            # Gérer les erreurs et annuler la transaction en cas d'échec
            db.session.rollback()
            print(f"Erreur lors de l'insertion des cartes : {e}")

    def get_communes():
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
                print(f"Récupération des stats de la carte {tempCard.reference}...")
                detailsCard = card_routine.get_card_by_id(tempCard.reference)
                tempCard = map_effect_to_cards(tempCard, detailsCard)
                cardToInsert.append(tempCard)
            
            # Passer à la page suivante
            page += 1
        # Isnérer dans la db
        insert_cards_into_db(cardToInsert)

    def get_rare():
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
                print(f"Récupération des stats de la carte {tempCard.reference}...")
                detailsCard = card_routine.get_card_by_id(tempCard.reference)
                tempCard = map_effect_to_cards(tempCard, detailsCard)
                cardToInsert.append(tempCard)
            
            # Passer à la page suivante
            page += 1


        # Isnérer dans la db
        insert_cards_into_db(cardToInsert)

get_communes()
get_rare()

# Fin du timer
end_time = time.time()
execution_time = end_time - start_time

print ("Fin de l'insertion des cartes.")
print(f"Temps d'exécution : {execution_time:.2f} secondes")






