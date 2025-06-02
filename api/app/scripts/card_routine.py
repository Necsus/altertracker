import requests
from urllib.parse import urlencode
from app.extensions import db
from app.models.cookie_manager import CookieManager

_token = ''
_token0 = 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..I6M1yBDEem-A7zyM.-rozvEBbcVw0ybAbXOPPj1N-qlFVAylta9lyiesyarBvwppqY7EEkIcKJf1FAhydp3RvmGtOkPucaD_M3oMwYk6mgliaDUsTdcwIS373C_YHCvZWnMwpAEj-aZjiYZtDshtsPj0_Tyhj6ukS1WaQjFFyS9qSpi9Va5Mc31fXcGL6Nz2rQ5YvL7k2J0xlrvn3L-RX5Bt-oYvEG_sBGxpBCry_3ZWmGXsND9ZOrxS-02dcxLUqVWf0qwRq1yAHGZXoPT3PTE6bezDhhlqLOv3HFYUPBt_tr6CbzmeqKMigAAeCxaw0R5A4Tex03wopqMDnwHQuiFZzhb-KtrWUOGDyRt8rC7ti5OpnCVkUUDHLpIV5xXvrw-jYXF8gO9-PBNi6oHFbPW3uN3dkHQolYdPq8LA1IVez8zIEaKmz20tHrEX2HgVt-4xjZasZzqQYFSa9zNgAoY8bLxFf8tdYSG3Ka8lga1LvfLc88v2V97FJfYsL_MxrvSflvM_JL9qV_jubsByWpnMrIlrWTQdNpNUh_O1iZi5aaAw33BxpHUZ-ZrtP8q5yxn6ctJbVnA5rzXmJrIa8cU8kGPM_70Iuly408pmiS5waMFdinLAN3KfylRzyCdluRkejlKcvTHqYujk7DTm3ReMmJQoVcfIp6WNaAE83IbO4-MMA5hvjbUh2pq0LVwiMCLUxCWzWQgfex4Qd7uudMtX21pHwLp_S7a2UdFiHBPBwETp2SLNNbe5n0jVLiw1C6DPJmADvAEjyH3-CdLas5wmlrAiiVSJoX6CJ7Rex0yi_bb7j2bcZpoLky4lgs-KH_4c9kbkkfIek2TLKU7NJs6LDZ6PE7lTutkmawbpHXD7mkvFwdoAlHJydT6LolaDL89XcIoO8kSZhe0mluB1D6PrrsJMbc32tq7zn7Pwy3dbFixlFD1KtDtGtOmV3574AvAYmuAMpOgsgYThEHQi6WPVBW4E-5pIg8clEXJQ1lEC2tkd92_D0JDckpWb_rEfJ7I8Ix2SXjcfMOZDFiNlcEXfH39Cwjk3EzuCzsFNiNTz-qgbU2HwY_OSb9PDB_mayjPnGuhVBsaSdVVuJwEp2uaEl8Im6QinYWhK55Ahs-wW6498l-P1MSxwhv8e_g6eKoyJ_Ilv29osSf0v5jzghTGvi5SFHPEawJy6o5dM_EbzVEDILAUcLcEzd9FD5zcXZuSpap6sXlohTmcpZfaghDG6ly-9V1fmbczuxCao1I6NHeD63BFdkk8UYRU1BABuIXKEVZihq1jFAIBhCs2Jm58U_hP4fHAOyjmh9LF32Cv5KfRLVFmjcnpftC2x2oTE6WI-kSsH-awQMq0rswHYpGz1WLj6zfJEgMkeMuGVSGuqcDA9iDDPZb_0ZL8FjTCPwWJ8_GKhavFsqwl2_N-bwXdj4tfCsl6wvkZpAHK1AC7BVcVlXMpQip7a_a55GVrgy8e8uTVOOXw-R_nWGwR9JObsB4xSm4pQRHqm7LGxece_YU5cz5QfDQsonaUencNqWsB9W_0GS0o6H9kI4atY1lRlEPNU46U4k_tynCercbhveCua_ZNVhk1KWycZXTwpt_Z-FadlkiGk7B4PolEvfHKkMpb0kyG3dby2DPyDOnlRsvgQ5Rm6cdiqtuFh1dRncP7pbSszj7aS1BxFpXIOM1xeuIZP4k9A9pcCBoIXjRVdqtWfvCuPJVOs6q6tA3aNd-_4E9nkLcCFR-5DqPkBHeSqFFVs-S9YFEEz-L8PvQg9CqU4AWbtog-fb_RjuyZ2gQSYM_CvE-P1y-zej5uFhN_K6QvroC1TkbnAlmxDq-Q3ZP8buev1IEGZLXSeU4kQTXiP1t-4p5mWql5uixy52A208Xl-KS0brj52rapaRb92doWVzX4hS-QNF4HhEl_PI0mPqdr-XOGOrAZizbVw23jPD4lxBtROleCKzt2jLhV4OTfh85cRaO3h4Bj2wD2U3CIGzeo6sw38nVzcPAEhYSRhGswj_hEeH38WRZulkC6W3okrbJgC44R4lcEgoLbdC44_dlO5ScVAOoIK0RPTAAr7koQD6f6T3GxpnwFwmXFdVqqkx7hi1afcI1fJxS77Ry7mCiYt5Jv2ofgvfFzDaJ1Yi6sLjypgCF_jpY8Fjr-RxUuURp40eljlxaHxzqv55c1Hrg4z01s_TyJL8SXlb0WcljWXKJMWpPkEuEz50n7fK6WFCEl0rAHkNQxRMN676OmB-PHm3dVP_9pfuwN894GmU1_wdsG1rgx_D9jFyRus86xyE8VhYASGaIZxoRJzaDZNRXuAqaCD5plFPRqRwrm9G9SgQ19pHbfRACq19xYvpY1eLceFok7lJAZW4JGTvVSjO43cjA1nWAwBiYnhJLwX8XBMZpy0yA0h3HPuBwRsvjdQPZUKsPoZCkhdgQC8iTudd3mF2XRxXV9nf30I478XzRtXHaHVnNMGLRL0chsQgQ66sTad8x-kZpJUX9J5dRHbhYRkDd-pGTSqL8_dFoixf5ayvCWt4YUK-oHNcVevKNU6b6pqN_6Cr8i40fMWiYnDGwOU2FuchwqI7P7zXSYBwD4XwXQ4fszFz7GR8XtyNYS461fl5rq9NifvfFzIxrce_tYyyQuhSL2K3MMK0LQr_TSbJJh69fbAiMWoqVxFNprnGzDKlWUrXQTg26I9uN9ZckMXCumNbK4ieVvAjJdJhcLvpoKmPu5AYaTaS9LpTjowZPKMUozNjHg7dw280XsFGKyR4UqnE21W8taLdzm-0hoA1hMWvhQiu-r4P_4NgKaT4jh7I1vgjgeMgI57RwwDT1MNU1BKikDh62FWml5xSGWRgL4h1y609ZmXt1-nqE4T7vBKrHiMpuUhMx1BLYZNjOzH9DbU8z02IFip60sziAnuVAsa0Q3L-XxCIgCwj45m_0H5Kgj6g0ujbfPdxObdAind6prEdUgV-uknkXO9ecVvm7vrrT79t7CTuI-qJJ8LrS6-c274_CTzYCBW4gJL5SUMpB413Te4xcgyPjaVT67ok3uQzbAI0SsODhM4QYNpnSKvZTnErjGXjyLmoRtxcPVNxgpKLpfiF5r-Oz8qn5UXfuhZ8mgh3hhoE0T-zWNqCFB51VvU9Wt3q6gzuKYnkj274TMcpaqWqpNl0qrjMde7EZOKchdRFCqxIUTdGeABOEu9fuaOr8ZOs70r1agqpl74L-5oW4bzJOIs8nzjRRR3klfMUf_twAaNLm3ISFWSkWv6f8DloPujHua2fPWtJUY0ZhS3eP0Z82bOGSeI25YZAVvmG2dnk4E_dM0_RwrelbMzy-Tb1ctM4TRIIN1TOL0sKzlqJNm7PAo0D7uZuNKVEujjRRkokZ2aPlAWfuKiXevVH4I0sofKBHXVOlR1YPD76b8CRg5LrlpOZITd2JyesP5oNRPmvjq7AYk9ig_VlUhIdrZ9sxg2tulzUA9vHIUg6gn1ywiZQbgwnpnOKo8VTUXn0nIRH5TGMHPSzq4BPGEVqolE7kcQW78ir5hcH9ETiteOEXwZXmp2iowo8wFnFoa8jQ12Sll268Cdx2KG_WwDM3nkTnVV8c5A8Yz8Na-lDfrTSkOPh75aO0ZMYy2_4cG0h0QuzUro3AmNI6kO4QyC_K0zW3zmIWHAPy45QMypoP6KTHMBJSIqs-zrvbfu7EdhR7sfi-X57yVYmmYKh0Lmrkp4A34KJZGLUTlUQrlDsV1JJYiJawddEYje7F5BB1lLXboXJC-QVzJ4YNU6ZLfJ9MyZYwsFSxwP4f3hnBvXoBbXJTfAoJb1k2G2--T-1uP3RpvcnX4L12ENLf-PPGIN2bjXbFZtYC9Rf7Si1lzG7tadsM1BYhFtBoFGCvOPDhOczXkuytDWFp53il--7be_'
_token1 = 'g_EAa2cIkFgrFGaDOEzJiQu7T4-Ah3QH-H5jJf5EWKIJWitvZoe7mYMrA0d0b685F8XAzSzX-oLVmvJO7d2I5DiGVHnaMHiSz6tJTu65Ya-BnpUD1tN0niCSHq4AuVvOsGhzYsMmcxoIEL5Y3HMIzP6JwHcQejLjmvxT8ACwI37txgRQIIXt6094HJAtxQIgkjI1H463LMnaVjrGYUhtyGbzFXqnHFze621MWHk4XKjQdBnGOIUzppyULZoDKckfsJj74UmwE5-w9fL-sNpnba6A_EXAVhuxEeydTHn9tWjESK1hH0GTzkwUPD32cVCFKP5a9USpDOy-EM-EvlSGdY5X0WmPeHVCKjp6nCqVS_kosH0MBWpa6Jo2PRByaL_sE-ZTTqpmAe2M_vYpJ4N2KtmSG4rBEmpfQiZn-MtcgPydB750yJmYykfMcANxV6yjnR16PgHGo8yXYm2ImiBlUN7usIbO7ZtQhSzdKZmPboMjBZ1Cb-R_0sCpiS1V3g7MrCyx82hyALjeskzWYz1Mh-3tu4BB36lnQlbeZ-7NQQp0Ak9EA_Nmo8kAuB5CfKIXWfOQ_QsqHQsZuKqKVixl--nC6jxGf0HjRHJaYfmfbBEib.oV8StqkX-hmA55WTfH-4oQ'

