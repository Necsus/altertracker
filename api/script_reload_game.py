"""
Script de mise à niveau des données de parties (games).
Recharge les informations complètes depuis l'API BGA pour toutes les parties en base.
"""

import sys
import os

# Ajouter le chemin parent pour importer l'app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.game import Game
from app.services.player_service import import_table_service
from app.data.player_data import get_game_by_table_id_data
from app.scripts.bga_routine import getTableInfos
from app.services.player_service import get_faction_hero_by_label, get_faction_code_by_label, get_or_create_tournament_data
import time

def _safe_float_cast(value) -> float | None:
    """Convertit une valeur en float de manière sécurisée."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def reload_game_fast(game: Game) -> dict:
    """
    Version rapide de import_table_service SANS commit automatique.
    Le commit sera fait en batch par le script principal.
    """
    try:
        ti = getTableInfos(game.table_id)
        if ti.get('status', 0) != 1:
            return {
                'status': 0,
                'error': f"Err : {ti.get('error', 'err API')}",
                'table_id': game.table_id
            }

        table_data = ti.get('data', {})
        if not table_data:
            return {
                'status': 0,
                'error': f"No data for table ID: {game.table_id}",
                'table_id': game.table_id
            }

        result = table_data.get('result', {})
        if not result:
            return {
                'status': 0,
                'error': f"No result found for table ID: {game.table_id}",
                'table_id': game.table_id
            }
        
        # Options (ranked)
        options = table_data.get('options', {})
        if options:
            opt201 = options.get('201', {})
            if opt201:
                value = opt201.get('value', None)
                game.ranked = (value == '2') if value is not None else None

        # Arena points
        if result and game.ranked:
            players = result.get('player', [])
            for player_data in players:
                if str(player_data.get('player_id', '')) == str(game.player1.bga_id):
                    game.player1_arena_point_win = _safe_float_cast(player_data.get('arena_points_win'))
                    game.player1_arena_point_after_game = _safe_float_cast(player_data.get('arena_after_game'))
                elif str(player_data.get('player_id', '')) == str(game.player2.bga_id):
                    game.player2_arena_point_win = _safe_float_cast(player_data.get('arena_points_win'))
                    game.player2_arena_point_after_game = _safe_float_cast(player_data.get('arena_after_game'))

        # Tournament
        if table_data.get('has_tournament', '0') == '1':
            tournament = table_data.get('tournament', {})
            if tournament:
                tournament_bga_id = tournament.get('id')
                tournament_name = tournament.get('tournament_name')
                championship_name = tournament.get('championship_name')

                if tournament_bga_id and tournament_name:
                    try:
                        tournament_obj = get_or_create_tournament_data(
                            bga_id=tournament_bga_id,
                            tournament_name=tournament_name,
                            championship_name=championship_name
                        )
                        game.tournament_id = tournament_obj.id
                    except Exception as e:
                        pass  # Ignorer les erreurs de tournoi

        # Stats
        stats = result.get('stats', {})
        if not stats:
            return {
                'status': 0,
                'error': f"No stats found for table ID: {game.table_id}",
                'table_id': game.table_id
            }

        # Factions/Héros depuis table
        table = stats.get('table', {})
        if table:
            days_value = table.get('days', {}).get('value', 0)
            if days_value is not None:
                game.round = int(days_value)

            winner_hero_model = get_faction_hero_by_label(table.get('gameWinner', {}).get('valuelabel'))
            loser_hero_model = get_faction_hero_by_label(table.get('gameLooser', {}).get('valuelabel'))
            
            if game.winner_id == game.player1_id:
                game.player1_faction = winner_hero_model['faction']
                game.player1_hero = winner_hero_model['hero']
                game.player2_faction = loser_hero_model['faction']
                game.player2_hero = loser_hero_model['hero']
            elif game.winner_id == game.player2_id:
                game.player1_faction = loser_hero_model['faction']
                game.player1_hero = loser_hero_model['hero']
                game.player2_faction = winner_hero_model['faction']
                game.player2_hero = winner_hero_model['hero']

        # Stats player
        player = stats.get('player', {})
        if player:
            p1_bga_id_str = str(game.player1.bga_id)
            p2_bga_id_str = str(game.player2.bga_id)
            
            # Factions
            faction_labels = player.get('faction', {}).get('valuelabels', {})
            if p1_bga_id_str in faction_labels:
                game.player1_faction = get_faction_code_by_label(faction_labels[p1_bga_id_str])
            if p2_bga_id_str in faction_labels:
                game.player2_faction = get_faction_code_by_label(faction_labels[p2_bga_id_str])

            # Temps de réflexion
            reflection_time_values = player.get('reflexion_time', {}).get('values', {})
            if p1_bga_id_str in reflection_time_values:
                game.player1_reflexion_time = reflection_time_values[p1_bga_id_str]
            if p2_bga_id_str in reflection_time_values:
                game.player2_reflexion_time = reflection_time_values[p2_bga_id_str]

            # Nombre de tours
            turns_values = player.get('turns', {}).get('values', {})
            if p1_bga_id_str in turns_values:
                game.player1_nb_turns = turns_values[p1_bga_id_str]
            if p2_bga_id_str in turns_values:
                game.player2_nb_turns = turns_values[p2_bga_id_str]

        # ✅ PAS DE COMMIT ICI - Sera fait en batch
        return {
            'status': 1,
            'table_id': game.table_id
        }
        
    except Exception as e:
        return {
            'status': 0,
            'error': str(e),
            'table_id': game.table_id
        }

def reload_all_games(
    limit: int = None,
    start_table_id: int = None,
    filter_incomplete: bool = False,
    filter_no_tournament: bool = False,
    filter_no_ranked: bool = False,
    batch_size: int = 50  # ✅ Commit tous les X parties
):
    """
    Recharge les données de toutes les parties depuis l'API BGA.
    """
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("🔄 SCRIPT DE RECHARGEMENT DES PARTIES (MODE OPTIMISÉ)")
        print("="*80)
        
        # 1. Construire la requête
        query = Game.query.order_by(Game.table_id.asc())
        
        # Filtres optionnels
        if start_table_id:
            query = query.filter(Game.table_id >= start_table_id)
            print(f"🎯 Démarrage à partir du table_id: {start_table_id}")
        
        if filter_incomplete:
            query = query.filter(
                db.or_(
                    Game.player1_faction == None,
                    Game.player2_faction == None,
                    Game.player1_hero == None,
                    Game.player2_hero == None,
                    Game.player1_reflexion_time == None,
                    Game.player2_reflexion_time == None,
                    Game.player1_nb_turns == None,
                    Game.player2_nb_turns == None
                )
            )
            print("🔍 Filtre: Parties incomplètes uniquement")
        
        if filter_no_tournament:
            query = query.filter(Game.tournament_id == None)
            print("🔍 Filtre: Parties sans tournoi uniquement")
        
        if filter_no_ranked:
            query = query.filter(Game.ranked == None)
            print("🔍 Filtre: Parties sans statut ranked uniquement")
        
        if limit:
            query = query.limit(limit)
            print(f"📊 Limite: {limit} parties")
        
        # 2. Récupérer les parties
        games = query.all()
        total_games = len(games)
        
        if total_games == 0:
            print("\n⚠️  Aucune partie à traiter avec les filtres appliqués")
            return
        
        print(f"\n📊 Total de parties à traiter: {total_games}")
        print(f"🔄 Batch size (commit): {batch_size} parties")
        print(f"⏳ Temps estimé: ~{(total_games * 0.3 / 60):.1f} minutes")  # ~0.3s par partie
        print("="*80 + "\n")
        
        # 3. Confirmation
        response = input("⚠️  Voulez-vous continuer ? (y/n): ")
        if response.lower() != 'y':
            print("❌ Annulé par l'utilisateur")
            return
        
        # 4. Statistiques
        stats = {
            'success': 0,
            'errors': 0,
            'total': total_games
        }
        
        # 5. Traitement
        print("\n🔄 Début du traitement...\n")
        start_time = time.time()
        
        for idx, game in enumerate(games, 1):
            try:
                # Barre de progression
                progress = (idx / total_games) * 100
                elapsed = time.time() - start_time
                eta = (elapsed / idx) * (total_games - idx) if idx > 0 else 0
                
                print(f"[{idx}/{total_games}] ({progress:.1f}%) | ETA: {eta/60:.1f}min | Table #{game.table_id}...", end=" ", flush=True)
                
                # ✅ Appeler la version rapide (sans commit)
                result = reload_game_fast(game)
                
                if result.get('status') == 1:
                    print("✅")
                    stats['success'] += 1
                else:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"❌ {error_msg}")
                    stats['errors'] += 1
                
                # ✅ Commit par batch
                if idx % batch_size == 0:
                    db.session.commit()
                    print(f"💾 Commit batch #{idx // batch_size} ({batch_size} parties)")
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interruption par l'utilisateur")
                db.session.commit()  # Sauvegarder avant de quitter
                break
            except Exception as e:
                print(f"❌ ERREUR: {e}")
                stats['errors'] += 1
                continue
        
        # ✅ Commit final pour les parties restantes
        db.session.commit()
        print(f"💾 Commit final")
        
        # 6. Résumé final
        elapsed_total = time.time() - start_time
        
        print("\n" + "="*80)
        print("📊 RÉSUMÉ DU RECHARGEMENT")
        print("="*80)
        print(f"✅ Réussites: {stats['success']}")
        print(f"❌ Erreurs: {stats['errors']}")
        print(f"📊 Total traité: {stats['success'] + stats['errors']}/{stats['total']}")
        print(f"⏱️  Temps écoulé: {elapsed_total/60:.1f} minutes")
        print(f"⚡ Vitesse moyenne: {(stats['success'] + stats['errors'])/elapsed_total:.2f} parties/seconde")
        print("="*80 + "\n")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Recharge les données des parties depuis l\'API BGA')
    parser.add_argument('--limit', type=int, help='Nombre maximum de parties à traiter')
    parser.add_argument('--start', type=int, help='Reprendre à partir d\'un table_id spécifique')
    parser.add_argument('--incomplete', action='store_true', help='Ne traiter que les parties incomplètes')
    parser.add_argument('--no-tournament', action='store_true', help='Ne traiter que les parties sans tournoi')
    parser.add_argument('--no-ranked', action='store_true', help='Ne traiter que les parties sans statut ranked')
    parser.add_argument('--batch', type=int, default=50, help='Nombre de parties avant commit DB (défaut: 50)')
    
    args = parser.parse_args()
    
    # Exemples d'utilisation
    if len(sys.argv) == 1:
        print("\n📚 EXEMPLES D'UTILISATION:")
        print("="*80)
        print("\n1️⃣  Recharger TOUTES les parties (batch 100):")
        print("   python script_reload_game.py --batch 100")
        print("\n2️⃣  Recharger les 1000 premières parties:")
        print("   python script_reload_game.py --limit 1000 --batch 100")
        print("\n3️⃣  Recharger uniquement les parties sans ranked:")
        print("   python script_reload_game.py --no-ranked --batch 100")
        print("\n4️⃣  Reprendre à partir d'un table_id:")
        print("   python script_reload_game.py --start 123456789 --batch 100")
        print("\n" + "="*80)
        
        response = input("\nVoulez-vous lancer un rechargement complet maintenant ? (y/n): ")
        if response.lower() == 'y':
            reload_all_games()
    else:
        reload_all_games(
            limit=args.limit,
            start_table_id=args.start,
            filter_incomplete=args.incomplete,
            filter_no_tournament=args.no_tournament,
            filter_no_ranked=args.no_ranked,
            batch_size=args.batch
        )