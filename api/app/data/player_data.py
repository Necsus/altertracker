from typing import List, Optional
import uuid
from datetime import datetime, timezone
from app.models.player import Player, Game, PlayerSeasonStats
from app.extensions import db
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload
from app.models.season import Season

def _ensure_timezone_aware(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    
    # Si déjà timezone-aware, retourner tel quel
    if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
        return dt
    
    # Sinon, ajouter UTC
    return dt.replace(tzinfo=timezone.utc)

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
    existing = get_player_by_bga_id_data(new_player.bga_id)
    if existing:
        existing.name = new_player.name
        existing.country = new_player.country
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
    return db.session.query(Player).filter_by(bga_id=bga_id).first()

def get_game_by_table_id_data(table_id: int) -> Optional[Game]:
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
            # ✅ Normaliser les datetimes avant comparaison
            last_game_at_aware = _ensure_timezone_aware(last_game_at)
            player_last_game_aware = _ensure_timezone_aware(player.last_game_at)
            
            if player_last_game_aware is None or (last_game_at_aware is not None and last_game_at_aware > player_last_game_aware):
                player.last_game_at = last_game_at_aware
        
        # Recalculer le win_rate
        player.calculate_win_rate()
        
        db.session.commit()
        return player
        
    except Exception as e:
        db.session.rollback()
        print(f"\033[91m❌ Erreur lors de la mise à jour des stats: {e}\033[0m")
        raise e

def batch_update_players_stats_data(players_stats: dict) -> None:
    try:
        for player_id, stats in players_stats.items():
            player = db.session.query(Player).filter_by(id=player_id).first()
            if player:
                player.total_wins += stats.get('wins', 0)
                player.total_losses += stats.get('losses', 0)
                player.total_draws += stats.get('draws', 0)
                
                last_game_at = stats.get('last_game_at')
                if last_game_at:
                    # ✅ Normaliser les deux datetimes avant comparaison
                    last_game_at_aware = _ensure_timezone_aware(last_game_at)
                    player_last_game_aware = _ensure_timezone_aware(player.last_game_at)
                    
                    if player_last_game_aware is None or (last_game_at_aware is not None and last_game_at_aware > player_last_game_aware):
                        player.last_game_at = last_game_at_aware
                
                player.calculate_win_rate()
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"\033[91m❌ Erreur lors de la mise à jour batch des stats: {e}\033[0m")
        raise e

def get_player_history_data(player_id: str, season: int) -> List[Game]:
    player = get_player_by_id_data(player_id)
    if not player:
        raise ValueError(f"Player not found: {player_id}")
    
    query = db.session.query(Game).filter(
        (Game.player1_id == player.id) | (Game.player2_id == player.id)
    )
    
    if season is not None:
        query = query.filter(Game.season == season)

    return query.order_by(Game.played_at.desc()).all()

def get_or_create_season_stats_data(player_id: uuid.UUID, season: str) -> PlayerSeasonStats:
    stats = db.session.query(PlayerSeasonStats).filter_by(
        player_id=player_id,
        season=season
    ).first()
    
    if not stats:
        stats = PlayerSeasonStats(
            player_id=player_id,
            season=season
        )
        db.session.add(stats)
        db.session.commit()
    
    return stats

def update_season_stats_data(season_stats: PlayerSeasonStats, **kwargs) -> PlayerSeasonStats:
    try:
        for key, value in kwargs.items():
            if hasattr(season_stats, key):
                setattr(season_stats, key, value)
        
        # Recalculer le win_rate si nécessaire
        if any(k in kwargs for k in ['wins', 'losses', 'draws']):
            season_stats.calculate_win_rate()
        
        db.session.commit()
        return season_stats
        
    except Exception as e:
        db.session.rollback()
        print(f"\033[91m❌ Erreur lors de la mise à jour des stats de saison: {e}\033[0m")
        raise e

def bulk_upsert_season_stats_data(season_stats_updates: list[dict]) -> int:
    try:
        updated_count = 0
        
        for stats in season_stats_updates:
            print(stats)
            # Chercher les stats existantes
            season_stat = PlayerSeasonStats.query.filter_by(
                player_id=stats['player_id'],
                season=stats['season']
            ).first()
            
            if season_stat:
                # ✅ Mise à jour COMPLÈTE
                season_stat.wins = stats.get('wins', season_stat.wins)
                season_stat.losses = stats.get('losses', season_stat.losses)
                season_stat.draws = stats.get('draws', season_stat.draws)
                season_stat.win_rate = stats.get('win_rate', season_stat.win_rate)
                season_stat.points = stats.get('points', season_stat.points)
                season_stat.rank = stats.get('rank', season_stat.rank)
                season_stat.highest_rank = stats.get('highest_rank', season_stat.highest_rank)
                updated_count += 1
            else:
                # ✅ Création avec valeurs par défaut
                season_stat = PlayerSeasonStats(
                    player_id=stats['player_id'],
                    season=stats['season'],
                    wins=stats.get('wins', 0),
                    losses=stats.get('losses', 0),
                    draws=stats.get('draws', 0),
                    win_rate=stats.get('win_rate', 0.0),
                    points=stats.get('points', 0),
                    rank=stats.get('rank'),
                    highest_rank=stats.get('highest_rank')
                )
                db.session.add(season_stat)
                updated_count += 1
        
        db.session.commit()
        return updated_count
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur bulk_upsert_season_stats_data: {e}")
        raise e

def get_season_stats_data(
    season: int, 
    include_player: bool = True,
    page: int = 1,
    limit: int = 100
) -> tuple[List[PlayerSeasonStats], int]:
    query = db.session.query(PlayerSeasonStats).filter_by(season=str(season))
    
    # ✅ Eager loading du player pour éviter les N+1 queries
    if include_player:
        query = query.options(joinedload(PlayerSeasonStats.player))
    
    # ✅ Trier par rang (ou points si pas de rang)
    query = query.order_by(
        PlayerSeasonStats.rank.nullslast(),
        PlayerSeasonStats.points.desc()
    )
    
    # ✅ Compter le total
    total = query.count()
    
    # ✅ Appliquer la pagination
    stats = query.limit(limit).offset((page - 1) * limit).all()
    
    return stats, total

def get_all_seasons_data() -> List[Season]:
    return db.session.query(Season).order_by(Season.season.desc()).all()

def count_total_players_data() -> int:
    return db.session.query(func.count(Player.id)).scalar()

def get_current_season_data() -> Optional[Season]:
    return db.session.query(Season).filter_by(current=True).first()

def get_season_stats_by_player_data(player_id: str, season: int) -> Optional[PlayerSeasonStats]:
    return db.session.query(PlayerSeasonStats).filter_by(
        player_id=player_id,
        season=str(season)
    ).first()

def update_player_data(player: Player) -> Player:
    try:
        db.session.commit()
        return player
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur update_player_data: {e}")
        raise e