def get_cards(page: int, set: str, rarity: str):
    base_url = "https://api.altered.gg/cards"
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
        print(f"\033[91mErreur lors de la requête : {e}")
        return None
    
def get_unique_cards_name_faction(name: str, faction: str, set: str, mainCost: int, recallCost: int, forestPower: list[str], page: int):
    base_url = "https://api.altered.gg/cards"
    params = {
        "page": page,
        "cardSet[]": set,
        "cardType[]": "CHARACTER",
        "factions[]": faction,
        "forestPower[]": forestPower,
        "mainCost[]": mainCost,
        "recallCost[]": recallCost,
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
        # print(f"\033[91mErreur lors de la requête : {e}\033[0m")
        return None

def get_card_by_reference(card_reference: str, en: bool = False):
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
        print(f"\033[91mErreur lors de la requête : {e}\033[0m")
        return None

def get_offer_by_reference(reference: str, token: str):
    base_url = f"https://api.altered.gg/cards/{reference}/offers?itemsPerPage=10&page=1"
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

        if 'code' in data and data['code'] == 401:
            if 'message' in data and data['message']:
                print(f"\033[91m{data['message']}\033[0m")
            else:
                print("\033[91mError lors de la requete card_routine.get_offer_by_reference\033[0m")
            return None
        
        if data['hydra:totalItems'] <= 0 or len(data['hydra:member']) <= 0:
            return None
        
        # Retourner les données
        return data['hydra:member']
    except requests.exceptions.RequestException as e:
        # Gérer les erreurs de requête
        print(f"\033[91mErreur lors de la requête : {e}\033[0m")
        return None
    
def getToken() -> str:
    global _token
    global _token0
    global _token1
    if _token:
        return _token
    try:
        
        headers = {
            "Cookie": f"__Secure-next-auth.callback-url=https%3A%2F%2Fwww.altered.gg;__Secure-next-auth.session-token.0={_token0};__Secure-next-auth.session-token.1={_token1}",
            "accept": "*/*"
        }
        response = requests.get("https://www.altered.gg/api/auth/session", headers=headers)
        response.raise_for_status()

        for cookie in response.cookies:
            if cookie.name == '__Secure-next-auth.session-token.0':
                print(f"token.0 : {cookie.value}")
                _token0 = cookie.value
            elif cookie.name == '__Secure-next-auth.session-token.1':
                print(f"token.1 : {cookie.value}")
                _token1 = cookie.value
        data = response.json()
        _token = data['accessToken']
        print(f"Token récupéré : {_token}")
        return _token
    except requests.exceptions.RequestException as e:
        print(f"\033[91mErreur lors de la récupération du token : {e}\033[0m")
        return None

def get_unique_offers(name: str, faction: str, set: str, page: int):
    base_url = "https://api.altered.gg/cards/stats"
    params = {
        "page": page,
        "factions[]": faction,
        "inSale": "true",
        "rarity[]": "UNIQUE",
        "cardSet[]": set,
        "translations.name": name,
        "itemsPerPage": 36,
        "locale": "en-us"
    }
    token = getToken()
    headers = {
        "authorization": f"Bearer {token}",
        "accept": "*/*"
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
        print(f"\033[91mErreur lors de la requête : {e}\033[0m")
        return None