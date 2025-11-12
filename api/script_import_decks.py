"""
Script pour importer les decks de toutes les parties existantes en base de données
Utilise le système de normalisation de decks pour créer les archétypes et stocker les decks

Usage:
    python script_import_decks.py --season 2
    python script_import_decks.py --limit 100
    python script_import_decks.py --all
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.game import Game
from app.services.player_service import import_deck_service
import argparse
import time

app = create_app()

def import_decks_for_season(season: int = None, limit: int = None, dry_run: bool = False):
    """
    Importe les decks pour toutes les parties d'une saison
    """
    with app.app_context():
        print(f"\n{'='*80}")
        print(f"🎯 IMPORT DES DECKS")
        if season:
            print(f"📅 Saison: {season}")
        if limit:
            print(f"📊 Limite: {limit} parties")
        print(f"{'='*80}\n")
        
        # Construire la requête
        query = Game.query.filter(
            Game.player1_deck_id.is_(None),  # Parties sans deck importé
            Game.ranked == True  # Uniquement les parties ranked
        )
        
        if season:
            query = query.filter_by(season=season)
        
        # Trier par date décroissante (parties les plus récentes d'abord)
        query = query.order_by(Game.played_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        games = query.all()
        total_games = len(games)
        
        if total_games == 0:
            print("ℹ️  Aucune partie à traiter")
            return
        
        print(f"🎮 {total_games} partie(s) à traiter\n")
        
        if dry_run:
            print("🔍 MODE DRY-RUN : Aucune modification ne sera effectuée\n")
        
        # Statistiques
        stats = {
            'success': 0,
            'skipped': 0,
            'errors': 0,
            'decks_created': 0
        }
        
        # Traiter chaque partie
        for idx, game in enumerate(games, 1):
            try:
                print(f"[{idx}/{total_games}] Partie #{game.table_id} ({game.player1.name} vs {game.player2.name})")
                
                if dry_run:
                    print(f"  🔍 [DRY-RUN] Serait traité")
                    stats['success'] += 1
                    continue
                
                # Importer les decks
                result = import_deck_service(game.table_id)
                
                if result.get('status') == 1:
                    decks_imported = len(result.get('decks', []))
                    stats['decks_created'] += decks_imported
                    stats['success'] += 1
                    print(f"  ✅ {decks_imported} deck(s) importé(s)")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    
                    # Distinguer les erreurs réelles des parties sans decks
                    if 'No logs found' in error_msg or 'No deck' in error_msg:
                        stats['skipped'] += 1
                        print(f"  ⏭️  Ignoré: {error_msg}")
                    else:
                        stats['errors'] += 1
                        print(f"  ❌ Erreur: {error_msg}")
                
                # Pause pour éviter de surcharger l'API BGA
                if idx < total_games:
                    time.sleep(0.5)
                
            except Exception as e:
                stats['errors'] += 1
                print(f"  ❌ Exception: {e}")
                continue
        
        # Affichage final
        print("\n" + "="*80)
        print("📊 RÉSUMÉ DE L'IMPORT")
        print("="*80)
        print(f"✅ Succès: {stats['success']}")
        print(f"🎴 Decks créés: {stats['decks_created']}")
        print(f"⏭️  Ignorés: {stats['skipped']}")
        print(f"❌ Erreurs: {stats['errors']}")
        print(f"📈 Total: {total_games}")
        print("="*80 + "\n")


def import_all_decks(batch_size: int = 50):
    """
    Importe tous les decks manquants par batch
    """
    with app.app_context():
        print(f"\n{'='*80}")
        print(f"🎯 IMPORT COMPLET DES DECKS (batch de {batch_size})")
        print(f"{'='*80}\n")
        
        # Compter le total
        total_without_decks = Game.query.filter(
            Game.player1_deck_id.is_(None),
            Game.ranked == True
        ).count()
        
        print(f"🎮 {total_without_decks} partie(s) sans deck en base\n")
        
        processed = 0
        
        while processed < total_without_decks:
            print(f"\n📦 Batch {processed // batch_size + 1} ({processed}/{total_without_decks})")
            import_decks_for_season(limit=batch_size)
            processed += batch_size
            
            # Pause entre les batchs
            if processed < total_without_decks:
                print(f"\n⏸️  Pause de 5 secondes...")
                time.sleep(5)
        
        print(f"\n✅ Import complet terminé !")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import des decks depuis BGA')
    parser.add_argument('--season', type=int, help='Numéro de la saison à importer')
    parser.add_argument('--limit', type=int, help='Limite de parties à traiter')
    parser.add_argument('--all', action='store_true', help='Importer tous les decks manquants')
    parser.add_argument('--dry-run', action='store_true', help='Mode test sans modifications')
    parser.add_argument('--batch-size', type=int, default=50, help='Taille des batchs pour --all')
    
    args = parser.parse_args()
    
    if args.all:
        import_all_decks(batch_size=args.batch_size)
    else:
        import_decks_for_season(
            season=args.season,
            limit=args.limit,
            dry_run=args.dry_run
        )
