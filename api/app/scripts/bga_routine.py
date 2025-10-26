import time
from bs4 import BeautifulSoup
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
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
    }
    try:
        response = requests.post(url, data=formdata, headers=headers)

        response.raise_for_status()
        data = response.json()
        
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
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
    }
    try:
        response = requests.post(url, data=formdata, headers=headers)

        response.raise_for_status()
        data = response.json()
        
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

        request_token = data.get('data', {}).get('request_token') if isinstance(data.get('data'), dict) else None

        if not request_token:
            print(f"\033[91m❌ Request token not found in response\033[0m")
            return None

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
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
        }

        response = requests.get(url, headers=headers, params=params)
        
        response.raise_for_status()
        data = response.json()

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

def getGames(bga_id: int, start_date: int = None, end_date: int = None, page: int = 0, retry: bool = True) -> dict:
    try:
        url = "https://boardgamearena.com/gamestats/gamestats/getGames.html"
        params = {
            "player": bga_id,
            "game_id": 1909,  # ID du jeu Altered
            "finished": 1,
            "updateStats": 1,
            "page": page
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        TournoiEnLigne_sso_user = db.session.query(CookieManager).filter_by(name="TournoiEnLigne_sso_user").first()
        TournoiEnLigne_sso_id = db.session.query(CookieManager).filter_by(name="TournoiEnLigne_sso_id").first()
        TournoiEnLigneidt = db.session.query(CookieManager).filter_by(name="TournoiEnLigneidt").first()
        TournoiEnLignetkt = db.session.query(CookieManager).filter_by(name="TournoiEnLignetkt").first()
        TournoiEnLigneid = db.session.query(CookieManager).filter_by(name="TournoiEnLigneid").first()
        TournoiEnLignetk = db.session.query(CookieManager).filter_by(name="TournoiEnLignetk").first()
        
        # Récupérer les cookies avec la fonction helper
        headers = {
            "cookie": f"TournoiEnLigne_sso_user={TournoiEnLigne_sso_user.value};TournoiEnLigne_sso_id={TournoiEnLigne_sso_id.value};TournoiEnLignetkt={TournoiEnLignetkt.value};TournoiEnLigneidt={TournoiEnLigneidt.value};TournoiEnLignetk={TournoiEnLignetk.value};TournoiEnLigneid={TournoiEnLigneid.value}",
            "x-request-token": TournoiEnLigneidt.value,
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
        }

        
        response = requests.get(url, headers=headers, params=params)
        
        response.raise_for_status()
        data = response.json()
        
        # Vérifier le status
        status = data.get('status', 0)
        if status != 1:
            if retry:
                print(f"\033[93m🔄 Reconnexion...\033[0m")
                postLoginUserWithPassword()
                time.sleep(1)
                return getGames(bga_id, page, retry=False)
            return {
                'status': 0,
                'error': 'BGA API error',
                'data': {'tables': [], 'stats': {}}
            }
        
        # ✅ Affichage formaté du JSON
        print("\n" + "="*80)
        print("📊 GET GAMES BGA - DATA RECEIVED")
        print("="*80)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("="*80 + "\n")
        
        # Extraire les données
        games_data = data.get('data', {})
        tables = games_data.get('tables', [])
        stats = games_data.get('stats', {})
        
        # Transformer les tables
        transformed_tables = []
        for table in tables:
            # Parser les données CSV
            player_ids = table.get('players', '').split(',')
            player_names = table.get('player_names', '').split(',')
            scores = table.get('scores', '').split(',')
            ranks = table.get('ranks', '').split(',')
            
            # Trouver l'index du joueur recherché
            player_index = -1
            player_score = 0
            player_rank = 0
            
            try:
                player_index = player_ids.index(str(bga_id))
                player_score = int(scores[player_index]) if player_index < len(scores) else 0
                player_rank = int(ranks[player_index]) if player_index < len(ranks) else 0
            except (ValueError, IndexError):
                pass
            
            # Créer la liste des joueurs
            players_list = []
            for i, pid in enumerate(player_ids):
                if pid:  # Ignorer les IDs vides
                    players_list.append({
                        'id': int(pid),
                        'name': player_names[i] if i < len(player_names) else 'Unknown',
                        'score': int(scores[i]) if i < len(scores) and scores[i] else 0,
                        'rank': int(ranks[i]) if i < len(ranks) and ranks[i] else 0,
                        'is_main_player': pid == str(bga_id)
                    })
            
            # Construire l'objet table transformé
            transformed_table = {
                'table_id': int(table.get('table_id', 0)),
                'game_name': table.get('game_name', 'altered'),
                'game_id': int(table.get('game_id', 1909)),
                'start_timestamp': int(table.get('start', 0)),
                'end_timestamp': int(table.get('end', 0)),
                'duration_seconds': int(table.get('end', 0)) - int(table.get('start', 0)),
                'concede': table.get('concede') == '1',
                'unranked': table.get('unranked') == '1',
                'normalend': table.get('normalend') == '1',
                'ranking_disabled': table.get('ranking_disabled') == '1',
                'players': players_list,
                'player_score': player_score,
                'player_rank': player_rank,
                'is_winner': player_rank == 1,
                'elo_win': float(table.get('elo_win', 0)) if table.get('elo_win') else 0,
                'elo_penalty': float(table.get('elo_penalty', 0)) if table.get('elo_penalty') else 0,
                'elo_after': int(table.get('elo_after', 0)) if table.get('elo_after') else 0,
                'arena_win': float(table.get('arena_win', 0)) if table.get('arena_win') else 0,
                'arena_after': float(table.get('arena_after', 0)) if table.get('arena_after') else 0,
            }
            
            transformed_tables.append(transformed_table)
        
        # Transformer les stats
        transformed_stats = {}
        
        if isinstance(stats, dict):
            # Stats générales
            general = stats.get('general', {})
            transformed_stats['general'] = {
                'total_games': int(general.get('played', 0)),
                'total_victories': int(general.get('victory', 0)),
                'win_rate': float(general.get('score', 0)),  # Taux de victoire (0-1)
                'total_elo_win': float(general.get('elo_win', 0)),
                'avg_elo_per_game': float(general.get('elo_win', 0)) / int(general.get('played', 1)) if int(general.get('played', 0)) > 0 else 0
            }
            
            # Stats par jeu (normalement un seul jeu : Altered)
            games = stats.get('games', [])
            transformed_stats['games'] = []
            if isinstance(games, list):
                for game in games:
                    transformed_stats['games'].append({
                        'game_id': int(game.get('game_id', 1909)),
                        'game_name': game.get('game_name', 'altered'),
                        'total_games': int(game.get('cnt', 0))
                    })

        result = {
            'status': 1,
            'data': {
                'tables': transformed_tables,
                'stats': transformed_stats,
                'pagination': {
                    'current_page': page,
                    'games_in_page': len(transformed_tables),
                    'has_more': len(transformed_tables) > 0  # S'il y a des résultats, il peut y avoir une page suivante
                }
            }
        }
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"\033[91m❌ Erreur HTTP : {e}\033[0m")
        if retry:
            print(f"\033[93m🔄 Reconnexion...\033[0m")
            postLoginUserWithPassword()
            time.sleep(1)
            return getGames(bga_id, page, retry=False)
        return {
            'status': 0,
            'error': f'Request failed: {str(e)}',
            'data': {'tables': [], 'stats': {}}
        }
    except Exception as e:
        print(f"\033[91m❌ Erreur inattendue : {e}\033[0m")
        import traceback
        traceback.print_exc()
        return {
            'status': 0,
            'error': f'Unexpected error: {str(e)}',
            'data': {'tables': [], 'stats': {}}
        }

