from app.data.player_data import search_players_data
from app.models.player import Player

def search_players_service(query: str) -> list:
    players = search_players_data(query)
    return [player.json() for player in players]