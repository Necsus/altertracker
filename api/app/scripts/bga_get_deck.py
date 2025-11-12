from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from app.models.cookie_manager import CookieManager
from app.extensions import db

def init_selenium_driver(headless: bool = True) -> webdriver.Chrome:
    """Initialise un driver Selenium avec les cookies de session"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless=new")  # Mode headless moderne
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Laisser Selenium 4.x gérer automatiquement le driver
    driver = webdriver.Chrome(options=chrome_options)
    
    # Charger une page BGA pour pouvoir ajouter les cookies
    driver.get("https://boardgamearena.com")
    time.sleep(1)
    
    # Récupérer et ajouter les cookies depuis la base de données
    try:
        cookies_to_add = [
            'TournoiEnLigne_sso_user',
            'TournoiEnLigne_sso_id',
            'TournoiEnLigneidt',
            'TournoiEnLignetkt',
            'TournoiEnLigneid',
            'TournoiEnLignetk'
        ]
        
        for cookie_name in cookies_to_add:
            cookie_obj = db.session.query(CookieManager).filter_by(name=cookie_name).first()
            if cookie_obj:
                driver.add_cookie({
                    'name': cookie_name,
                    'value': cookie_obj.value,
                    'domain': '.boardgamearena.com'
                })
                print(f"✅ Cookie {cookie_name} ajouté")
            else:
                print(f"⚠️  Cookie {cookie_name} non trouvé dans la DB")
        
        # Rafraîchir pour appliquer les cookies
        driver.refresh()
        time.sleep(1)
        
    except Exception as e:
        print(f"\033[91m❌ Erreur lors de l'ajout des cookies : {e}\033[0m")
        driver.quit()
        raise
    
    return driver

def getGamerView(table_id: int, retry: bool = True, driver: webdriver.Chrome = None) -> dict:
    """
    Récupère les informations d'une partie via Selenium
    """
    should_quit_driver = False
    
    try:
        # Créer un driver si non fourni
        if driver is None:
            driver = init_selenium_driver(headless=True)
            should_quit_driver = True
        
        # Naviguer vers la page de review de la partie
        url = f"https://boardgamearena.com/gamereview?table={table_id}"
        print(f"🌐 Navigation vers : {url}")
        driver.get(url)
        
        # Attendre que la page soit chargée
        wait = WebDriverWait(driver, 10)
        
        # Vérifier si la partie existe (pas de message d'erreur)
        try:
            error_element = driver.find_element(By.CSS_SELECTOR, ".error_msg, .page_error")
            error_text = error_element.text
            print(f"\033[91m❌ Erreur BGA : {error_text}\033[0m")
            return {
                'status': 0,
                'error': f'Game not found or error: {error_text}',
                'data': None
            }
        except NoSuchElementException:
            # Pas d'erreur trouvée, c'est bon !
            pass
        
        # Attendre que le contenu principal soit chargé
        try:
            wait.until(EC.presence_of_element_located((By.ID, "game_name")))
        except TimeoutException:
            print(f"\033[91m❌ Timeout : Le contenu de la partie ne s'est pas chargé\033[0m")
            return {
                'status': 0,
                'error': 'Page load timeout',
                'data': None
            }
        
        # Extraire les données de la partie
        game_data = {}
        
        # 1. Nom du jeu
        try:
            game_name = driver.find_element(By.ID, "game_name").text
            game_data['game_name'] = game_name
            print(f"✅ Jeu : {game_name}")
        except NoSuchElementException:
            game_data['game_name'] = None
        
        # 2. Date de la partie
        try:
            date_element = driver.find_element(By.CSS_SELECTOR, ".smalltext.gamestatedate")
            game_data['game_date'] = date_element.text
            print(f"✅ Date : {game_data['game_date']}")
        except NoSuchElementException:
            game_data['game_date'] = None
        
        # 3. Informations des joueurs
        try:
            players = []
            player_panels = driver.find_elements(By.CSS_SELECTOR, ".player-panel, .player_board_inner")
            
            for panel in player_panels:
                player_info = {}
                
                # Nom du joueur
                try:
                    name_elem = panel.find_element(By.CSS_SELECTOR, ".playername, .player_name")
                    player_info['name'] = name_elem.text
                except NoSuchElementException:
                    player_info['name'] = None
                
                # Score
                try:
                    score_elem = panel.find_element(By.CSS_SELECTOR, ".player_score_value, .score")
                    player_info['score'] = score_elem.text
                except NoSuchElementException:
                    player_info['score'] = None
                
                # Rang
                try:
                    rank_elem = panel.find_element(By.CSS_SELECTOR, ".rank, .player_rank")
                    player_info['rank'] = rank_elem.text
                except NoSuchElementException:
                    player_info['rank'] = None
                
                if player_info['name']:
                    players.append(player_info)
            
            game_data['players'] = players
            print(f"✅ {len(players)} joueurs trouvés")
            
        except Exception as e:
            print(f"⚠️  Erreur lors de l'extraction des joueurs : {e}")
            game_data['players'] = []
        
        # 4. Résultat de la partie
        try:
            result_elem = driver.find_element(By.CSS_SELECTOR, ".gameresult, .game_result")
            game_data['result'] = result_elem.text
            print(f"✅ Résultat : {game_data['result']}")
        except NoSuchElementException:
            game_data['result'] = None
        
        # 5. Durée de la partie
        try:
            duration_elem = driver.find_element(By.CSS_SELECTOR, ".gameduration, .game_duration")
            game_data['duration'] = duration_elem.text
            print(f"✅ Durée : {game_data['duration']}")
        except NoSuchElementException:
            game_data['duration'] = None
        
        # 6. Screenshot de la partie (optionnel)
        try:
            # Prendre un screenshot de la zone de jeu
            game_area = driver.find_element(By.ID, "game_play_area")
            screenshot = game_area.screenshot_as_base64
            game_data['screenshot'] = screenshot
            print(f"✅ Screenshot capturé")
        except Exception as e:
            print(f"⚠️  Impossible de capturer le screenshot : {e}")
            game_data['screenshot'] = None
        
        # 7. Logs de la partie (cliquer sur l'onglet logs si présent)
        try:
            logs_tab = driver.find_element(By.CSS_SELECTOR, "a[href='#logs'], .logs_tab")
            logs_tab.click()
            time.sleep(1)
            
            logs_container = driver.find_element(By.ID, "logs")
            logs_entries = logs_container.find_elements(By.CSS_SELECTOR, ".log, .logentry")
            
            logs = [entry.text for entry in logs_entries if entry.text]
            game_data['logs'] = logs
            print(f"✅ {len(logs)} logs extraits")
            
        except Exception as e:
            print(f"⚠️  Logs non disponibles : {e}")
            game_data['logs'] = []
        
        return {
            'status': 1,
            'error': '',
            'data': game_data
        }
        
    except TimeoutException as e:
        print(f"\033[91m❌ Timeout Selenium : {e}\033[0m")
        if retry:
            print(f"\033[93m🔄 Nouvelle tentative...\033[0m")
            time.sleep(2)
            if should_quit_driver and driver:
                driver.quit()
            return getGamerView(table_id, retry=False)
        return {
            'status': 0,
            'error': f'Selenium timeout: {str(e)}',
            'data': None
        }
        
    except Exception as e:
        print(f"\033[91m❌ Erreur Selenium : {e}\033[0m")
        import traceback
        traceback.print_exc()
        return {
            'status': 0,
            'error': f'Selenium error: {str(e)}',
            'data': None
        }
        
    finally:
        # Fermer le driver seulement si on l'a créé dans cette fonction
        if should_quit_driver and driver:
            driver.quit()
            print("🔒 Driver Selenium fermé")

# ✅ Fonction utilitaire pour réutiliser le même driver pour plusieurs appels
def get_multiple_games_with_selenium(table_ids: list[int]) -> list[dict]:
    """
    Récupère plusieurs parties avec un seul driver Selenium (plus efficace)
    """
    driver = None
    results = []
    
    try:
        driver = init_selenium_driver(headless=True)
        
        for table_id in table_ids:
            print(f"\n📊 Récupération de la partie {table_id}...")
            result = getGamerView(table_id, retry=True, driver=driver)
            results.append(result)
            time.sleep(1)  # Petit délai entre chaque partie
        
        return results
        
    finally:
        if driver:
            driver.quit()
            print("🔒 Driver Selenium fermé")