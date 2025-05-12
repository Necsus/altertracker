import requests

def get_token() -> str:
    url = "https://www.altered.gg/api/auth/session"
    try:
        # Effectuer une requête GET vers l'URL
        response = requests.get(url)
        
        # Vérifier si la requête a réussi (code 200)
        response.raise_for_status()
        
        # Récupérer les données au format JSON
        data = response.json()
        
        # Test si le token d'accès est présent dans la réponse
        if 'accessToken' not in data:
            return generate_token()
        return data.accessToken
    except requests.exceptions.RequestException as e:
        # Gérer les erreurs de requête
        print(f"Erreur lors de la requête : {e}")
        return None
    
def generate_token() -> str:
    # TODO ne pas hardcoder le token
    return ""