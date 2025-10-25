from typing import List, Optional
import uuid
from app.models.player import Player
from app.extensions import db
from sqlalchemy import func, case

def search_players_data(query: str, limit: int = 10) -> List[Player]:
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

def create_player_data(new_player: Player) -> Player:
    db.session.add(new_player)
    db.session.commit()
    return new_player

def get_player_by_id_data(player_id: str) -> Optional[Player]:
    """
    Récupérer un joueur par son ID (UUID)
    
    Args:
        player_id (str): UUID du joueur au format string
        
    Returns:
        Optional[Player]: Le joueur ou None si non trouvé
        
    Raises:
        ValueError: Si l'UUID est invalide
    """
    try:
        # Convertir le string en UUID
        player_uuid = uuid.UUID(player_id)
        return db.session.query(Player).filter_by(id=player_uuid).first()
    except ValueError:
        raise ValueError(f"Invalid UUID format: {player_id}")
    except Exception as e:
        raise e