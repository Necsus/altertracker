import json
from app.models.player import Player
from app.scripts.bga_routine import getGames, getPlayer, getSearch
from app.data.player_data import create_player_data, get_player_by_id_data, search_players_data

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
    player = getPlayer(bga_id)
    if not player or player.get('status') != 1:
        return {
            'status': 0,
            'error': player.get('error', 'Unknown error') if player else 'No response',
            'player': None
        }

    new_player = Player(
        bga_id = player['data'].get('bga_id', 0),
        name = player['data'].get('name', None),
        country = player['data'].get('country', None),
        bio = player['data'].get('bio', None),
    )

    new_player = create_player_data(new_player)
    print(new_player)

    games = getGames(bga_id, 1)

    if not games or games.get('status') != 1:
        return {
            'status': 0,
            'error': games.get('error', 'Unknown error') if games else 'No response',
            'player': None
        }
    # ✅ Affichage formaté du JSON
    print("\n" + "="*80)
    print("📊 IMPORT PLAYER BGA - DATA RECEIVED")
    print("="*80)
    print(json.dumps(games, indent=2, ensure_ascii=False))
    print("="*80 + "\n")

    return str(new_player.id)

def get_player_by_id_service(player_id: str) -> dict:
    """
    Récupérer un joueur par son ID (UUID)
    
    Args:
        player_id (str): UUID du joueur
        
    Returns:
        dict: Données du joueur au format JSON
    """
    player = get_player_by_id_data(player_id)
    
    if not player:
        return None
    
    return player.json()