from app import create_app
from app.extensions import db
from app.models.user_alert import UserAlert
from sqlalchemy import func

app = create_app()

with app.app_context():
    # Trouver les doublons
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

    for id_user, reference_card, nb in duplicates:
        # Récupère tous les doublons, triés du plus récent au plus ancien
        alerts = (
            UserAlert.query
            .filter_by(id_user=id_user, reference_card=reference_card)
            .order_by(UserAlert.created_at.desc())
            .all()
        )
        # On garde le plus récent, on supprime les autres
        for alert in alerts[1:]:
            db.session.delete(alert)
            total_deleted += 1

    db.session.commit()
    print(f"Suppression terminée. {total_deleted} doublon(s) supprimé(s).")