def getPlayer(bga_id: int, retry: bool = True) -> dict:
    try:
        url = "https://boardgamearena.com/player"
        params = {
            "id": bga_id,
        }

        TournoiEnLigne_sso_user = db.session.query(CookieManager).filter_by(name="TournoiEnLigne_sso_user").first()
        TournoiEnLigne_sso_id = db.session.query(CookieManager).filter_by(name="TournoiEnLigne_sso_id").first()
        TournoiEnLigneidt = db.session.query(CookieManager).filter_by(name="TournoiEnLigneidt").first()
        TournoiEnLignetkt = db.session.query(CookieManager).filter_by(name="TournoiEnLignetkt").first()
        TournoiEnLigneid = db.session.query(CookieManager).filter_by(name="TournoiEnLigneid").first()
        TournoiEnLignetk = db.session.query(CookieManager).filter_by(name="TournoiEnLignetk").first()
        
        # Récupérer les cookies avec la fonction helper
        headers = {
            "cookie": f"TournoiEnLigne_sso_user={TournoiEnLigne_sso_user.value};TournoiEnLigne_sso_id={TournoiEnLigne_sso_id.value};TournoiEnLignetkt={TournoiEnLignetkt.value};TournoiEnLigneidt={TournoiEnLigneidt.value};TournoiEnLignetk={TournoiEnLignetk.value};TournoiEnLigneid={TournoiEnLigneid.value}",
            "x-request-token": TournoiEnLigneidt.value,
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
        }

        
        response = requests.get(url, headers=headers, params=params)
        
        response.raise_for_status()
        # ✅ Parser le HTML avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        player_data = {
            'bga_id': bga_id,
            'name': None,
            'country': None,
            'country_name': None,
            'bio': None
        }

        # 1. ✅ Nom du joueur - SPAN avec id="real_player_name"
        name_elem = soup.find('span', id='real_player_name')
        if name_elem:
            player_data['name'] = name_elem.get_text(strip=True)
            print(f"✅ Nom trouvé: {player_data['name']}")
        else:
            print("⚠️  Span #real_player_name non trouvé")

        # 2. ✅ Avatar du joueur - IMG avec id="real_player_avatar"
        bio_elem = soup.find('div', id='textdescription')
        if bio_elem:
            player_data['bio'] = bio_elem.get_text(strip=True)
            print(f"✅ Bio trouvée: {player_data['bio']}")
        else:
            print("⚠️  Div #textdescription non trouvée")

                # 3. ✅ Pays du joueur - Chercher la div.bga-flag avec data-country
        # Structure: <div class="row-value"><div class="bga-flag" data-country="FR"></div> France</div>
        country_flag = soup.find('div', class_='bga-flag')
        if country_flag:
            # Extraire le code pays depuis l'attribut data-country
            player_data['country'] = country_flag.get('data-country')
            
            # Extraire le nom du pays depuis le texte parent
            row_value = country_flag.find_parent('div', class_='row-value')
            if row_value:
                # Récupérer le texte complet et nettoyer
                full_text = row_value.get_text(strip=True)
                # Retirer les espaces et caractères spéciaux
                country_name = full_text.replace('\xa0', ' ').strip()
                player_data['country_name'] = country_name
                
            print(f"✅ Pays trouvé: {player_data['country']} ({player_data['country_name']})")
        else:
            print("⚠️  Div .bga-flag non trouvée")

        # ✅ Affichage formaté des données extraites
        print("\n" + "="*80)
        print("📊 PLAYER DATA EXTRACTED")
        print("="*80)
        print(json.dumps(player_data, indent=2, ensure_ascii=False))
        print("="*80 + "\n")

        return {
            'status': 1,
            'data': player_data
        }

    except requests.exceptions.RequestException as e:
        print(f"\033[91m❌ Erreur HTTP : {e}\033[0m")
        if retry:
            print(f"\033[93m🔄 Reconnexion...\033[0m")
            postLoginUserWithPassword()
            time.sleep(1)
            return getPlayer(bga_id, retry=False)
        return {
            'status': 0,
            'error': f'Request failed: {str(e)}',
            'data': None
        }
    except Exception as e:
        print(f"\033[91m❌ Erreur inattendue : {e}\033[0m")
        import traceback
        traceback.print_exc()
        return {
            'status': 0,
            'error': f'Unexpected error: {str(e)}',
            'data': None
        }
    
