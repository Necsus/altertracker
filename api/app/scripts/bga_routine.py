import time
import requests
from app.models.cookie_manager import CookieManager
from app.config import ConfigEnv
from app.extensions import db
import json

def postLoginUserWithPassword() -> bool:
    url = "https://fr.boardgamearena.com/account/auth/loginUserWithPassword.html"
    formdata = {
        "username": ConfigEnv.BGA_USERNAME,
        "password": ConfigEnv.BGA_PASSWORD,
        "remember_me": 'true',
        "request_token": postGetRequestToken()
    }
    
    PHPSESSID = db.session.query(CookieManager).filter_by(name="PHPSESSID").first()
    
    if not PHPSESSID:
        print("\033[91m❌ PHPSESSID cookie not found in database\033[0m")
        return False
    
    headers = {
        "Cookie": f"PHPSESSID={PHPSESSID.value}",
        "accept": "*/*",
        "content-type": "multipart/form-data",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
    }
    
    # ✅ Print détails de la requête
    print("\n" + "="*80)
    print("📤 POST LOGIN REQUEST DETAILS")
    print("="*80)
    print(f"URL: {url}")
    print(f"\nHeaders:")
    for key, value in headers.items():
        if key == "Cookie":
            print(f"  {key}: PHPSESSID={PHPSESSID.value[:20]}...{PHPSESSID.value[-10:]}")
        else:
            print(f"  {key}: {value}")
    print(f"\nForm Data:")
    for key, value in formdata.items():
        if key == "password":
            print(f"  {key}: ********")
        elif key == "request_token":
            print(f"  {key}: {value[:30] if value else 'None'}...")
        else:
            print(f"  {key}: {value}")
    print("="*80 + "\n")
    
    try:
        response = requests.post(url, data=formdata, headers=headers)
        
        # ✅ Print détails de la réponse
        print("\n" + "="*80)
        print("📥 POST LOGIN RESPONSE DETAILS")
        print("="*80)
        print(f"Status Code: {response.status_code}")
        print(f"Reason: {response.reason}")
        print(f"\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print(f"\nCookies reçus:")
        for cookie in response.cookies:
            print(f"  {cookie.name}: {cookie.value[:20]}...{cookie.value[-10:] if len(cookie.value) > 30 else cookie.value}")
        
        response.raise_for_status()
        data = response.json()
        
        print(f"\nResponse Body:")
        print(f"  {json.dumps(data, indent=2)}")
        print("="*80 + "\n")
        
        # ✅ Vérifier le statut (peut être 'status' ou 'statut')
        status = data.get('status') or data.get('statut')
        if status != 1:
            print(f"\033[91m❌ Erreur postLoginUserWithPassword status : {status}\033[0m")
            return False
        
        # Récupérer et mettre à jour les cookies
        TournoiEnLigne_sso_user = db.session.query(CookieManager).filter_by(name="TournoiEnLigne_sso_user").first()
        TournoiEnLigne_sso_id = db.session.query(CookieManager).filter_by(name="TournoiEnLigne_sso_id").first()
        TournoiEnLigneidt = db.session.query(CookieManager).filter_by(name="TournoiEnLigneidt").first()
        TournoiEnLignetkt = db.session.query(CookieManager).filter_by(name="TournoiEnLignetkt").first()
        TournoiEnLigneid = db.session.query(CookieManager).filter_by(name="TournoiEnLigneid").first()
        TournoiEnLignetk = db.session.query(CookieManager).filter_by(name="TournoiEnLignetk").first()
        
        for cookie in response.cookies:
            if cookie.name == 'TournoiEnLigne_sso_user' and TournoiEnLigne_sso_user:
                TournoiEnLigne_sso_user.value = cookie.value
                print(f"✅ TournoiEnLigne_sso_user : {cookie.value[-10:]}...")
            elif cookie.name == 'TournoiEnLigne_sso_id' and TournoiEnLigne_sso_id:
                TournoiEnLigne_sso_id.value = cookie.value
                print(f"✅ TournoiEnLigne_sso_id : {cookie.value[-10:]}...")
            elif cookie.name == 'TournoiEnLigneidt' and TournoiEnLigneidt:
                TournoiEnLigneidt.value = cookie.value
                print(f"✅ TournoiEnLigneidt : {cookie.value[-10:]}...")
            elif cookie.name == 'TournoiEnLignetkt' and TournoiEnLignetkt:
                TournoiEnLignetkt.value = cookie.value
                print(f"✅ TournoiEnLignetkt : {cookie.value[-10:]}...")
            elif cookie.name == 'TournoiEnLigneid' and TournoiEnLigneid:
                TournoiEnLigneid.value = cookie.value
                print(f"✅ TournoiEnLigneid : {cookie.value[-10:]}...")
            elif cookie.name == 'TournoiEnLignetk' and TournoiEnLignetk:
                TournoiEnLignetk.value = cookie.value
                print(f"✅ TournoiEnLignetk : {cookie.value[-10:]}...")
        
        db.session.commit()
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\033[91m❌ Erreur lors de la requête : {e}\033[0m")
        return False
    except Exception as e:
        print(f"\033[91m❌ Erreur inattendue : {e}\033[0m")
        import traceback
        traceback.print_exc()
        return False


def postGetRequestToken() -> str:
    url = "https://fr.boardgamearena.com/account/auth/getRequestToken.html"
    formdata = {
        "bgapp": "bga"
    }
    headers = {
        "accept": "*/*",
        "content-type": "multipart/form-data",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
    }
    
    # ✅ Print détails de la requête
    print("\n" + "="*80)
    print("📤 GET REQUEST TOKEN DETAILS")
    print("="*80)
    print(f"URL: {url}")
    print(f"\nHeaders:")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    print(f"\nForm Data:")
    for key, value in formdata.items():
        print(f"  {key}: {value}")
    print("="*80 + "\n")
    
    try:
        response = requests.post(url, data=formdata, headers=headers)
        
        # ✅ Print détails de la réponse
        print("\n" + "="*80)
        print("📥 GET REQUEST TOKEN RESPONSE")
        print("="*80)
        print(f"Status Code: {response.status_code}")
        print(f"\nCookies reçus:")
        for cookie in response.cookies:
            print(f"  {cookie.name}: {cookie.value[:20]}...{cookie.value[-10:] if len(cookie.value) > 30 else cookie.value}")
        
        response.raise_for_status()
        data = response.json()
        
        print(f"\nResponse Body:")
        print(f"  {json.dumps(data, indent=2)}")
        print("="*80 + "\n")
        
        # ✅ Vérifier le statut (peut être 'status' ou 'statut')
        status = data.get('status') or data.get('statut')
        if status != 1:
            print(f"\033[91m❌ Erreur postGetRequestToken status : {status}\033[0m")
            return None
        
        PHPSESSID = db.session.query(CookieManager).filter_by(name="PHPSESSID").first()
        
        if not PHPSESSID:
            print("\033[91m❌ PHPSESSID cookie not found in database\033[0m")
            return None
        
        for cookie in response.cookies:
            if cookie.name == 'PHPSESSID':
                PHPSESSID.value = cookie.value
                print(f"✅ PHPSESSID : {cookie.value[-10:]}...")
        
        # ✅ Gérer différentes structures de réponse
        request_token = data.get('data', {}).get('request_token') if isinstance(data.get('data'), dict) else None
        
        if not request_token:
            print(f"\033[91m❌ Request token not found in response\033[0m")
            return None
            
        print(f"✅ Request Token : {request_token[:30]}...")
        db.session.commit()
        return request_token
        
    except requests.exceptions.RequestException as e:
        print(f"\033[91m❌ Erreur lors de la requête : {e}\033[0m")
        return None
    except Exception as e:
        print(f"\033[91m❌ Erreur inattendue : {e}\033[0m")
        import traceback
        traceback.print_exc()
        return None


def getSearch(query: str, retry: bool = True) -> dict:
    try:
        url = "https://boardgamearena.com/omnibar/omnibar/search.html"
        params = {
            "query": query,
        }
        
        # Récupérer les cookies
        TournoiEnLigne_sso_user = db.session.query(CookieManager).filter_by(name="TournoiEnLigne_sso_user").first()
        TournoiEnLigne_sso_id = db.session.query(CookieManager).filter_by(name="TournoiEnLigne_sso_id").first()
        TournoiEnLigneidt = db.session.query(CookieManager).filter_by(name="TournoiEnLigneidt").first()
        TournoiEnLignetkt = db.session.query(CookieManager).filter_by(name="TournoiEnLignetkt").first()
        TournoiEnLigneid = db.session.query(CookieManager).filter_by(name="TournoiEnLigneid").first()
        TournoiEnLignetk = db.session.query(CookieManager).filter_by(name="TournoiEnLignetk").first()
        
        # ✅ Vérifier que tous les cookies existent
        if not all([TournoiEnLigne_sso_user, TournoiEnLigne_sso_id, TournoiEnLigneidt, 
                    TournoiEnLignetkt, TournoiEnLigneid, TournoiEnLignetk]):
            print("\033[91m❌ Cookies manquants, tentative de connexion...\033[0m")
            if retry:
                postLoginUserWithPassword()
                time.sleep(1)
                return getSearch(query, retry=False)
            else:
                return {'status': 0, 'error': 'Missing cookies', 'players': []}
        
        headers = {
            "cookie": f"TournoiEnLigne_sso_user={TournoiEnLigne_sso_user.value};TournoiEnLigne_sso_id={TournoiEnLigne_sso_id.value};TournoiEnLignetkt={TournoiEnLignetkt.value};TournoiEnLigneidt={TournoiEnLigneidt.value};TournoiEnLignetk={TournoiEnLignetk.value};TournoiEnLigneid={TournoiEnLigneid.value}",
            "x-request-token": TournoiEnLigneidt.value,
            "accept": "*/*",
            "content-type": "multipart/form-data",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
        }
        
        # ✅ Print détails de la requête
        print("\n" + "="*80)
        print("📤 SEARCH REQUEST DETAILS")
        print("="*80)
        print(f"URL: {url}")
        print(f"Query: {query}")
        print(f"\nHeaders:")
        for key, value in headers.items():
            if key == "cookie":
                print(f"  {key}:")
                print(f"    TournoiEnLigne_sso_user: ...{TournoiEnLigne_sso_user.value[-10:]}")
                print(f"    TournoiEnLigne_sso_id: ...{TournoiEnLigne_sso_id.value[-10:]}")
                print(f"    TournoiEnLignetkt: ...{TournoiEnLignetkt.value[-10:]}")
                print(f"    TournoiEnLigneidt: ...{TournoiEnLigneidt.value[-10:]}")
                print(f"    TournoiEnLignetk: ...{TournoiEnLignetk.value[-10:]}")
                print(f"    TournoiEnLigneid: ...{TournoiEnLigneid.value[-10:]}")
            else:
                print(f"  {key}: {value[:50] if len(value) > 50 else value}")
        print("="*80 + "\n")
        
        response = requests.get(url, headers=headers, params=params)
        
        # ✅ Print détails de la réponse
        print("\n" + "="*80)
        print("📥 SEARCH RESPONSE DETAILS")
        print("="*80)
        print(f"Status Code: {response.status_code}")
        print(f"Reason: {response.reason}")
        print(f"\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        response.raise_for_status()
        data = response.json()
        
        print(f"\nResponse Body (full):")
        print(json.dumps(data, indent=2))
        print("="*80 + "\n")
        
        # ✅ Gérer si data est une liste ou un dict
        if isinstance(data, list):
            print(f"\033[93m⚠️  Response is a list, not a dict. Converting...\033[0m")
            return {
                'status': 1,
                'players': [
                    {
                        'bga_id': player.get('id'),
                        'name': player.get('fullname') or player.get('name'),
                        'country': player.get('country_infos', {}).get('code') or player.get('country', 'XX')
                    }
                    for player in data
                ]
            }
        
        # ✅ Si c'est un dict, vérifier le status
        status = data.get('status') or data.get('statut')
        if status != 1:
            print(f"\033[91m❌ Erreur lors de la recherche BGA : status={status}\033[0m")
            
            if retry:
                print(f"\033[93m🔄 Tentative de récupération du token...\033[0m")
                time.sleep(1)
                postLoginUserWithPassword()
                time.sleep(1)
                return getSearch(query, retry=False)
            
            return {'status': 0, 'error': 'BGA API error', 'players': []}
        
        # ✅ Extraire les joueurs
        players_data = data.get('data', {})
        if isinstance(players_data, dict):
            players_list = players_data.get('players', [])
        elif isinstance(players_data, list):
            players_list = players_data
        else:
            players_list = []
        
        # Transformer les données
        result = {
            'status': status,
            'players': [
                {
                    'bga_id': player.get('id'),
                    'name': player.get('fullname') or player.get('name'),
                    'country': player.get('country_infos', {}).get('code') if isinstance(player.get('country_infos'), dict) else player.get('country', 'XX')
                }
                for player in players_list
            ]
        }
        print(f"✅ Recherche BGA réussie : {len(result['players'])} joueur(s) trouvé(s)")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"\033[91m❌ Erreur lors de la requête : {e}\033[0m")
        if retry:
            print(f"\033[93m🔄 Tentative de récupération du token...\033[0m")
            time.sleep(1)
            postLoginUserWithPassword()
            time.sleep(1)
            return getSearch(query, retry=False)
        else:
            return {'status': 0, 'error': str(e), 'players': []}
    except Exception as e:
        print(f"\033[91m❌ Erreur inattendue : {e}\033[0m")
        import traceback
        traceback.print_exc()
        return {'status': 0, 'error': str(e), 'players': []}