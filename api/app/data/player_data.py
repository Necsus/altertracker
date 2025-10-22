from typing import List
from app.models.player import Player
from app.extensions import db
from sqlalchemy import func, case

def search_players_data(query: str, limit: int = 10) -> List[Player]:
    """
    Recherche des joueurs par nom avec priorité :
    1. Ceux dont le nom commence par la query
    2. Ceux qui contiennent la query dans leur nom
    """
    query_lower = query.lower()
    
    # Créer un ordre de priorité
    priority = case(
        (func.lower(Player.name).like(f'{query_lower}%'), 1),  # Commence par
        else_=2  # Contient
    )
    
    # Recherche avec tri par priorité puis par nom
    players = db.session.query(Player).filter(
        func.lower(Player.name).like(f'%{query_lower}%')
    ).order_by(
        priority,
        Player.name
    ).limit(limit).all()
    
    return players