import time
import requests
from app.models.cookie_manager import CookieManager
from app.config import ConfigEnv
from app.extensions import db

def postLoginUserWithPassword() -> bool:
    url = "https://fr.boardgamearena.com/account/auth/loginUserWithPassword.html"
    formdata = {
        "username": ConfigEnv.BGA_USERNAME,
        "password": ConfigEnv.BGA_PASSWORD,
        "remember_me": 'true',
        "request_token": postGetRequestToken()
    }
    PHPSESSID = db.query(CookieManager).filter_by(name="PHPSESSID").first()
    headers = {
        "Cookie": f"PHPSESSID={PHPSESSID.value}",
        "accept": "*/*",
        "content-type": "multipart/form-data",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
    }
    try:
        response = requests.post(url, data=formdata, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['statut'] is not 1:
            print(f"\033[91mErreur lors de la requête statut : {data['statut']}")
            return False
        TournoiEnLigne_sso_user = db.query(CookieManager).filter_by(name="TournoiEnLigne_sso_user").first()
        TournoiEnLigne_sso_id = db.query(CookieManager).filter_by(name="TournoiEnLigne_sso_id").first()
        TournoiEnLigneidt = db.query(CookieManager).filter_by(name="TournoiEnLigneidt").first()
        TournoiEnLignetkt = db.query(CookieManager).filter_by(name="TournoiEnLignetkt").first()
        TournoiEnLigneid = db.query(CookieManager).filter_by(name="TournoiEnLigneid").first()
        TournoiEnLignetk = db.query(CookieManager).filter_by(name="TournoiEnLignetk").first()
        for cookie in response.cookies:
            if cookie.name == 'TournoiEnLigne_sso_user':
                TournoiEnLigne_sso_user.value = cookie.value
                print(f"TournoiEnLigne_sso_user : {cookie.value[-10:]}...")
            elif cookie.name == 'TournoiEnLigne_sso_id':
                TournoiEnLigne_sso_id.value = cookie.value
                print(f"TournoiEnLigne_sso_id : {cookie.value[-10:]}...")
            elif cookie.name == 'TournoiEnLigneidt':
                TournoiEnLigneidt.value = cookie.value
                print(f"TournoiEnLigneidt : {cookie.value[-10:]}...")
            elif cookie.name == 'TournoiEnLignetkt':
                TournoiEnLignetkt.value = cookie.value
                print(f"TournoiEnLignetkt : {cookie.value[-10:]}...")
            elif cookie.name == 'TournoiEnLigneid':
                TournoiEnLigneid.value = cookie.value
                print(f"TournoiEnLigneid : {cookie.value[-10:]}...")
            elif cookie.name == 'TournoiEnLignetk':
                TournoiEnLignetk.value = cookie.value
                print(f"TournoiEnLignetk : {cookie.value[-10:]}...")
        db.commit()
        return True
    except requests.exceptions.RequestException as e:
        # Gérer les erreurs de requête
        print(f"\033[91mErreur lors de la requête : {e}")
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
    try:
        response = requests.post(url, data=formdata, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['statut'] is not 1:
            print(f"\033[91mErreur lors de la requête statut : {data['statut']}")
            return None
        PHPSESSID = db.query(CookieManager).filter_by(name="PHPSESSID").first()
        for cookie in response.cookies:
            if cookie.name == 'PHPSESSID':
                PHPSESSID.value = cookie.value
                print(f"PHPSESSID : {cookie.value[-10:]}...")
        db.commit()
        return data['data']['request_token']
    except requests.exceptions.RequestException as e:
        # Gérer les erreurs de requête
        print(f"\033[91mErreur lors de la requête : {e}")
        return None

def getSearch(query: str, retry: bool = True) -> dict:
    url = "https://boardgamearena.com/omnibar/omnibar/search.html"
    params = {
        "query": query,
    }
    TournoiEnLigne_sso_user = db.query(CookieManager).filter_by(name="TournoiEnLigne_sso_user").first()
    TournoiEnLigne_sso_id = db.query(CookieManager).filter_by(name="TournoiEnLigne_sso_id").first()
    TournoiEnLigneidt = db.query(CookieManager).filter_by(name="TournoiEnLigneidt").first()
    TournoiEnLignetkt = db.query(CookieManager).filter_by(name="TournoiEnLignetkt").first()
    TournoiEnLigneid = db.query(CookieManager).filter_by(name="TournoiEnLigneid").first()
    TournoiEnLignetk = db.query(CookieManager).filter_by(name="TournoiEnLignetk").first()
    headers = {
        "cookie": f"TournoiEnLigne_sso_user={TournoiEnLigne_sso_user};TournoiEnLigne_sso_id={TournoiEnLigne_sso_id};TournoiEnLignetkt={TournoiEnLignetkt};TournoiEnLigneidt={TournoiEnLigneidt}; TournoiEnLignetk={TournoiEnLignetk}; TournoiEnLigneid={TournoiEnLigneid}",
        "x-request-token": TournoiEnLigneidt.value,
        "accept": "*/*",
        "content-type": "multipart/form-data",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('status') != 1:
            print(f"\033[91mErreur lors de la recherche BGA : status={data.get('status')}")
            return {'status': 0, 'error': 'BGA API error', 'players': []}
        
        # Transformer les données pour un format plus utilisable
        result = {
            'status': data['status'],
            'players': [
                {
                    'bga_id': player['id'],
                    'name': player['fullname'],
                    'country': player['country_infos']['code']
                }
                for player in data['data'].get('players', [])
            ]
        }
        print(f"✅ Recherche BGA réussie : {len(result['players'])} joueur(s) trouvé(s)")
        return result
    except requests.exceptions.RequestException as e:
        if retry:
            print(f"\033[93mTentative de récupération du token...\033[0m")
            time.sleep(1)
            postLoginUserWithPassword()
            time.sleep(1)
            return getSearch(query, retry=False)
        else:
            print(f"\033[91mErreur lors de la requête : {e}")
            return None