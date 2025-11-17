from app import create_app
from app.extensions import db
from app.models.user_alert import UserAlert
from sqlalchemy import func

app = create_app()

with app.app_context():
    print("🔍 Recherche des doublons d'alertes...")
    
    # ✅ CORRECTION : Trouver les doublons (id_user, reference_card) - id_search peut être NULL
    duplicates = (
        db.session.query(
            UserAlert.id_user,
            UserAlert.reference_card,
            func.count(UserAlert.id).label('nb')
        )
        .group_by(UserAlert.id_user, UserAlert.reference_card)
        .having(func.count(UserAlert.id) > 1)
        .all()
    )

    total_deleted = 0
    total_groups = len(duplicates)

    if total_groups == 0:
        print("✅ Aucun doublon trouvé !")
    else:
        print(f"⚠️  {total_groups} groupe(s) de doublons trouvé(s)")

    for id_user, reference_card, nb in duplicates:
        print(f"  • User {id_user}, Card {reference_card}: {nb} exemplaires")
        
        # Récupère tous les doublons, triés du plus récent au plus ancien
        alerts = (
            UserAlert.query
            .filter_by(id_user=id_user, reference_card=reference_card)
            .order_by(UserAlert.created_at.desc())
            .all()
        )
        
        # On garde le plus récent, on supprime les autres
        for alert in alerts[1:]:
            print(f"    🗑️  Suppression de l'alerte #{alert.id} (créée le {alert.created_at})")
            db.session.delete(alert)
            total_deleted += 1

    if total_deleted > 0:
        db.session.commit()
        print(f"\n✅ Nettoyage terminé. {total_deleted} doublon(s) supprimé(s).")
    else:
        print("\n✅ Rien à nettoyer !")