def import_ladder_from_bga(season: int, page: int = 0, retry: bool = True) -> dict:
    """
    Importe le classement BGA Arena pour une saison donnée avec pagination
    
    Args:
        season: Numéro de saison (ex: 202410)
        page: Numéro de page (commence à 0)
        retry: Autoriser une tentative de reconnexion
        
    Returns:
        Dict avec status, data (ranks) et pagination info
    """
    try:
        url = "https://boardgamearena.com/halloffame/halloffame/getRanking.html"
        params = {
            "game": 1909,  # ID du jeu Altered
            "start": page * 10,  # BGA retourne 10 résultats par page
            "mode": "arena",
            "season": season
        }

        TournoiEnLigne_sso_user = db.session.query(CookieManager).filter_by(name="TournoiEnLigne_sso_user").first()
        TournoiEnLigne_sso_id = db.session.query(CookieManager).filter_by(name="TournoiEnLigne_sso_id").first()
        TournoiEnLigneidt = db.session.query(CookieManager).filter_by(name="TournoiEnLigneidt").first()
        TournoiEnLignetkt = db.session.query(CookieManager).filter_by(name="TournoiEnLignetkt").first()
        TournoiEnLigneid = db.session.query(CookieManager).filter_by(name="TournoiEnLigneid").first()
        TournoiEnLignetk = db.session.query(CookieManager).filter_by(name="TournoiEnLignetk").first()
        
        headers = {
            "cookie": f"TournoiEnLigne_sso_user={TournoiEnLigne_sso_user.value};TournoiEnLigne_sso_id={TournoiEnLigne_sso_id.value};TournoiEnLignetkt={TournoiEnLignetkt.value};TournoiEnLigneidt={TournoiEnLigneidt.value};TournoiEnLignetk={TournoiEnLignetk.value};TournoiEnLigneid={TournoiEnLigneid.value}",
            "x-request-token": TournoiEnLigneidt.value,
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        
        # Vérifier le status
        status = data.get('status', 0)
        if status != 1:
            if retry:
                print(f"\033[93m🔄 Reconnexion...\033[0m")
                postLoginUserWithPassword()
                time.sleep(1)
                return import_ladder_from_bga(season, page, retry=False)
            return {
                'status': 0,
                'error': 'BGA API error',
                'data': None,
                'pagination': None
            }
        
        ranks = data.get('data', {}).get('ranks', [])
        
        # ✅ Affichage formaté du JSON
        print("\n" + "="*80)
        print(f"📊 LADDER SEASON {season} - PAGE {page}")
        print("="*80)
        print(f"Ranks trouvés: {len(ranks)}")
        print("="*80 + "\n")
        
        return {
            'status': 1,
            'data': data.get('data', {}),
            'pagination': {
                'current_page': page,
                'results_in_page': len(ranks),
                'has_more': len(ranks) == 10  # Si 10 résultats, il peut y avoir une page suivante
            }
        }
        
    except requests.exceptions.RequestException as e:
        print(f"\033[91m❌ Erreur HTTP : {e}\033[0m")
        if retry:
            print(f"\033[93m🔄 Reconnexion...\033[0m")
            postLoginUserWithPassword()
            time.sleep(1)
            return import_ladder_from_bga(season, page, retry=False)
        return {
            'status': 0,
            'error': f'Request failed: {str(e)}',
            'data': None,
            'pagination': None
        }
    except Exception as e:
        print(f"\033[91m❌ Erreur inattendue : {e}\033[0m")
        import traceback
        traceback.print_exc()
        return {
            'status': 0,
            'error': f'Unexpected error: {str(e)}',
            'data': None,
            'pagination': None
        }