from app.models.player import Player
from app.scripts.bga_routine import getGames, getSearch
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

def import_player_bga_service(bga_id: int) -> str:
    data = getGames(bga_id, 1)

    if not data or data.get('status') != 1:
        return {
            'status': 0,
            'error': data.get('error', 'Unknown error') if data else 'No response',
            'player': None
        }
    print(data)
    new_player = Player(
        name=name,
        bga_id=bga_id,
        )
    return 'dbplayerid'