from datetime import datetime, timezone
import json
import time
import uuid
from typing import List, Dict, Optional
from app.models.player import Player, Game
from app.scripts.bga_routine import getGames, getPlayer, getSearch, import_ladder_from_bga
from app.data.player_data import (
    bulk_upsert_season_stats_data,
    count_total_players_data,
    create_player_data,
    get_current_season_data,
    get_player_by_id_data,
    get_player_history_data,
    get_season_stats_data,
    search_players_data,
    get_player_by_bga_id_data,
    get_game_by_table_id_data,
    bulk_insert_games_data,
    batch_update_players_stats_data,
    get_all_seasons_data
)

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

def get_player_by_id_service(player_id: str) -> dict:
    player = get_player_by_id_data(player_id)
    if not player:
        return None
    
    if not player.is_active:
        import_player_bga_service(player.bga_id)
        player = get_player_by_id_data(player_id)

    return player.json()

def _ensure_timezone_aware(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    
    # Si déjà timezone-aware, retourner tel quel
    if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
        return dt
    
    # Sinon, ajouter UTC
    return dt.replace(tzinfo=timezone.utc)

def _get_or_create_player_from_bga_data(player_data: dict) -> Player:
    bga_id = player_data.get('id')
    
    # Chercher le joueur existant
    existing_player = get_player_by_bga_id_data(bga_id)
    if existing_player:
        return existing_player
    
    # Créer un nouveau joueur minimal
    new_player = Player(
        bga_id=bga_id,
        name=player_data.get('name'),
        total_points=0,
        total_wins=0,
        total_losses=0,
        total_draws=0,
        win_rate=0.0,
        is_active=False
    )
    
    return create_player_data(new_player)

def _transform_bga_game_to_model(game_data: dict, main_player: Player, opponent: Player, season: int) -> Game:
    players = game_data.get('players', [])
    
    # Identifier les données des joueurs
    main_player_data = None
    opponent_data = None
    
    for player in players:
        if player.get('is_main_player'):
            main_player_data = player
        else:
            opponent_data = player
    
    if not main_player_data or not opponent_data:
        raise ValueError("Impossible d'identifier les joueurs de la partie")
    
    # Déterminer le gagnant
    winner_id = None
    is_draw = False
    
    if main_player_data['rank'] == 1:
        winner_id = main_player.id
    elif opponent_data['rank'] == 1:
        winner_id = opponent.id
    elif main_player_data['rank'] == opponent_data['rank']:
        is_draw = True
    
    # Créer l'objet Game
    return Game(
        table_id=game_data['table_id'],
        ranked=not game_data.get('unranked', False),
        player1_id=main_player.id,
        player2_id=opponent.id,
        winner_id=winner_id,
        is_draw=is_draw,
        season=season,
        start=datetime.fromtimestamp(game_data['start_timestamp'], tz=timezone.utc),
        end=datetime.fromtimestamp(game_data['end_timestamp'], tz=timezone.utc),
        duration_minutes=game_data['duration_seconds'] // 60,
        played_at=datetime.fromtimestamp(game_data['end_timestamp'], tz=timezone.utc)
    )

def _calculate_player_stats_from_games(games: List[Game], player_id: uuid.UUID) -> Dict:
    """
    Calcule les statistiques d'un joueur à partir d'une liste de parties
    """
    stats = {
        'wins': 0,
        'losses': 0,
        'draws': 0,
        'last_game_at': None
    }
    
    for game in games:
        if game.winner_id == player_id:
            stats['wins'] += 1
        elif game.is_draw:
            stats['draws'] += 1
        else:
            stats['losses'] += 1
        
        # ✅ S'assurer que les deux datetimes sont timezone-aware
        game_played_at = _ensure_timezone_aware(game.played_at)
        last_game_at = _ensure_timezone_aware(stats['last_game_at'])
        
        if last_game_at is None or (game_played_at is not None and game_played_at > last_game_at):
            stats['last_game_at'] = game_played_at
    
    return stats

def import_games_bulk_service(main_player_id: str, games_data_from_bga: list, season: int) -> dict:
    try:
        # 1. Validation du joueur principal
        main_player_uuid = uuid.UUID(main_player_id)
        main_player = get_player_by_id_data(main_player_id)
        
        if not main_player:
            raise ValueError(f"Player not found: {main_player_id}")
        
        # 2. Initialisation des statistiques
        stats = {
            'created': 0,
            'existing': 0,
            'errors': 0,
            'skipped_ranked': 0,
            'total_processed': 0
        }
        
        # 3. Préparation des données
        games_to_insert: List[Game] = []
        players_stats = {}  # {player_id: {'wins': int, 'losses': int, 'draws': int, 'last_game_at': datetime}}
        
        # Initialiser les stats du joueur principal
        players_stats[main_player.id] = {
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'last_game_at': None
        }
        
        # 4. Traitement de chaque partie (logique métier)
        for game_data in games_data_from_bga:
            stats['total_processed'] += 1
            
            try:
                # Vérifier l'existence
                if get_game_by_table_id_data(game_data['table_id']):
                    stats['existing'] += 1
                    continue
                
                # Filtrer les parties non-ranked
                if game_data.get('unranked') or game_data.get('ranking_disabled'):
                    stats['skipped_ranked'] += 1
                    continue
                
                # Identifier les joueurs
                players = game_data.get('players', [])
                if len(players) < 2:
                    stats['errors'] += 1
                    continue
                
                # Récupérer ou créer l'adversaire
                opponent_data = next((p for p in players if not p.get('is_main_player')), None)
                if not opponent_data:
                    stats['errors'] += 1
                    continue
                
                opponent = _get_or_create_player_from_bga_data(opponent_data)
                
                # Initialiser les stats de l'adversaire si nécessaire
                if opponent.id not in players_stats:
                    players_stats[opponent.id] = {
                        'wins': 0,
                        'losses': 0,
                        'draws': 0,
                        'last_game_at': None
                    }
                
                # Transformer en modèle Game
                game = _transform_bga_game_to_model(game_data, main_player, opponent, season)
                games_to_insert.append(game)
                
                # Calculer les stats pour chaque joueur
                if game.winner_id == main_player.id:
                    players_stats[main_player.id]['wins'] += 1
                    players_stats[opponent.id]['losses'] += 1
                elif game.winner_id == opponent.id:
                    players_stats[main_player.id]['losses'] += 1
                    players_stats[opponent.id]['wins'] += 1
                elif game.is_draw:
                    players_stats[main_player.id]['draws'] += 1
                    players_stats[opponent.id]['draws'] += 1
                
                # ✅ Mettre à jour last_game_at avec timezone-aware datetime
                game_played_at = _ensure_timezone_aware(game.played_at)
                
                for player_id in [main_player.id, opponent.id]:
                    last_game_at = _ensure_timezone_aware(players_stats[player_id]['last_game_at'])
                    
                    if last_game_at is None or (game_played_at is not None and game_played_at > last_game_at):
                        players_stats[player_id]['last_game_at'] = game_played_at
                
                stats['created'] += 1
                
            except Exception as e:
                print(f"\033[91m❌ Erreur sur la partie {game_data.get('table_id')}: {e}\033[0m")
                import traceback
                traceback.print_exc()
                stats['errors'] += 1
                continue
        
        # 5. Insertion bulk des parties (délégué à la couche data)
        if games_to_insert:
            bulk_insert_games_data(games_to_insert)
        
        # 6. Mise à jour des stats des joueurs (délégué à la couche data)
        if players_stats:
            batch_update_players_stats_data(players_stats)
        
        # 7. Affichage des statistiques
        print("\n" + "="*80)
        print("📊 GAMES IMPORT STATS")
        print("="*80)
        print(f"✅ Parties créées: {stats['created']}")
        print(f"ℹ️  Parties existantes: {stats['existing']}")
        print(f"⏭️  Parties non-ranked ignorées: {stats['skipped_ranked']}")
        print(f"❌ Erreurs: {stats['errors']}")
        print(f"📈 Total traité: {stats['total_processed']}")
        print("="*80 + "\n")
        
        return stats
        
    except Exception as e:
        print(f"\033[91m❌ Erreur critique lors de l'import bulk: {e}\033[0m")
        import traceback
        traceback.print_exc()
        raise e

def import_player_bga_service(bga_id: int) -> dict:
    try:
        # 1. Récupérer les infos du joueur
        player_response = getPlayer(bga_id)
        if not player_response or player_response.get('status') != 1:
            return {
                'status': 0,
                'error': player_response.get('error', 'Unknown error') if player_response else 'No response',
                'player_id': None
            }

        # 2. ✅ Récupérer TOUTES les saisons (triées par saison décroissante)
        seasons = get_all_seasons_data()
        
        if not seasons or len(seasons) == 0:
            print("⚠️  Aucune saison trouvée en base de données")
            return {
                'status': 0,
                'error': 'No seasons found in database',
                'player_id': None
            }
        
        print(f"\n📅 {len(seasons)} saison(s) trouvée(s) : {[s.season for s in seasons]}")
        
        # 3. ✅ Variables pour accumuler les résultats de toutes les saisons
        new_player = None
        all_seasons_stats = {
            'total_games': 0,
            'total_pages': 0,
            'seasons_processed': 0,
            'seasons_with_games': 0,      # ✅ Nouvelles stats
            'seasons_without_games': 0,   # ✅ Nouvelles stats
            'games_by_season': {}
        }
        
        # 4. ✅ Boucler sur TOUTES les saisons
        for currentSeason in seasons:
            print(f"\n{'='*80}")
            print(f"🎯 Traitement de la saison {currentSeason.season}")
            print(f"📅 Période: {datetime.fromtimestamp(currentSeason.start, tz=timezone.utc)} → {datetime.fromtimestamp(currentSeason.end, tz=timezone.utc)}")
            print(f"{'='*80}")
            
            # Récupérer les parties de cette saison avec pagination
            all_games_data = []
            page = 1
            has_more = True
            season_pages = 0
            
            while has_more:
                print(f"📄 Saison {currentSeason.season} - Page {page}...")
                
                try:
                    games_response = getGames(
                        bga_id,
                        start_date=currentSeason.start,
                        end_date=currentSeason.end,
                        page=page
                    )
                    
                    if not games_response or games_response.get('status') != 1:
                        print(f"⚠️  Aucune réponse pour la page {page}")
                        # ✅ Si c'est la première page, pas de parties pour cette saison
                        if page == 1:
                            print(f"ℹ️  Pas de parties pour la saison {currentSeason.season}")
                            all_seasons_stats['seasons_without_games'] += 1
                            all_seasons_stats['games_by_season'][currentSeason.season] = 0
                        break
                    
                    # Extraire les parties de cette page
                    games_data = games_response.get('data', {}).get('tables', [])
                    pagination_info = games_response.get('data', {}).get('pagination', {})
                    
                    if not games_data or len(games_data) == 0:
                        # ✅ Si c'est la première page et qu'elle est vide
                        if page == 1:
                            print(f"ℹ️  Aucune partie pour la saison {currentSeason.season}")
                            all_seasons_stats['seasons_without_games'] += 1
                            all_seasons_stats['games_by_season'][currentSeason.season] = 0
                        else:
                            print(f"ℹ️  Fin des parties à la page {page}")
                        break
                    
                    # Ajouter les parties de cette page
                    all_games_data.extend(games_data)
                    season_pages += 1
                    
                    print(f"✅ Page {page} : {len(games_data)} parties récupérées")
                    
                    # Vérifier s'il y a d'autres pages
                    has_more = pagination_info.get('has_more', False)
                    
                    if has_more:
                        page += 1
                        time.sleep(0.3)
                    else:
                        print(f"✅ Dernière page atteinte")
                        break
                        
                except Exception as e:
                    print(f"❌ Erreur lors de la récupération de la page {page}: {e}")
                    # ✅ Si c'est la première page, considérer qu'il n'y a pas de parties
                    if page == 1:
                        print(f"⚠️  Impossible de récupérer les parties de la saison {currentSeason.season}")
                        all_seasons_stats['seasons_without_games'] += 1
                        all_seasons_stats['games_by_season'][currentSeason.season] = 0
                    break
            
            # Afficher le résumé de cette saison
            print(f"\n📊 Saison {currentSeason.season} : {len(all_games_data)} parties sur {season_pages} page(s)")
            
            # ✅ Stocker les stats de cette saison
            all_seasons_stats['games_by_season'][currentSeason.season] = len(all_games_data)
            all_seasons_stats['total_games'] += len(all_games_data)
            all_seasons_stats['total_pages'] += season_pages
            
            # ✅ Si aucune partie pour cette saison, passer à la suivante SANS erreur
            if not all_games_data or len(all_games_data) == 0:
                print(f"⏭️  Passage à la saison suivante...")
                continue
            
            # ✅ On a trouvé des parties pour cette saison
            all_seasons_stats['seasons_with_games'] += 1
            
            # 5. ✅ Créer le joueur lors de la première saison avec des parties
            if new_player is None:
                try:
                    new_player = Player(
                        bga_id=player_response['data'].get('bga_id', 0),
                        name=player_response['data'].get('name', None),
                        country=player_response['data'].get('country', None),
                        bio=player_response['data'].get('bio', None),
                        is_active=True
                    )
                    new_player = create_player_data(new_player)
                    print(f"\n✅ Joueur créé: {new_player.name} (ID: {new_player.id})")
                except Exception as e:
                    print(f"❌ Erreur lors de la création du joueur: {e}")
                    return {
                        'status': 0,
                        'error': f'Failed to create player: {str(e)}',
                        'player_id': None
                    }
            
            # 6. ✅ Importer les parties de cette saison
            try:
                print(f"\n💾 Import des parties de la saison {currentSeason.season}...")
                games_stats = import_games_bulk_service(
                    str(new_player.id), 
                    all_games_data, 
                    currentSeason.season
                )
                
                all_seasons_stats['seasons_processed'] += 1
                
                # Affichage des stats de cette saison
                print(f"\n📊 Saison {currentSeason.season} - Résultats:")
                print(f"  ✅ Nouvelles parties: {games_stats['created']}")
                print(f"  ℹ️  Déjà existantes: {games_stats['existing']}")
                print(f"  ⏭️  Non-ranked: {games_stats['skipped_ranked']}")
                print(f"  ❌ Erreurs: {games_stats['errors']}")
                
            except Exception as e:
                print(f"❌ Erreur lors de l'import des parties de la saison {currentSeason.season}: {e}")
                import traceback
                traceback.print_exc()
                # ✅ Continuer avec la saison suivante même en cas d'erreur
                continue
        
        # 7. ✅ Affichage récapitulatif GLOBAL
        if new_player is None:
            print("\n⚠️  Aucune partie trouvée pour ce joueur sur aucune saison")
            return {
                'status': 0,
                'error': 'No games found for this player in any season',
                'player_id': None,
                'seasons_checked': len(seasons),
                'seasons_without_games': all_seasons_stats['seasons_without_games']
            }
        
        print("\n" + "="*80)
        print(f"🏆 RÉSUMÉ GLOBAL - {new_player.name}")
        print("="*80)
        print(f"📅 Saisons vérifiées: {len(seasons)}")
        print(f"✅ Saisons avec parties: {all_seasons_stats['seasons_with_games']}")
        print(f"⭕ Saisons sans parties: {all_seasons_stats['seasons_without_games']}")
        print(f"💾 Saisons importées: {all_seasons_stats['seasons_processed']}")
        print(f"🎮 Total de parties: {all_seasons_stats['total_games']}")
        print(f"📄 Total de pages: {all_seasons_stats['total_pages']}")
        print(f"\n📊 Détail par saison:")
        for season_num in sorted(all_seasons_stats['games_by_season'].keys(), reverse=True):
            games_count = all_seasons_stats['games_by_season'][season_num]
            if games_count > 0:
                print(f"  ✅ Saison {season_num}: {games_count} parties")
            else:
                print(f"  ⭕ Saison {season_num}: Aucune partie")
        print("="*80 + "\n")
        
        return {
            'status': 1,
            'player_id': str(new_player.id),
            'seasons_stats': all_seasons_stats,
            'games_by_season': all_seasons_stats['games_by_season']
        }
            
    except Exception as e:
        print(f"\033[91m❌ Erreur critique lors de l'import du joueur: {e}\033[0m")
        import traceback
        traceback.print_exc()
        return {
            'status': 0,
            'error': str(e),
            'player_id': None
        }

def get_player_history_service(player_id: str, season: int) -> list[Game]:
    player = get_player_by_id_data(player_id)
    if not player:
        raise ValueError(f"Player not found: {player_id}")
    
    # Récupérer les parties du joueur
    games = get_player_history_data(player_id, season)
    
    return [game.json() for game in games]

def import_ladder_service(season: int, max_pages: int = None) -> dict:
    try:
        print(f"\n🔄 Import du ladder saison {season}...")
        
        # Statistiques globales
        global_stats = {
            'total_ranks': 0,
            'players_created': 0,
            'players_existing': 0,
            'season_stats_created': 0,
            'errors': 0,
            'pages_processed': 0
        }
        
        season_str = str(season)
        
        # Liste pour accumuler toutes les données de saison
        all_season_stats = []
        
        # ✅ Pagination automatique
        page = 0
        has_more = True
        
        while has_more:
            # Vérifier la limite de pages si définie
            if max_pages is not None and page >= max_pages:
                print(f"⚠️  Limite de {max_pages} pages atteinte")
                break
            
            print(f"\n📄 Récupération de la page {page + 1}...")
            
            # Récupérer les données de la page
            response = import_ladder_from_bga(season, page)
            
            if response.get('status') != 1:
                print(f"❌ Échec de la récupération de la page {page + 1}")
                break
            
            ladder_data = response.get('data', {})
            ranks = ladder_data.get('ranks', [])
            pagination = response.get('pagination', {})
            
            if not ranks:
                print(f"ℹ️  Aucun résultat sur la page {page + 1}, arrêt de la pagination")
                break
            
            global_stats['pages_processed'] += 1
            global_stats['total_ranks'] += len(ranks)
            
            # Traiter chaque joueur de la page
            for rank_data in ranks:
                try:
                    bga_id = int(rank_data.get('id'))
                    name = rank_data.get('name')
                    country_code = rank_data.get('country', {}).get('code', 'XX')
                    arena_points_str = rank_data.get('arena', '0.0')
                    if '.' in str(arena_points_str):
                        arena_points = int(str(arena_points_str).split('.')[1])  # "501.1900" -> 1900
                    else:
                        arena_points = 0
                    rank_no = int(rank_data.get('rank_no', 0))
                    
                    # Récupérer ou créer le joueur
                    player = get_player_by_bga_id_data(bga_id)
                    
                    if not player:
                        player = Player(
                            bga_id=bga_id,
                            name=name,
                            country=country_code,
                            total_points=0,
                            total_wins=0,
                            total_losses=0,
                            total_draws=0,
                            win_rate=0.0,
                            is_active=False
                        )
                        player = create_player_data(player)
                        global_stats['players_created'] += 1
                        print(f"  ✅ Joueur créé: {name} (#{rank_no})")
                    else:
                        global_stats['players_existing'] += 1
                    
                    # Préparer les données de saison
                    all_season_stats.append({
                        'player_id': player.id,
                        'season': season_str,
                        'points': int(arena_points),
                        'rank': rank_no,
                        'highest_rank': rank_no
                    })
                    
                except Exception as e:
                    print(f"  \033[91m❌ Erreur sur le joueur {rank_data.get('name')}: {e}\033[0m")
                    global_stats['errors'] += 1
                    continue
            
            # Vérifier s'il y a d'autres pages
            has_more = pagination.get('has_more', False)
            
            if has_more:
                print(f"✅ Page {page + 1} traitée, passage à la page suivante...")
                page += 1
                time.sleep(0.5)  # Petit délai pour ne pas surcharger l'API
            else:
                print(f"✅ Page {page + 1} traitée, dernière page atteinte")
        
        # ✅ Bulk upsert de toutes les stats de saison en une seule fois
        if all_season_stats:
            print(f"\n💾 Enregistrement de {len(all_season_stats)} stats de saison en base...")
            upserted_count = bulk_upsert_season_stats_data(all_season_stats)
            global_stats['season_stats_created'] = upserted_count
        
        # Affichage des statistiques finales
        print("\n" + "="*80)
        print(f"📊 LADDER IMPORT STATS - SEASON {season}")
        print("="*80)
        print(f"📄 Pages traitées: {global_stats['pages_processed']}")
        print(f"✅ Joueurs créés: {global_stats['players_created']}")
        print(f"ℹ️  Joueurs existants: {global_stats['players_existing']}")
        print(f"📈 Stats de saison créées/maj: {global_stats['season_stats_created']}")
        print(f"❌ Erreurs: {global_stats['errors']}")
        print(f"📊 Total traité: {global_stats['total_ranks']}")
        print("="*80 + "\n")
        
        return {
            'status': 1,
            'season': season_str,
            'stats': global_stats
        }
        
    except Exception as e:
        print(f"\033[91m❌ Erreur critique lors de l'import du ladder: {e}\033[0m")
        import traceback
        traceback.print_exc()
        return {
            'status': 0,
            'error': str(e)
        }
    
def get_ladder_by_season_service(
    season: int, 
    include_player: bool = True,
    page: int = 1,
    limit: int = 100
) -> dict:
    try:
        season_str = str(season)
        
        # ✅ Récupérer les stats avec pagination
        stats, total = get_season_stats_data(
            season=season, 
            include_player=include_player,
            page=page,
            limit=limit
        )
        
        if not stats:
            return {
                'season': season_str,
                'total_players': 0,
                'total_points': 0,
                'avg_points': 0,
                'ladder': [],
                'pagination': {
                    'current_page': page,
                    'total_pages': 0,
                    'total_players': 0,
                    'limit': limit
                }
            }
        
        # ✅ Sérialiser avec les données du player
        ladder = [stat.json(include_player=include_player) for stat in stats]
        
        # Calculer quelques métadonnées utiles (sur la page actuelle)
        page_players = len(stats)
        page_points = sum(stat.points for stat in stats)
        page_avg_points = page_points / page_players if page_players > 0 else 0
        
        return {
            'season': season_str,
            'total_players': total,
            'total_points': page_points,  # Points de la page actuelle
            'avg_points': round(page_avg_points, 2),  # Moyenne de la page actuelle
            'ladder': ladder,
            'pagination': {
                'current_page': page,
                'total_pages': (total + limit - 1) // limit,  # Arrondi supérieur
                'total_players': total,
                'limit': limit
            }
        }
        
    except Exception as e:
        print(f"\033[91m❌ Erreur lors de la récupération du ladder: {e}\033[0m")
        import traceback
        traceback.print_exc()
        raise e
    
def get_all_seasons_service() -> list:
    seasons = get_all_seasons_data()
    return [season.json() for season in seasons]

def get_total_players_service() -> int:
    return count_total_players_data()