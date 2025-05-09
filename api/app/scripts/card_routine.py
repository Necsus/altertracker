import requests
from urllib.parse import urlencode

def get_cards(page: int, rarity: str):
    base_url = "https://api.altered.gg/cards"
    params = {
        "page": page,
        "cardSet[]": ["CORE", "ALIZE"],
        "cardType[]": [
            "EXPEDITION_PERMANENT",
            "CHARACTER",
            "PERMANENT",
            "SPELL",
            "LANDMARK_PERMANENT"
        ],
        "rarity[]": rarity,
        "itemsPerPage": 36,
        "locale": "fr-fr"
    }

    # Construire l'URL avec les paramètres encodés
    url = f"{base_url}?{urlencode(params, doseq=True)}"
    try:
        # Effectuer une requête GET vers l'URL
        response = requests.get(url)
        
        # Vérifier si la requête a réussi (code 200)
        response.raise_for_status()
        
        # Récupérer les données au format JSON
        data = response.json()
        
        if data['hydra:totalItems'] <= 0:
            return None

        # Retourner les données
        return data
    except requests.exceptions.RequestException as e:
        # Gérer les erreurs de requête
        print(f"Erreur lors de la requête : {e}")
        return None
    
def get_unique_cards_name_faction(name: str, faction: str, set: str, mainCost: int, page: int):
    base_url = "https://api.altered.gg/cards"
    params = {
        "page": page,
        "cardSet[]": set,
        "cardType[]": "CHARACTER",
        "factions[]": faction,
        "mainCost[]": mainCost,
        "rarity[]": "UNIQUE",
        "translations.name": f"\"{name}\"",
        "itemsPerPage": 36,
        "locale": "fr-fr"
    }

    # Construire l'URL avec les paramètres encodés
    url = f"{base_url}?{urlencode(params, doseq=True)}"
    try:
        # Effectuer une requête GET vers l'URL
        response = requests.get(url)
        
        # Vérifier si la requête a réussi (code 200)
        response.raise_for_status()
        
        # Récupérer les données au format JSON
        data = response.json()

        if data['hydra:totalItems'] <= 0:
            return None

        # Retourner les données
        return data
    except requests.exceptions.RequestException as e:
        # Gérer les erreurs de requête
        print(f"Erreur lors de la requête : {e}")
        return None

def get_card_by_id(card_reference: str, en: bool = False):
    base_url = f"https://api.altered.gg/cards/{card_reference}"
    params = {
        "locale": "en-us" if en else "fr-fr"
    }
    url = f"{base_url}?{urlencode(params, doseq=True)}"
    try:
        # Effectuer une requête GET vers l'URL
        response = requests.get(url)
        
        # Vérifier si la requête a réussi (code 200)
        response.raise_for_status()
        
        # Récupérer les données au format JSON
        data = response.json()
        
        # Retourner les données
        return data
    except requests.exceptions.RequestException as e:
        # Gérer les erreurs de requête
        print(f"Erreur lors de la requête : {e}")
        return None