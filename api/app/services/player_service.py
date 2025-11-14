from datetime import datetime, timezone
import time
import uuid
from typing import List, Dict, Optional
from app.scripts.bga_get_deck import getGamerView
from app.models.player import Player
from app.models.game import Game
from app.scripts.bga_routine import getGames, getLogs, getPlayer, getSearch, getTableInfos, import_ladder_from_bga
from app.data.player_data import (
    bulk_upsert_season_stats_data,
    count_total_players_data,
    create_player_data,
    get_or_create_tournament_data,
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
    update_game_data,
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
    
    # Filtrer les joueurs anonymisés présents dans la BDD
    players = data.get('players', [])
    filtered_players = []
    
    for player in players:
        bga_id = player.get('bga_id')
        if bga_id:
            existing_player = get_player_by_bga_id_data(bga_id)
            # Exclure si le joueur existe ET est anonymisé
            if existing_player and existing_player.is_anonymized:
                continue
        filtered_players.append(player)
    
    # Mettre à jour les données avec les joueurs filtrés
    if 'players' in data:
        data['players'] = filtered_players
    
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
        
        # ✅ Utiliser game.start (date de DÉBUT) au lieu de game.played_at (date de FIN)
        game_start_date = game.start
        last_game_at = stats['last_game_at']
        
        if last_game_at is None or (game_start_date is not None and game_start_date > last_game_at):
            stats['last_game_at'] = game_start_date
    
    return stats

def import_games_bulk_service(main_player_id: str, games_data_from_bga: list, season: int) -> dict:
    try:
        # 1. Validation du joueur principal
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
                
                # ✅ Utiliser game.start (date de DÉBUT) au lieu de game.played_at (date de FIN)
                game_start_date = game.start
                
                for player_id in [main_player.id, opponent.id]:
                    last_game_at = players_stats[player_id]['last_game_at']
                    
                    if last_game_at is None or (game_start_date is not None and game_start_date > last_game_at):
                        players_stats[player_id]['last_game_at'] = game_start_date
                
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
    hero: str = None,
    include_player: bool = True,
    page: int = 1,
    limit: int = 100
) -> dict:
    try:
        season_str = str(season)
        
        # ✅ Récupérer les stats avec pagination
        stats, total = get_season_stats_data(
            season=season,
            hero=hero,
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
        
        # ✅ Sérialiser avec les données du player (masquer l'ID si anonymisé)
        ladder = []
        for stat in stats:
            stat_json = stat.json(include_player=include_player)
            
            # ✅ Si le joueur est anonymisé, supprimer son ID
            if include_player and stat.player and stat.player.is_anonymized:
                stat_json['player']['id'] = None
            
            ladder.append(stat_json)
        
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
            'seasons_affected': set(),
            'tables_updated': 0,  # ✅ Nouveau
            'incomplete_tables': 0  # ✅ Nouveau
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
        
        # 7. ✅ NORMALISATION DES TABLES INCOMPLÈTES
        print(f"\n{'='*80}")
        print("🔍 VÉRIFICATION DES TABLES INCOMPLÈTES")
        print(f"{'='*80}")
        
        try:
            # Récupérer TOUTES les parties du joueur (toutes saisons)
            all_player_games = get_player_history_data(player_id, season=None)
            print(f"🎮 Total de parties en base: {len(all_player_games)}")
            
            # Identifier les tables incomplètes (sans faction ou sans héros)
            incomplete_tables = []
            
            for game in all_player_games:
                is_incomplete = (
                    game.player1_faction is None or 
                    game.player2_faction is None or 
                    game.player1_reflexion_time is None or game.player2_reflexion_time is None or 
                    game.player1_nb_turns is None or game.player2_nb_turns is None
                )
                
                if is_incomplete:
                    incomplete_tables.append(game)
            
            reload_stats['incomplete_tables'] = len(incomplete_tables)
            
            if incomplete_tables:
                print(f"\n⚠️  {len(incomplete_tables)} table(s) incomplète(s) détectée(s)")
                print(f"🔄 Mise à jour en cours...\n")
                
                # ✅ Mettre à jour chaque table incomplète
                for idx, game in enumerate(incomplete_tables, 1):
                    try:
                        # ✅ Appeler import_table_service pour compléter les données
                        import_table_service(game.table_id)

                        # if idx < len(incomplete_tables):
                        #     time.sleep(0.1)
                            
                    except Exception as e:
                        print(f"  ❌ Erreur table #{game.table_id}: {e}")
                        reload_stats['errors'] += 1
                        continue
                
                print(f"\n✅ Normalisation terminée: {reload_stats['tables_updated']}/{reload_stats['incomplete_tables']} tables mises à jour")
            else:
                print("✅ Toutes les tables sont complètes")
                
        except Exception as e:
            print(f"❌ Erreur lors de la normalisation des tables: {e}")
            import traceback
            traceback.print_exc()
            reload_stats['errors'] += 1
        
        # 8. ✅ RECALCUL COMPLET DES STATISTIQUES (toujours effectué)
        print(f"\n{'='*80}")
        print("📊 RECALCUL DES STATISTIQUES")
        print(f"{'='*80}")
        
        try:
            # 8.1. Recharger TOUTES les parties (après normalisation)
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
            
            # 8.2. Recalculer les statistiques GLOBALES
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
            player.last_game_at = global_stats['last_game_at']
            player.updated_at = datetime.now(timezone.utc)
            player.is_active = True
            
            # Sauvegarder
            update_player_data(player)
        except Exception as e:
            print(f"❌ Erreur recalcul stats globales: {e}")
            import traceback
            traceback.print_exc()
            reload_stats['errors'] += 1
        
        # 8.3. ✅ Recalculer les statistiques PAR SAISON avec enrichissement
        print(f"\n📅 Recalcul des stats par saison (enrichies)...")
    
        try:
            season_stats_updates = []
            
            # Récupérer TOUTES les saisons où le joueur a des parties
            all_seasons_with_games = set()
            for game in all_player_games:
                all_seasons_with_games.add(game.season)
            
            all_seasons_with_games = sorted(all_seasons_with_games)
            
            print(f"🎯 Recalcul de {len(all_seasons_with_games)} saison(s): {all_seasons_with_games}")
            
            # Pour chaque saison où le joueur a des parties
            for season_num in all_seasons_with_games:
                # ✅ Calculer TOUTES les stats (basiques + enrichies) en un seul pass
                enriched_stats = calculate_enriched_season_stats(
                    player_uuid,
                    season_num,
                    all_player_games  # Passer toutes les parties (filtrage interne)
                )
                
                # ✅ Récupérer l'objet PlayerSeasonStats existant (ou le créer)
                existing_stats = get_season_stats_by_player_data(player_id, season_num)
                
                if existing_stats:
                    # ✅ Mettre à jour l'objet existant
                    existing_stats.wins = enriched_stats['wins']
                    existing_stats.losses = enriched_stats['losses']
                    existing_stats.draws = enriched_stats['draws']
                    existing_stats.win_rate = enriched_stats['win_rate']
                    existing_stats.most_played_faction = enriched_stats.get('most_played_faction')
                    existing_stats.most_played_hero = enriched_stats.get('most_played_hero')
                    existing_stats.faction_stats = enriched_stats.get('faction_stats', {})
                    existing_stats.hero_stats = enriched_stats.get('hero_stats', {})
                    existing_stats.total_reflexion_time = enriched_stats.get('total_reflexion_time')
                    existing_stats.total_turns = enriched_stats.get('total_turns')
                    existing_stats.fastest_game_minutes = enriched_stats.get('fastest_game_minutes')
                    existing_stats.slowest_game_minutes = enriched_stats.get('slowest_game_minutes')
                    existing_stats.current_streak = enriched_stats.get('current_streak', 0)
                    existing_stats.best_win_streak = enriched_stats.get('best_win_streak', 0)
                    existing_stats.worst_loss_streak = enriched_stats.get('worst_loss_streak', 0)
                    existing_stats.updated_at = datetime.now(timezone.utc)
                    
                    season_stats_updates.append(existing_stats)
                else:
                    # ✅ Créer un nouvel objet PlayerSeasonStats
                    from app.models.player import PlayerSeasonStats
                    
                    new_stats = PlayerSeasonStats(
                        player_id=player_uuid,
                        season=str(season_num),
                        points=0,
                        wins=enriched_stats['wins'],
                        losses=enriched_stats['losses'],
                        draws=enriched_stats['draws'],
                        win_rate=enriched_stats['win_rate'],
                        rank=None,
                        highest_rank=None,
                        most_played_faction=enriched_stats.get('most_played_faction'),
                        most_played_hero=enriched_stats.get('most_played_hero'),
                        faction_stats=enriched_stats.get('faction_stats', {}),
                        hero_stats=enriched_stats.get('hero_stats', {}),
                        total_reflexion_time=enriched_stats.get('total_reflexion_time'),
                        total_turns = enriched_stats.get('total_turns'),
                        fastest_game_minutes=enriched_stats.get('fastest_game_minutes'),
                        slowest_game_minutes=enriched_stats.get('slowest_game_minutes'),
                        current_streak=enriched_stats.get('current_streak', 0),
                        best_win_streak=enriched_stats.get('best_win_streak', 0),
                        worst_loss_streak=enriched_stats.get('worst_loss_streak', 0),
                        tournaments_played=0,
                        tournaments_won=0,
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc)
                    )
                    
                    season_stats_updates.append(new_stats)
                
                print(f"  📅 Saison {season_num}:")
                print(f"    🎮 Parties: {enriched_stats['wins'] + enriched_stats['losses'] + enriched_stats['draws']}")
                print(f"    ✅ Victoires: {enriched_stats['wins']}")
                print(f"    📊 Win rate: {enriched_stats['win_rate']:.2f}%")
                print(f"    🎯 Faction principale: {enriched_stats['most_played_faction']}")
                print(f"    🦸 Héros principal: {enriched_stats['most_played_hero']}")
            
            # ✅ Sauvegarder via la couche data
            # Bulk update
            if season_stats_updates:
                from app.data.player_data import update_season_stats_bulk_data
                
                updated_count = update_season_stats_bulk_data(season_stats_updates)
                print(f"\n✅ {updated_count} saison(s) mise(s) à jour (avec stats enrichies)")
        
        except Exception as e:
            print(f"❌ Erreur recalcul stats par saison: {e}")
            import traceback
            traceback.print_exc()
            reload_stats['errors'] += 1
        
        # 9. Résumé final
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
            print(f"📅 Aucune nouvelle partie")
        print(f"🔧 Tables incomplètes détectées: {reload_stats['incomplete_tables']}")
        print(f"✅ Tables normalisées: {reload_stats['tables_updated']}")
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
        game = get_game_by_table_id_data(table_id)

        ti = getTableInfos(table_id)
        if (ti.get('status', 0) != 1):
            return {
                'status': 0,
                'error': f"Err : {ti.get('error', 'err API')}",
                'table_id': table_id
            }
        

        table_data = ti.get('data', {})
        if table_data:
            result = table_data.get('result', {})
            if not result:
                return {
                    'status': 0,
                    'error': f"No result found for table ID: {table_id}",
                    'table_id': table_id
                }
            
            options = table_data.get('options', {})
            if options:
                opt201 = options.get('201', {})
                if opt201:
                    value = opt201.get('value', None)
                    game.ranked = (value == '2') if value is not None else None

            result = table_data.get('result', {})
            if result and game.ranked:
                players = result.get('player', [])
                for player_data in players:
                    if str(player_data.get('player_id', '')) == str(game.player1.bga_id):
                        arena_points_win = player_data.get('arena_points_win', None)
                        arena_after_game = player_data.get('arena_after_game', None)
                        
                        game.player1_arena_point_win = float(arena_points_win) if arena_points_win is not None else None
                        game.player1_arena_point_after_game = float(arena_after_game) if arena_after_game is not None else None
                    
                    elif str(player_data.get('player_id', '')) == str(game.player2.bga_id):
                        arena_points_win = player_data.get('arena_points_win', None)
                        arena_after_game = player_data.get('arena_after_game', None)
                        
                        game.player2_arena_point_win = float(arena_points_win) if arena_points_win is not None else None
                        game.player2_arena_point_after_game = float(arena_after_game) if arena_after_game is not None else None
                

            if table_data.get('has_tournament', '0') == '1':
                tournament = table_data.get('tournament', {})
                if tournament:
                    tournament_name = tournament.get('tournament_name', None)
                    championship_name = tournament.get('championship_name', None)
                    tournament_bga_id = tournament.get('id', None)

                    if tournament_bga_id and tournament_name:
                        try:
                            tournament = get_or_create_tournament_data(
                                bga_id=tournament_bga_id,
                                tournament_name=tournament_name,
                                championship_name=championship_name
                            )
                            
                            game.tournament_id = tournament.id
                            print(f"🏆 Partie #{table_id} associée au tournoi '{tournament_name}'")
                        except Exception as e:
                            print(f"⚠️  Erreur création/association tournoi: {e}")
                    else:
                        print(f"⚠️  Données de tournoi incomplètes pour la partie #{table_id}")

            stats = result.get('stats', {})
            if not stats:
                return {
                    'status': 0,
                    'error': f"No stats found for table ID: {table_id}",
                    'table_id': table_id
                }

            table = stats.get('table', {})
            if table:
                days_value = table.get('days', {}).get('value', 0)
                if days_value is not None:
                    game.round = int(days_value)

                winner_hero_model = get_faction_hero_by_label(table.get('gameWinner', {}).get('valuelabel', None))
                loser_hero_model = get_faction_hero_by_label(table.get('gameLooser', {}).get('valuelabel', None))
                if game.winner_id == game.player1_id:
                    # Player1 a gagné → Player1 = winner_hero, Player2 = loser_hero
                    game.player1_faction = winner_hero_model['faction']
                    game.player1_hero = winner_hero_model['hero']
                    game.player2_faction = loser_hero_model['faction']
                    game.player2_hero = loser_hero_model['hero']
                elif game.winner_id == game.player2_id:
                    # Player2 a gagné → Player2 = winner_hero, Player1 = loser_hero
                    game.player1_faction = loser_hero_model['faction']
                    game.player1_hero = loser_hero_model['hero']
                    game.player2_faction = winner_hero_model['faction']
                    game.player2_hero = winner_hero_model['hero']

            player = stats.get('player', {})
            if player and (game.player1_faction is None or game.player2_faction is None or 
                          game.player1_reflexion_time is None or game.player2_reflexion_time is None or 
                          game.player1_nb_turns is None or game.player2_nb_turns is None):
                p1_bga_id_str = str(game.player1.bga_id)
                p2_bga_id_str = str(game.player2.bga_id)
                
                # Récupérer les valuelabels des factions
                faction_labels = player.get('faction', {}).get('valuelabels', {})
                if p1_bga_id_str in faction_labels:
                    faction_label_p1 = faction_labels[p1_bga_id_str]
                    game.player1_faction = get_faction_code_by_label(faction_label_p1)
                if p2_bga_id_str in faction_labels:
                    faction_label_p2 = faction_labels[p2_bga_id_str]
                    game.player2_faction = get_faction_code_by_label(faction_label_p2)

                # Récupérer les valuelabels des temps de réflexion
                reflection_time_values = player.get('reflexion_time', {}).get('values', {})
                if p1_bga_id_str in reflection_time_values:
                    game.player1_reflexion_time = reflection_time_values[p1_bga_id_str]
                if p2_bga_id_str in reflection_time_values:
                    game.player2_reflexion_time = reflection_time_values[p2_bga_id_str]

                # Récupérer les valuelabels des temps de réflexion
                turns_values = player.get('turns', {}).get('values', {})
                if p1_bga_id_str in turns_values:
                    game.player1_nb_turns = turns_values[p1_bga_id_str]
                if p2_bga_id_str in turns_values:
                    game.player2_nb_turns = turns_values[p2_bga_id_str]

        update_game_data(game)

        return {
            'status': 1,
            'table': game.json()
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
    
def import_deck_service(table_id: int) -> dict:
    """
    Importe les decks d'une partie BGA et les parse avec le système de normalisation
    """
    try:
        game = get_game_by_table_id_data(table_id)
        if not game:
            return {
                'status': 0,
                'error': f'Game not found for table ID: {table_id}',
                'table_id': table_id
            }

        # 1. Récupérer les données de la table depuis l'API BGA
        result = getGamerView(table_id)
        if result.get('status', 0) != 1:
            return {
                'status': 0,
                'error': f"Err : {result.get('error', 'err API')}",
                'table_id': table_id
            }
        
        data = result.get('data', {})
        logs = data.get('logs', [])
        if not logs or len(logs) == 0:
            return {
                'status': 0,
                'error': f'No logs found for table ID: {table_id}',
                'table_id': table_id
            }
        
        # 2. Extraire les données de sélection de decks
        decks_selections = []
        
        for log in logs:
            log_data = log.get('data', [])[0]
            if log_data.get('type', '') == 'updateInitialPrecoDeckSelection':
                private_data = log_data.get('args', {}).get('args', {}).get('_private')
                if private_data:
                    player_id_from_channel = int(log.get('channel', '').replace('/player/p', ''))
                    private_data['player_id'] = player_id_from_channel
                    
                    # Ne garder que les decks API (pas les decks RANDOM)
                    if private_data.get('selection', '') == 'API':
                        private_data.pop('decks', None)  # Supprimer les decks non-API
                        decks_selections.append(private_data)
                    
                    if len(decks_selections) == 2:
                        break
        
        # 3. ✅ PARSER ET STOCKER LES DECKS avec le nouveau système
        from app.services.deck_service import DeckService
        
        parsed_decks = []
        game_updated = False
        
        for deck_selection in decks_selections:
            bga_player_id = deck_selection.get('player_id')
            
            # Trouver le joueur correspondant
            player = get_player_by_bga_id_data(bga_player_id)
            if not player:
                print(f"⚠️  Joueur BGA #{bga_player_id} non trouvé en base")
                continue
            
            # Parser le deck avec le nouveau service
            deck = DeckService.parse_bga_deck(deck_selection, player.id)
            
            if deck:
                parsed_decks.append({
                    'player_id': str(player.id),
                    'player_bga_id': bga_player_id,
                    'deck_id': str(deck.id),
                    'deck_name': deck.deck_name,
                    'faction': deck.faction,
                    'hero': deck.hero,
                    'unique_count': deck.unique_count
                })
                
                # ✅ Associer le deck à la game ET mettre à jour faction/hero
                if game.player1.bga_id == bga_player_id:
                    game.player1_deck_id = deck.id
                    # ✅ Mettre à jour faction et hero depuis le deck si non définis
                    if not game.player1_faction:
                        game.player1_faction = deck.faction
                        game_updated = True
                    if not game.player1_hero:
                        game.player1_hero = deck.hero
                        game_updated = True
                    print(f"✅ Deck player1 associé - Faction: {deck.faction}, Hero: {deck.hero}")
                    
                elif game.player2.bga_id == bga_player_id:
                    game.player2_deck_id = deck.id
                    # ✅ Mettre à jour faction et hero depuis le deck si non définis
                    if not game.player2_faction:
                        game.player2_faction = deck.faction
                        game_updated = True
                    if not game.player2_hero:
                        game.player2_hero = deck.hero
                        game_updated = True
                    print(f"✅ Deck player2 associé - Faction: {deck.faction}, Hero: {deck.hero}")
        
        # 4. Sauvegarder les liens game<->deck et les mises à jour de faction/hero
        if game.player1_deck_id or game.player2_deck_id or game_updated:
            update_game_data(game)
            if game_updated:
                print(f"✅ Game #{table_id} mise à jour avec faction/hero depuis les decks")
        
        return {
            'status': 1,
            'table_id': table_id,
            'decks': parsed_decks,
            'game_updated': game_updated
        }
        
    except Exception as e:
        print(f"\033[91m❌ Erreur critique lors de l'import des decks: {e}\033[0m")
        import traceback
        traceback.print_exc()
        return {
            'status': 0,
            'error': str(e),
            'table_id': table_id
        }

    
def get_faction_code_by_label(label: str) -> dict:
    match label.lower():
        case 'yzmir':
            return 'YZ'
        case 'ordis':
            return 'OR'
        case 'muna':
            return 'MU'
        case 'lyra':
            return 'LY'
        case 'bravos':
            return 'BR'
        case 'axiom':
            return 'AX'
        case _:
            return None
    
def get_faction_hero_by_reference(reference: str) -> dict:
    model = {
        'hero': None,
        'hero_full': None,
        'faction': None
    }
    match reference:
        case ref if ref.endswith('YZ_01_C'):
            model['hero'] = 'Akesha'
            model['hero_full'] = 'Akesha & Taru'
            model['faction'] = 'YZ'
        case ref if ref.endswith('YZ_02_C'):
            model['hero'] = 'Lindiwe'
            model['hero_full'] = 'Lindiwe & Maw'
            model['faction'] = 'YZ'
        case ref if ref.endswith('YZ_03_C'):
            model['hero'] = 'Afanas'
            model['hero_full'] = 'Afanas & Senka'
            model['faction'] = 'YZ'
        case ref if ref.endswith('YZ_65_C'):
            model['hero'] = 'Moyo'
            model['hero_full'] = 'Moyo & Silk'
            model['faction'] = 'YZ'

        case ref if ref.endswith('OR_01_C'):
            model['hero'] = 'Sigismar'
            model['hero_full'] = 'Sigismar & Wingspan'
            model['faction'] = 'OR'
        case ref if ref.endswith('OR_02_C'):
            model['hero'] = 'Waru'
            model['hero_full'] = 'Waru & Mack'
            model['faction'] = 'OR'
        case ref if ref.endswith('OR_03_C'):
            model['hero'] = 'Gulrang'
            model['hero_full'] = 'Gulrang & Tocsin'
            model['faction'] = 'OR'
        case ref if ref.endswith('OR_65_C'):
            model['hero'] = 'Zhen'
            model['hero_full'] = 'Zhen & Zéphyr'
            model['faction'] = 'OR'
        case ref if ref.endswith('OR_85_C'):
            model['hero'] = 'Matz'
            model['hero_full'] = 'Matz & Hive'
            model['faction'] = 'OR'

        case ref if ref.endswith('MU_01_C'):
            model['hero'] = 'Teija'
            model['hero_full'] = 'Teija & Nauraa'
            model['faction'] = 'MU'
        case ref if ref.endswith('MU_02_C'):
            model['hero'] = 'Arjun'
            model['hero_full'] = 'Arjun & Spike'
            model['faction'] = 'MU'
        case ref if ref.endswith('MU_03_C'):
            model['hero'] = 'Rin'
            model['hero_full'] = 'Rin & Orchid'
            model['faction'] = 'MU'
        case ref if ref.endswith('MU_65_C'):
            model['hero'] = 'Kauri'
            model['hero_full'] = 'Kauri & Puff'
            model['faction'] = 'MU'
        case ref if ref.endswith('MU_85_C'):
            model['hero'] = 'Turuun'
            model['hero_full'] = 'Turuun & Benih'
            model['faction'] = 'MU'

        case ref if ref.endswith('LY_01_C'):
            model['hero'] = 'Nevenka'
            model['hero_full'] = 'Nevenka & Blotch'
            model['faction'] = 'LY'
        case ref if ref.endswith('LY_02_C'):
            model['hero'] = 'Auraq'
            model['hero_full'] = 'Auraq & Kibble'
            model['faction'] = 'LY'
        case ref if ref.endswith('LY_03_C'):
            model['hero'] = 'Fen'
            model['hero_full'] = 'Fen & Crowbar'
            model['faction'] = 'LY'
        case ref if ref.endswith('LY_65_C'):
            model['hero'] = 'Nadir'
            model['hero_full'] = 'Nadir & Bubbles'
            model['faction'] = 'LY'

        case ref if ref.endswith('BR_01_C'):
            model['hero'] = 'Kojo'
            model['hero_full'] = 'Kojo & Booda'
            model['faction'] = 'BR'
        case ref if ref.endswith('BR_02_C'):
            model['hero'] = 'Atsadi'
            model['hero_full'] = 'Atsadi & Surge'
            model['faction'] = 'BR'
        case ref if ref.endswith('BR_03_C'):
            model['hero'] = 'Basira'
            model['hero_full'] = 'Basira & Kaizaimon'
            model['faction'] = 'BR'
        case ref if ref.endswith('BR_65_C'):
            model['hero'] = 'Sol'
            model['hero_full'] = 'Sol & Halua'
            model['faction'] = 'BR'

        case ref if ref.endswith('AX_01_C'):
            model['hero'] = 'Sierra'
            model['hero_full'] = 'Sierra & Oddball'
            model['faction'] = 'AX'
        case ref if ref.endswith('AX_02_C'):
            model['hero'] = 'Treyst'
            model['hero_full'] = 'Treyst & Rossum'
            model['faction'] = 'AX'
        case ref if ref.endswith('AX_03_C'):
            model['hero'] = 'Subhash'
            model['hero_full'] = 'Subhash & Marmo'
            model['faction'] = 'AX'
        case ref if ref.endswith('AX_65_C'):
            model['hero'] = 'Isaree'
            model['hero_full'] = 'Isaree & Pebble'
            model['faction'] = 'AX'
        case ref if ref.endswith('AX_85_C'):
            model['hero'] = 'Della'
            model['hero_full'] = 'Della & Bolt'
            model['faction'] = 'AX'
    return model

def get_faction_hero_by_label(label: str) -> dict:
    model = {
        'hero': None,
        'hero_full': None,
        'faction': None
    }
    
    if not label:
        return model
    
    # Normaliser le label (lowercase + strip)
    search_label = label.lower().strip()
    
    # Yzyraté (YZ)
    if 'akesha' in search_label or 'taru' in search_label:
        model['hero'] = 'Akesha'
        model['hero_full'] = 'Akesha & Taru'
        model['faction'] = 'YZ'
    elif 'lindiwe' in search_label or 'maw' in search_label:
        model['hero'] = 'Lindiwe'
        model['hero_full'] = 'Lindiwe & Maw'
        model['faction'] = 'YZ'
    elif 'afanas' in search_label or 'senka' in search_label:
        model['hero'] = 'Afanas'
        model['hero_full'] = 'Afanas & Senka'
        model['faction'] = 'YZ'
    elif 'moyo' in search_label or 'silk' in search_label:
        model['hero'] = 'Moyo'
        model['hero_full'] = 'Moyo & Silk'
        model['faction'] = 'YZ'
    
    # Ordis (OR)
    elif 'sigismar' in search_label or 'wingspan' in search_label:
        model['hero'] = 'Sigismar'
        model['hero_full'] = 'Sigismar & Wingspan'
        model['faction'] = 'OR'
    elif 'waru' in search_label or 'mack' in search_label:
        model['hero'] = 'Waru'
        model['hero_full'] = 'Waru & Mack'
        model['faction'] = 'OR'
    elif 'gulrang' in search_label or 'tocsin' in search_label:
        model['hero'] = 'Gulrang'
        model['hero_full'] = 'Gulrang & Tocsin'
        model['faction'] = 'OR'
    elif 'zhen' in search_label or 'zéphyr' in search_label or 'zephyr' in search_label:
        model['hero'] = 'Zhen'
        model['hero_full'] = 'Zhen & Zéphyr'
        model['faction'] = 'OR'
    elif 'matz' in search_label or 'hive' in search_label:
        model['hero'] = 'Matz'
        model['hero_full'] = 'Matz & Hive'
        model['faction'] = 'OR'
    
    # Muna (MU)
    elif 'teija' in search_label or 'nauraa' in search_label:
        model['hero'] = 'Teija'
        model['hero_full'] = 'Teija & Nauraa'
        model['faction'] = 'MU'
    elif 'arjun' in search_label or 'spike' in search_label:
        model['hero'] = 'Arjun'
        model['hero_full'] = 'Arjun & Spike'
        model['faction'] = 'MU'
    elif 'rin' in search_label or 'orchid' in search_label:
        model['hero'] = 'Rin'
        model['hero_full'] = 'Rin & Orchid'
        model['faction'] = 'MU'
    elif 'kauri' in search_label or 'puff' in search_label:
        model['hero'] = 'Kauri'
        model['hero_full'] = 'Kauri & Puff'
        model['faction'] = 'MU'
    elif 'turuun' in search_label or 'benih' in search_label:
        model['hero'] = 'Turuun'
        model['hero_full'] = 'Turuun & Benih'
        model['faction'] = 'MU'
    
    # Lyra (LY)
    elif 'nevenka' in search_label or 'blotch' in search_label:
        model['hero'] = 'Nevenka'
        model['hero_full'] = 'Nevenka & Blotch'
        model['faction'] = 'LY'
    elif 'auraq' in search_label or 'kibble' in search_label:
        model['hero'] = 'Auraq'
        model['hero_full'] = 'Auraq & Kibble'
        model['faction'] = 'LY'
    elif 'fen' in search_label or 'crowbar' in search_label:
        model['hero'] = 'Fen'
        model['hero_full'] = 'Fen & Crowbar'
        model['faction'] = 'LY'
    elif 'nadir' in search_label or 'bubbles' in search_label:
        model['hero'] = 'Nadir'
        model['hero_full'] = 'Nadir & Bubbles'
        model['faction'] = 'LY'
    
    # Bravos (BR)
    elif 'kojo' in search_label or 'booda' in search_label:
        model['hero'] = 'Kojo'
        model['hero_full'] = 'Kojo & Booda'
        model['faction'] = 'BR'
    elif 'atsadi' in search_label or 'surge' in search_label:
        model['hero'] = 'Atsadi'
        model['hero_full'] = 'Atsadi & Surge'
        model['faction'] = 'BR'
    elif 'basira' in search_label or 'kaizaimon' in search_label:
        model['hero'] = 'Basira'
        model['hero_full'] = 'Basira & Kaizaimon'
        model['faction'] = 'BR'
    elif 'sol' in search_label or 'halua' in search_label:
        model['hero'] = 'Sol'
        model['hero_full'] = 'Sol & Halua'
        model['faction'] = 'BR'
    
    # Axiom (AX)
    elif 'sierra' in search_label or 'oddball' in search_label:
        model['hero'] = 'Sierra'
        model['hero_full'] = 'Sierra & Oddball'
        model['faction'] = 'AX'
    elif 'treyst' in search_label or 'rossum' in search_label:
        model['hero'] = 'Treyst'
        model['hero_full'] = 'Treyst & Rossum'
        model['faction'] = 'AX'
    elif 'subhash' in search_label or 'marmo' in search_label:
        model['hero'] = 'Subhash'
        model['hero_full'] = 'Subhash & Marmo'
        model['faction'] = 'AX'
    elif 'isaree' in search_label or 'pebble' in search_label:
        model['hero'] = 'Isaree'
        model['hero_full'] = 'Isaree & Pebble'
        model['faction'] = 'AX'
    elif 'della' in search_label or 'bolt' in search_label:
        model['hero'] = 'Della'
        model['hero_full'] = 'Della & Bolt'
        model['faction'] = 'AX'
    return model

def calculate_enriched_season_stats(player_id: uuid.UUID, season: int, games: List[Game]) -> dict:
    # Filtrer les parties de la saison (games déjà fourni)
    season_games = [g for g in games if g.season == season]
    
    if not season_games:
        return {}
    
    # ✅ Variables d'accumulation (1 seul pass sur les données)
    wins = 0
    losses = 0
    draws = 0
    
    faction_stats = {}  # {'AX': {'wins': 0, 'losses': 0, 'draws': 0, 'games': 0}}
    hero_stats = {}     # {'Sigismar & Wingspan': {'wins': 0, 'losses': 0, 'draws': 0}}
    
    total_reflexion_time = 0
    total_turns = 0  # ✅ Nombre total de tours
    
    fastest_game = None
    slowest_game = None
    
    current_streak = 0
    best_win_streak = 0
    worst_loss_streak = 0
    temp_win_streak = 0
    temp_loss_streak = 0
    
    # ✅ SINGLE PASS : Parcourir les parties UNE SEULE FOIS
    for game in sorted(season_games, key=lambda x: x.played_at):
        # Déterminer faction et héros du joueur
        is_player1 = game.player1_id == player_id
        player_faction = game.player1_faction if is_player1 else game.player2_faction
        player_hero = game.player1_hero if is_player1 else game.player2_hero
        player_reflexion = game.player1_reflexion_time if is_player1 else game.player2_reflexion_time
        player_turns = game.player1_nb_turns if is_player1 else game.player2_nb_turns
        
        # Résultat
        is_win = game.winner_id == player_id
        is_draw = game.is_draw
        is_loss = not is_win and not is_draw
        
        # Stats globales
        if is_win:
            wins += 1
            temp_win_streak += 1
            temp_loss_streak = 0
            best_win_streak = max(best_win_streak, temp_win_streak)
        elif is_loss:
            losses += 1
            temp_loss_streak += 1
            temp_win_streak = 0
            worst_loss_streak = max(worst_loss_streak, temp_loss_streak)
        else:
            draws += 1
            temp_win_streak = 0
            temp_loss_streak = 0
        
        # Streak actuel (dernière partie)
        current_streak = temp_win_streak if temp_win_streak > 0 else -temp_loss_streak
        
        # Stats par faction
        if player_faction:
            if player_faction not in faction_stats:
                faction_stats[player_faction] = {'wins': 0, 'losses': 0, 'draws': 0, 'games': 0}
            
            faction_stats[player_faction]['games'] += 1
            if is_win:
                faction_stats[player_faction]['wins'] += 1
            elif is_loss:
                faction_stats[player_faction]['losses'] += 1
            else:
                faction_stats[player_faction]['draws'] += 1
        
        # Stats par héros
        if player_hero:
            if player_hero not in hero_stats:
                hero_stats[player_hero] = {'wins': 0, 'losses': 0, 'draws': 0, 'games': 0}
            
            hero_stats[player_hero]['games'] += 1
            if is_win:
                hero_stats[player_hero]['wins'] += 1
            elif is_loss:
                hero_stats[player_hero]['losses'] += 1
            else:
                hero_stats[player_hero]['draws'] += 1
        
        # ✅ Accumuler temps BRUT + tours (pas de calcul de moyenne ici)
        if player_reflexion and player_reflexion > 0 and player_turns and player_turns > 0:
            total_reflexion_time += player_reflexion
            total_turns += player_turns
        
        # Durée de partie
        if game.duration_minutes:
            if fastest_game is None or game.duration_minutes < fastest_game:
                fastest_game = game.duration_minutes
            if slowest_game is None or game.duration_minutes > slowest_game:
                slowest_game = game.duration_minutes
    
    # ✅ Calcul du win_rate global
    total_games = wins + losses + draws
    win_rate = (wins / total_games * 100) if total_games > 0 else 0.0
    
    # ✅ Faction/Héros le plus joué
    most_played_faction = max(faction_stats.items(), key=lambda x: x[1]['games'])[0] if faction_stats else None
    most_played_hero = max(hero_stats.items(), key=lambda x: x[1]['games'])[0] if hero_stats else None
    
    # ✅ Calculer win_rate par faction
    for faction, stats in faction_stats.items():
        games_count = stats['games']
        stats['win_rate'] = (stats['wins'] / games_count * 100) if games_count > 0 else 0.0
    
    # ✅ Calculer win_rate par héros
    for hero, stats in hero_stats.items():
        games_count = stats['games']
        stats['win_rate'] = (stats['wins'] / games_count * 100) if games_count > 0 else 0.0
    
    return {
        'wins': wins,
        'losses': losses,
        'draws': draws,
        'win_rate': round(win_rate, 2),
        'most_played_faction': most_played_faction,
        'most_played_hero': most_played_hero,
        'faction_stats': faction_stats,
        'hero_stats': hero_stats,
        'total_reflexion_time': total_reflexion_time,  # ✅ Temps BRUT total
        'total_turns': total_turns,  # ✅ Nombre total de tours
        'fastest_game_minutes': fastest_game,
        'slowest_game_minutes': slowest_game,
        'current_streak': current_streak,
        'best_win_streak': best_win_streak,
        'worst_loss_streak': worst_loss_streak,
    }