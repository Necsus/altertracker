import datetime
import time
import requests
from urllib.parse import urlencode
from app.models.cookie_manager import CookieManager

_token = None
_expires = None

def get_cards(page: int, set: str, rarity: str):
    time.sleep(0.1)
    base_url = "https://api.altered.gg/public/cards"
    params = {
        "page": page,
        "cardSet[]": set,
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

    headers = {
        "accept": "*/*",
        "user-agent": "AlterTracker/1.0 (necsus.dev@proton.me)",
        "authorization": "AlterTracker"
    }

    # Construire l'URL avec les paramètres encodés
    url = f"{base_url}?{urlencode(params, doseq=True)}"
    try:
        # Effectuer une requête GET vers l'URL
        response = requests.get(url, headers=headers)
        
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
        print(f"\033[91mErreur lors de la requête : {e}")
        return None
    
def get_unique_cards_name_faction(name: str, faction: str, set: str, mainCost: int, recallCost: int, forestPower: list[str], page: int):
    time.sleep(0.1)
    base_url = "https://api.altered.gg/public/cards"
    params = {
        "page": page,
        "cardSet[]": set,
        "cardType[]": "CHARACTER",
        "factions[]": faction,
        "forestPower[]": forestPower,
        "mainCost[]": mainCost,
        "recallCost[]": recallCost,
        "rarity[]": "UNIQUE",
        "query": f"\"{name}\"",
        "itemsPerPage": 30,
        "locale": "fr-fr"
    }

    headers = {
        "accept": "*/*",
        "user-agent": "AlterTracker/1.0 (necsus.dev@proton.me)",
        "authorization": "AlterTracker"
    }

    # Construire l'URL avec les paramètres encodés
    url = f"{base_url}?{urlencode(params, doseq=True)}"
    try:
        # Effectuer une requête GET vers l'URL
        response = requests.get(url, headers=headers)
        
        # Vérifier si la requête a réussi (code 200)
        response.raise_for_status()

        # Récupérer les données au format JSON
        data = response.json()
        print(len(data['hydra:member']))
        if data['hydra:totalItems'] <= 0:
            return None

        # Retourner les données
        return data
    except requests.exceptions.RequestException as e:
        # Gérer les erreurs de requête
        print(f"\033[91mErreur lors de la requête : {e}\033[0m")
        return None

def get_card_by_reference(card_reference: str, en: bool = False):
    time.sleep(0.1)
    base_url = f"https://api.altered.gg/public/cards/{card_reference}"
    params = {
        "locale": "en-us" if en else "fr-fr"
    }

    headers = {
        "accept": "*/*",
        "user-agent": "AlterTracker/1.0 (necsus.dev@proton.me)",
        "authorization": "AlterTracker"
    }

    url = f"{base_url}?{urlencode(params, doseq=True)}"
    try:
        # Effectuer une requête GET vers l'URL
        response = requests.get(url, headers=headers)
        
        # Vérifier si la requête a réussi (code 200)
        response.raise_for_status()
        
        # Récupérer les données au format JSON
        print(url)
        data = response.json()
        
        # Retourner les données
        return data
    except requests.exceptions.RequestException as e:
        # Gérer les erreurs de requête
        print(f"\033[91mErreur lors de la requête : {e}\033[0m")
        return None

def get_offer_by_reference(session, reference: str, retry: bool = True):
    time.sleep(0.4)
    base_url = f"https://api.altered.gg/cards/{reference}/offers?itemsPerPage=10&page=1"
    token = getToken(session)
    headers = {
        "authorization": f"Bearer {token}",
        "accept": "*/*"
    }
    try:
        # Effectuer une requête GET vers l'URL
        response = requests.get(base_url, headers=headers)
        
        # Vérifier si la requête a réussi (code 200)
        response.raise_for_status()

        # Récupérer les données au format JSON
        data = response.json()
        
        if data['hydra:totalItems'] <= 0 or len(data['hydra:member']) <= 0:
            return None
        
        # Retourner les données
        return data['hydra:member']
    except requests.exceptions.RequestException as e:
        if retry:
            print(f"\033[93mTentative de récupération du token...\033[0m")
            time.sleep(1)
            getToken(session, True)
            return get_offer_by_reference(session, reference, retry=False)
        else:
            print(f"\033[91mErreur lors de la requête : {e}\033[0m")
            return None
    
def _iso_to_timestamp(iso_str):
    # Gère le format ISO 8601 avec ou sans millisecondes
    try:
        dt = datetime.datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        dt = datetime.datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")
    return dt.replace(tzinfo=datetime.timezone.utc).timestamp()
    
def getToken(session, clearToken: bool = False) -> str:
    global _token, _expires
    if clearToken:
        _token = None
        _expires = None
    elif _token:
        return _token
    try:
        _token0 = session.query(CookieManager).filter_by(name="__Secure-next-auth.session-token.0").first()
        _token1 = session.query(CookieManager).filter_by(name="__Secure-next-auth.session-token.1").first()
        _callback = session.query(CookieManager).filter_by(name="__Secure-next-auth.callback-url").first()
        headers = {
            "Cookie": f"__Secure-next-auth.callback-url={_callback.value};__Secure-next-auth.session-token.0={_token0.value};__Secure-next-auth.session-token.1={_token1.value}",
            "accept": "*/*"
        }
        response = requests.get("https://www.altered.gg/api/auth/session", headers=headers)
        response.raise_for_status()

        for cookie in response.cookies:
            if cookie.name == '__Secure-next-auth.session-token.0':
                print(f"token.0 : {cookie.value[-10:]}...")
                _token0.value = cookie.value
            elif cookie.name == '__Secure-next-auth.session-token.1':
                print(f"token.1 : {cookie.value[-10:]}...")
                _token1.value = cookie.value
        session.commit()
        data = response.json()
        _token = data['accessToken']
        _expires = data['expires']
        return _token
    except requests.exceptions.RequestException as e:
        print(f"\033[91mErreur lors de la récupération du token : {e}\033[0m")

def get_unique_offers(session, name: str, faction: str, set: str, page: int, retry: bool = True):
    time.sleep(0.4)
    base_url = "https://api.altered.gg/cards/stats"
    params = {
        "page": page,
        "factions[]": faction,
        "inSale": "true",
        "rarity[]": "UNIQUE",
        "cardSet[]": set,
        "query": f"\"{name}\"",
        "itemsPerPage": 36,
        "locale": "en-us"
    }
    token = getToken(session)
    headers = {
        "authorization": f"Bearer {token}",
        "accept": "*/*",
        "user-agent": "insomnia/11.0.2"
    }

    # Construire l'URL avec les paramètres encodés
    url = f"{base_url}?{urlencode(params, doseq=True)}"
    # print(f"🔄 URL: {url}")
    # print(f"📋 Headers envoyés:")
    # for key, value in headers.items():
    #     if key == "authorization":
    #         print(f"  {key}: Bearer {value[-10:]}...")  # Masque le token
    #     else:
    #         print(f"  {key}: {value}")
    
    # start_time = time.time()
    try:
        # Effectuer une requête GET vers l'URL
        response = requests.get(url, headers=headers)

        # elapsed_time = time.time() - start_time
        # print(f"⏱️ Temps de réponse: {elapsed_time:.2f}s")
        # print(f"📨 Status code: {response.status_code}")
        # print(f"📋 Headers de réponse:")
        
        # Vérifier si la requête a réussi (code 200)
        response.raise_for_status()
        
        # Récupérer les données au format JSON
        data = response.json()
        if data['hydra:totalItems'] <= 0:
            return None
        
        if data['hydra:totalItems'] >= 1000:
            print(params)
        # print(data['hydra:totalItems'])
        # Retourner les données
        return data
    except requests.exceptions.RequestException as e:
        if retry:
            print(f"\033[93mTentative de récupération du token...\033[0m")
            time.sleep(1)
            getToken(session, True)
            return get_unique_offers(session, name, faction, set, page, retry=False)
        else:
            print(f"\033[91mErreur lors de la requête : {e}\033[0m")
            return None