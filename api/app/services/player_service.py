from datetime import datetime, timezone
import time
import uuid
from typing import List, Dict, Optional
from app.models.player import Player, Game
from app.scripts.bga_routine import getGames, getLogs, getPlayer, getSearch, import_ladder_from_bga
from app.data.player_data import (
    bulk_upsert_season_stats_data,
    count_total_players_data,
    create_player_data,
    get_player_by_id_data,
    get_player_history_data,
    get_season_stats_by_player_data,
    get_season_stats_data,
    search_players_data,
    get_player_by_bga_id_data,
    get_game_by_table_id_data,
    bulk_insert_games_data,
    batch_update_players_stats_data,
    get_all_seasons_data,
    bulk_upsert_season_stats_data,
    update_player_data
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
        reload_player_service(player_id)
        player = get_player_by_id_data(player_id)

    return player.json()

def _get_or_create_player_from_bga_data(player_data: dict) -> Player:
    bga_id = player_data.get('id')
    
    # Chercher le joueur existant
    existing_player = get_player_by_bga_id_data(bga_id)
    if (existing_player):
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
        game_played_at = game.played_at
        last_game_at = stats['last_game_at']
        
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
                game_played_at = game.played_at
                
                for player_id in [main_player.id, opponent.id]:
                    last_game_at = players_stats[player_id]['last_game_at']
                    
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
            # ✅ Vérifier si le joueur est banni
            if player_response.get('bga_banned'):
                # Chercher si le joueur existe déjà en base
                existing_player = get_player_by_bga_id_data(bga_id)
                if existing_player:
                    # Marquer le joueur comme banni
                    existing_player.bga_banned = True
                    update_player_data(existing_player)
                    print(f"⚠️  Joueur {existing_player.name} marqué comme banni")
                    
                return {
                    'status': 0,
                    'error': 'Player is banned or does not exist on BGA',
                    'player_id': str(existing_player.id) if existing_player else None,
                    'bga_banned': True
                }
            
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
            'seasons_with_games': 0,
            'seasons_without_games': 0,
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
            season_pages = 0  # ✅ Initialiser AVANT la boucle while
            
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
                        if page == 1:
                            print(f"ℹ️  Pas de parties pour la saison {currentSeason.season}")
                            all_seasons_stats['seasons_without_games'] += 1
                            all_seasons_stats['games_by_season'][currentSeason.season] = 0
                        break
                    
                    # Extraire les parties de cette page
                    games_data = games_response.get('data', {}).get('tables', [])
                    pagination_info = games_response.get('data', {}).get('pagination', {})
                    
                    if not games_data or len(games_data) == 0:
                        if page == 1:
                            print(f"ℹ️  Aucune partie pour la saison {currentSeason.season}")
                            all_seasons_stats['seasons_without_games'] += 1
                            all_seasons_stats['games_by_season'][currentSeason.season] = 0
                        else:
                            print(f"ℹ️  Fin des parties à la page {page}")
                        break
                    
                    # Ajouter les parties de cette page
                    all_games_data.extend(games_data)
                    season_pages += 1  # ✅ Incrémenter le compteur
                    
                    print(f"✅ Page {page} : {len(games_data)} parties récupérées")
                    
                    # Vérifier s'il y a d'autres pages
                    has_more = pagination_info.get('has_more', False)
                    
                    if has_more:
                        page += 1
                        time.sleep(0.1)
                    else:
                        print(f"✅ Dernière page atteinte")
                        break
                        
                except Exception as e:
                    print(f"❌ Erreur lors de la récupération de la page {page}: {e}")
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
            except Exception as e:
                print(f"❌ Erreur lors de l'import des parties de la saison {currentSeason.season}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # 7. ✅ VÉRIFICATION : Si aucune partie trouvée sur AUCUNE saison, retourner une erreur
        if all_seasons_stats['total_games'] == 0:
            print("\n" + "="*80)
            print("⚠️  AUCUNE PARTIE TROUVÉE")
            print("="*80)
            print(f"❌ Le joueur BGA #{bga_id} n'a aucune partie d'Altered sur les {len(seasons)} saisons vérifiées")
            print(f"📅 Saisons vérifiées: {', '.join(str(s.season) for s in seasons)}")
            print("="*80 + "\n")
            
            return {
                'status': 0,
                'error': f'No Altered games found for player {bga_id} across all seasons',
                'player_id': None,
                'seasons_checked': len(seasons),
                'seasons_without_games': all_seasons_stats['seasons_without_games'],
                'details': {
                    'bga_id': bga_id,
                    'seasons_verified': [s.season for s in seasons],
                    'total_pages_checked': all_seasons_stats['total_pages']
                }
            }
        
        # 8. ✅ Affichage récapitulatif GLOBAL (si des parties ont été trouvées)
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
            'player_name': new_player.name,
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
                time.sleep(0.1)  # Petit délai pour ne pas surcharger l'API
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

def get_player_overview_service(player_id: str, season: int) -> dict:
    playerSeasonStats = get_season_stats_by_player_data(player_id=player_id, season=season)
    return playerSeasonStats.json() if playerSeasonStats else {}

def reload_player_service(player_id: str) -> dict:
    try:
        # 1. Validation du joueur
        player = get_player_by_id_data(player_id)
        if not player:
            return {
                'status': 0,
                'error': f'Player not found: {player_id}'
            }
        
        print(f"\n🔄 Rechargement des données pour {player.name} (BGA ID: {player.bga_id})")
        
        # 2. Déterminer le timestamp de départ
        if player.last_game_at:
            start_timestamp = int(player.last_game_at.timestamp())
            print(f"📅 Dernière partie: {player.last_game_at}")
            print(f"🕐 Timestamp: {start_timestamp}")
        else:
            # Aucune partie, on part de la première saison
            print("⚠️  Aucune partie enregistrée, rechargement complet...")
            seasons = get_all_seasons_data()
            if not seasons:
                return {'status': 0, 'error': 'No seasons found'}
            start_timestamp = min(s.start for s in seasons)
        
        # 3. Récupérer toutes les saisons
        all_seasons = get_all_seasons_data()
        if not all_seasons:
            return {'status': 0, 'error': 'No seasons found in database'}
        
        print(f"📅 {len(all_seasons)} saisons disponibles")
        
        # 4. Statistiques du rechargement
        reload_stats = {
            'new_games': 0,
            'existing_games': 0,
            'skipped_ranked': 0,
            'errors': 0,
            'total_pages': 0,
            'seasons_affected': set()
        }
        
        # 5. Récupération de TOUTES les nouvelles parties (pagination automatique)
        print(f"\n📥 Récupération des nouvelles parties depuis le {player.last_game_at}...")
        
        all_new_games = []
        page = 1
        has_more = True
        
        while has_more:
            print(f"📄 Page {page}...")
            
            try:
                games_response = getGames(
                    player.bga_id,
                    start_date=start_timestamp,
                    page=page
                )
                
                if not games_response or games_response.get('status') != 1:
                    if page == 1:
                        print("ℹ️  Aucune nouvelle partie")
                    break
                
                games_data = games_response.get('data', {}).get('tables', [])
                pagination_info = games_response.get('data', {}).get('pagination', {})
                
                if not games_data:
                    break
                
                all_new_games.extend(games_data)
                reload_stats['total_pages'] += 1
                
                print(f"✅ Page {page}: {len(games_data)} parties récupérées")
                
                has_more = pagination_info.get('has_more', False)
                if has_more:
                    page += 1
                    time.sleep(0.1)
                else:
                    break
                    
            except Exception as e:
                print(f"❌ Erreur page {page}: {e}")
                reload_stats['errors'] += 1
                break
        
        print(f"\n📊 Total récupéré: {len(all_new_games)} nouvelles parties")
        
        # 6. ✅ Si nouvelles parties trouvées, les importer
        if all_new_games:
            print(f"\n💾 Import des nouvelles parties...")
            
            # Grouper les parties PAR SAISON (basé sur end_timestamp)
            games_by_season = {}
            
            for game_data in all_new_games:
                # Déterminer la saison de cette partie
                game_end_timestamp = game_data.get('end_timestamp')
                
                if not game_end_timestamp:
                    print(f"⚠️  Partie sans end_timestamp: {game_data.get('table_id')}")
                    reload_stats['errors'] += 1
                    continue
                
                # Trouver dans quelle saison cette partie se situe
                game_season = None
                for season in all_seasons:
                    if season.start <= game_end_timestamp <= season.end:
                        game_season = season.season
                        break
                
                if game_season is None:
                    print(f"⚠️  Partie hors saison (timestamp: {game_end_timestamp}): {game_data.get('table_id')}")
                    reload_stats['errors'] += 1
                    continue
                
                # Grouper par saison
                if game_season not in games_by_season:
                    games_by_season[game_season] = []
                
                games_by_season[game_season].append(game_data)
                reload_stats['seasons_affected'].add(game_season)
            
            print(f"\n📅 Saisons concernées: {sorted(reload_stats['seasons_affected'])}")
            
            # Importer les parties par saison
            for season_num in sorted(games_by_season.keys()):
                season_games = games_by_season[season_num]
                
                print(f"\n{'='*80}")
                print(f"💾 Import saison {season_num}: {len(season_games)} parties")
                print(f"{'='*80}")
                
                try:
                    games_stats = import_games_bulk_service(
                        player_id,
                        season_games,
                        season_num
                    )
                    
                    reload_stats['new_games'] += games_stats['created']
                    reload_stats['existing_games'] += games_stats['existing']
                    reload_stats['skipped_ranked'] += games_stats['skipped_ranked']
                    reload_stats['errors'] += games_stats['errors']
                    
                    print(f"📊 Saison {season_num}:")
                    print(f"  ✅ Nouvelles: {games_stats['created']}")
                    print(f"  ℹ️  Existantes: {games_stats['existing']}")
                    print(f"  ⏭️  Non-ranked: {games_stats['skipped_ranked']}")
                    
                except Exception as e:
                    print(f"❌ Erreur import saison {season_num}: {e}")
                    import traceback
                    traceback.print_exc()
                    reload_stats['errors'] += 1
                    continue
        else:
            print("ℹ️  Aucune nouvelle partie à importer")
        
        # 7. ✅ RECALCUL COMPLET DES STATISTIQUES (toujours effectué)
        print(f"\n{'='*80}")
        print("📊 RECALCUL DES STATISTIQUES")
        print(f"{'='*80}")
        
        try:
            # 7.1. Récupérer TOUTES les parties du joueur (toutes saisons)
            all_player_games = get_player_history_data(player_id, season=None)
            print(f"🎮 Total de parties en base: {len(all_player_games)}")
            
            if len(all_player_games) == 0:
                print("⚠️  Aucune partie en base pour ce joueur")
                return {
                    'status': 1,
                    'player_id': player_id,
                    'message': 'No games found for this player',
                    'stats': reload_stats
                }
            
            # 7.2. Recalculer les statistiques GLOBALES
            player_uuid = uuid.UUID(player_id)
            global_stats = _calculate_player_stats_from_games(all_player_games, player_uuid)
            
            total_games = len(all_player_games)
            total_wins = global_stats['wins']
            total_losses = global_stats['losses']
            total_draws = global_stats['draws']
            win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0
            
            # Mettre à jour le joueur
            player.total_wins = total_wins
            player.total_losses = total_losses
            player.total_draws = total_draws
            player.win_rate = round(win_rate, 2)
            player.last_game_at = global_stats['last_game_at']  # ✅ Timestamp int
            player.updated_at = datetime.now(timezone.utc)
            player.is_active = True
            
            # Sauvegarder
            update_player_data(player)
        except Exception as e:
            print(f"❌ Erreur recalcul stats globales: {e}")
            import traceback
            traceback.print_exc()
            reload_stats['errors'] += 1
        
        # 7.3. ✅ Recalculer les statistiques PAR SAISON (TOUTES les saisons avec parties)
        print(f"\n📅 Recalcul des stats par saison...")

        try:
            season_stats_updates = []
            
            # ✅ Récupérer TOUTES les saisons où le joueur a des parties
            all_seasons_with_games = set()
            for game in all_player_games:
                all_seasons_with_games.add(game.season)
            
            all_seasons_with_games = sorted(all_seasons_with_games)
            
            print(f"🎯 Recalcul de {len(all_seasons_with_games)} saison(s): {all_seasons_with_games}")
            
            # Pour chaque saison où le joueur a des parties
            for season_num in all_seasons_with_games:
                # Récupérer TOUTES les parties de cette saison
                season_games = [g for g in all_player_games if g.season == season_num]
                
                if not season_games:
                    print(f"  ⚠️  Saison {season_num}: Aucune partie (ignorée)")
                    continue
                
                # Calculer les stats
                season_stats = _calculate_player_stats_from_games(season_games, player_uuid)
                
                season_total = len(season_games)
                season_wins = season_stats['wins']
                season_losses = season_stats['losses']
                season_draws = season_stats['draws']
                season_win_rate = (season_wins / season_total * 100) if season_total > 0 else 0.0
                
                # Récupérer les stats existantes pour conserver rank et highest_rank
                existing_stats = get_season_stats_by_player_data(player_id, season_num)
                
                season_stats_updates.append({
                    'player_id': player_uuid,
                    'season': str(season_num),
                    'wins': season_wins,
                    'losses': season_losses,
                    'draws': season_draws,
                    'win_rate': round(season_win_rate, 2),
                    'points': existing_stats.points if existing_stats else 0,
                    'rank': existing_stats.rank if existing_stats else None,
                    'highest_rank': existing_stats.highest_rank if existing_stats else None
                })
                
                print(f"  📅 Saison {season_num}:")
                print(f"    🎮 Parties: {season_total}")
                print(f"    ✅ Victoires: {season_wins}")
                print(f"    ❌ Défaites: {season_losses}")
                print(f"    ⚖️  Nuls: {season_draws}")
                print(f"    📊 Win rate: {season_win_rate:.2f}%")
                if existing_stats:
                    print(f"    🏆 Points (ladder): {existing_stats.points}")
                    print(f"    📍 Rank: {existing_stats.rank or 'N/A'}")
            
            # Bulk update
            if season_stats_updates:
                updated_count = bulk_upsert_season_stats_data(season_stats_updates)
                print(f"\n✅ {updated_count} saison(s) mise(s) à jour")
            else:
                print(f"\n⚠️  Aucune saison à mettre à jour")
            
        except Exception as e:
            print(f"❌ Erreur recalcul stats par saison: {e}")
            import traceback
            traceback.print_exc()
            reload_stats['errors'] += 1
        
        # 8. Résumé final
        reload_stats['seasons_affected'] = sorted(reload_stats['seasons_affected']) if reload_stats['seasons_affected'] else []
        
        print("\n" + "="*80)
        print(f"🏆 RECHARGEMENT TERMINÉ - {player.name}")
        print("="*80)
        print(f"✅ Nouvelles parties importées: {reload_stats['new_games']}")
        print(f"ℹ️  Parties déjà existantes: {reload_stats['existing_games']}")
        print(f"⏭️  Parties non-ranked ignorées: {reload_stats['skipped_ranked']}")
        print(f"📄 Pages traitées: {reload_stats['total_pages']}")
        if reload_stats['seasons_affected']:
            print(f"📅 Saisons avec nouvelles parties: {', '.join(map(str, reload_stats['seasons_affected']))}")
        else:
            print(f"📅 Aucune nouvelle partie (stats recalculées quand même)")
        print(f"🔄 Toutes les stats ont été recalculées")
        print(f"❌ Erreurs: {reload_stats['errors']}")
        print("="*80 + "\n")
        
        return {
            'status': 1,
            'player_id': player_id,
            'player_name': player.name,
            'stats': reload_stats,
            'updated_stats': {
                'total_games': total_games,
                'total_wins': player.total_wins,
                'total_losses': player.total_losses,
                'total_draws': player.total_draws,
                'win_rate': player.win_rate,
                'last_game_at': player.last_game_at.isoformat() if player.last_game_at else None
            }
        }
        
    except Exception as e:
        print(f"\033[91m❌ Erreur critique lors du rechargement: {e}\033[0m")
        import traceback
        traceback.print_exc()
        return {
            'status': 0,
            'error': str(e),
            'player_id': player_id
        }
    
def import_table_service(table_id: int) -> dict:
    try:
        print(f"\n🔄 Import de la table ID: {table_id}...")

        table = get_game_by_table_id_data(table_id)
        
        # 1. Récupérer les données de la table depuis l'API BGA
        result = getLogs(table_id)
        if result.get('status', 0) != 1:
            return {
                'status': 0,
                'error': f"Err : {result.get('error', 'err API')}",
                'table_id': table_id
            }

        data = result.get('data', {})
        logs = data.get('logs', [])
        # logs = data.get('data', [])
        if not logs or len(logs) == 0:
            return {
                'status': 0,
                'error': f'No logs found for table ID: {table_id}',
                'table_id': table_id
            }
        
        decks_selections = []
        
        for log in logs:
            log_data = log.get('data', [])[0]
            if log_data.get('type', '') == 'updateInitialPrecoDeckSelection':
                private_data = log_data.get('args', {}).get('args', {}).get('_private')
                private_data['player_id'] = int(log.get('channel', '').replace('/player/p', ''))
                if private_data:
                    if private_data.get('selection', '') == 'API':
                        private_data.pop('decks', None)
                    decks_selections.append(private_data)
                    if len(decks_selections) == 2:
                        break

        return {
            'status': 1,
            'table': decks_selections
        }
        
    except Exception as e:
        print(f"\033[91m❌ Erreur critique lors de l'import de la table: {e}\033[0m")
        import traceback
        traceback.print_exc()
        return {
            'status': 0,
            'error': str(e),
            'table_id': table_id
        }