from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
from app.models.cookie_manager import CookieManager
from app.extensions import db

def init_selenium_driver(headless: bool = True) -> webdriver.Chrome:
    """Initialise un driver Selenium avec les cookies de session"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless=new")
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # ✅ Activer la capture des requêtes réseau
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
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

def intercept_logs_response(driver: webdriver.Chrome, table_id: int) -> dict:
    """
    Intercepte la réponse de l'appel logs.html qui est automatiquement fait par gamereview
    """
    try:
        print(f"🔍 Interception des requêtes réseau pour la table {table_id}...")
        
        # Récupérer tous les logs de performance
        logs = driver.get_log('performance')
        
        for log in logs:
            try:
                log_message = json.loads(log['message'])
                message = log_message.get('message', {})
                method = message.get('method', '')
                
                # Chercher les réponses réseau (Network.responseReceived)
                if method == 'Network.responseReceived':
                    params = message.get('params', {})
                    response = params.get('response', {})
                    url = response.get('url', '')
                    
                    # Vérifier si c'est l'appel logs.html pour notre table
                    if 'logs.html' in url and f'table={table_id}' in url:
                        request_id = params.get('requestId')
                        print(f"✅ Requête logs.html interceptée : {url}")
                        
                        # Récupérer le corps de la réponse via Chrome DevTools Protocol
                        try:
                            response_body = driver.execute_cdp_cmd(
                                'Network.getResponseBody',
                                {'requestId': request_id}
                            )
                            
                            body = response_body.get('body', '')
                            
                            # Parser le JSON
                            if body:
                                logs_data = json.loads(body)
                                print(f"✅ Données logs.html récupérées : {len(str(logs_data))} caractères")
                                return {
                                    'status': 1,
                                    'error': '',
                                    'data': logs_data
                                }
                        except Exception as e:
                            print(f"⚠️  Erreur lors de la récupération du corps de la réponse : {e}")
                            continue
                            
            except json.JSONDecodeError:
                continue
            except Exception as e:
                continue
        
        return {
            'status': 0,
            'error': 'logs.html request not found in network logs',
            'data': None
        }
        
    except Exception as e:
        print(f"\033[91m❌ Erreur lors de l'interception des logs réseau : {e}\033[0m")
        import traceback
        traceback.print_exc()
        return {
            'status': 0,
            'error': f'Network interception error: {str(e)}',
            'data': None
        }

def getGamerView(table_id: int, retry: bool = True, driver: webdriver.Chrome = None) -> dict:
    """
    Récupère les informations d'une partie en interceptant l'appel logs.html fait automatiquement par gamereview
    """
    should_quit_driver = False
    
    try:
        # Créer un driver si non fourni
        if driver is None:
            driver = init_selenium_driver(headless=True)
            should_quit_driver = True
        
        # Naviguer vers la page de review de la partie
        gamereview_url = f"https://boardgamearena.com/gamereview?table={table_id}"
        print(f"🌐 Navigation vers gamereview : {gamereview_url}")
        driver.get(gamereview_url)
        
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
            pass
        
        # Attendre que le contenu principal soit chargé
        try:
            wait.until(EC.presence_of_element_located((By.ID, "game_name")))
            print("✅ Page gamereview chargée")
        except TimeoutException:
            print(f"\033[91m❌ Timeout : Le contenu de la partie ne s'est pas chargé\033[0m")
            return {
                'status': 0,
                'error': 'Page load timeout',
                'data': None
            }
        
        # Attendre un peu pour que tous les appels réseau soient terminés
        time.sleep(2)
        
        # ✅ Intercepter la réponse de logs.html qui a été automatiquement appelée
        result = intercept_logs_response(driver, table_id)
        
        return result
        
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
            time.sleep(1)
        
        return results
        
    finally:
        if driver:
            driver.quit()
            print("🔒 Driver Selenium fermé")