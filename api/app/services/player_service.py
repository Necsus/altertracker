from app.scripts.bga_routine import getSearch
from app.data.player_data import search_players_data

def search_players_service(query: str) -> list:
    players = search_players_data(query)
    return [player.json() for player in players]

def search_players_bga_service(query: str) -> list:
    data = getSearch(query)
    
    if not data or data.get('status') != 1:
        return {
            'status': 0,
            'error': data.get('error', 'Unknown error') if data else 'No response',
            'players': []
        }
    return data