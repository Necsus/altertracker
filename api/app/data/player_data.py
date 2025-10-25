from typing import List, Optional
import uuid
from datetime import datetime
from app.models.player import Player, Game
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
        func.lower(Player.name).like(f'%{query_lower}%'),
        Player.is_active == True
    ).order_by(
        priority,
        Player.name
    ).limit(limit).all()
    
    return players

def create_player_data(new_player: Player) -> Player:
    existing = get_player_by_bga_id_data(new_player.bga_id)
    if existing:
        existing.is_active = True
        db.session.commit()
        return existing
    db.session.add(new_player)
    db.session.commit()
    return new_player

def get_player_by_id_data(player_id: str) -> Optional[Player]:
    try:
        player_uuid = uuid.UUID(player_id)
        return db.session.query(Player).filter_by(id=player_uuid).first()
    except ValueError:
        raise ValueError(f"Invalid UUID format: {player_id}")
    except Exception as e:
        raise e

def get_player_by_bga_id_data(bga_id: int) -> Optional[Player]:
    """Récupère un joueur par son BGA ID"""
    return db.session.query(Player).filter_by(bga_id=bga_id).first()

def get_game_by_table_id_data(table_id: int) -> Optional[Game]:
    """Vérifie si une partie existe déjà par son table_id"""
    return db.session.query(Game).filter_by(table_id=table_id).first()

def bulk_insert_games_data(games: List[Game]) -> int:
    try:
        if not games:
            return 0
            
        db.session.bulk_save_objects(games)
        db.session.commit()
        return len(games)
        
    except Exception as e:
        db.session.rollback()
        print(f"\033[91m❌ Erreur lors de l'insertion bulk: {e}\033[0m")
        raise e

def update_player_stats_data(player: Player, wins: int = 0, losses: int = 0, draws: int = 0, last_game_at: datetime = None) -> Player:
    try:
        player.total_wins += wins
        player.total_losses += losses
        player.total_draws += draws
        
        if last_game_at:
            if not player.last_game_at or last_game_at > player.last_game_at:
                player.last_game_at = last_game_at
        
        # Recalculer le win_rate
        player.calculate_win_rate()
        
        db.session.commit()
        return player
        
    except Exception as e:
        db.session.rollback()
        print(f"\033[91m❌ Erreur lors de la mise à jour des stats: {e}\033[0m")
        raise e

def batch_update_players_stats_data(players_stats: dict) -> None:
    """
    Met à jour les stats de plusieurs joueurs en batch
    
    Args:
        players_stats: Dict {player_id: {'wins': int, 'losses': int, 'draws': int, 'last_game_at': datetime}}
    """
    try:
        for player_id, stats in players_stats.items():
            player = db.session.query(Player).filter_by(id=player_id).first()
            if player:
                player.total_wins += stats.get('wins', 0)
                player.total_losses += stats.get('losses', 0)
                player.total_draws += stats.get('draws', 0)
                
                last_game_at = stats.get('last_game_at')
                if last_game_at:
                    if not player.last_game_at or last_game_at > player.last_game_at:
                        player.last_game_at = last_game_at
                
                player.calculate_win_rate()
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"\033[91m❌ Erreur lors de la mise à jour batch des stats: {e}\033[0m")
        raise e

