from app.models.user_alert import UserAlert
from app.extensions import db
from app import create_app

def limit_user_alerts():
    # Récupère tous les id_user ayant plus de 10 alertes actives
    subquery = (
        db.session.query(
            UserAlert.id_user
        )
        .filter(UserAlert.mail_active == True)
        .group_by(UserAlert.id_user)
        .having(db.func.count(UserAlert.id) > 10)
        .subquery()
    )

    # Pour chaque utilisateur concerné
    users = db.session.query(subquery.c.id_user).all()
    for (id_user,) in users:
        # Récupère toutes ses alertes actives, triées par date (les plus anciennes d'abord)
        alerts = (
            UserAlert.query
            .filter_by(id_user=id_user, mail_active=True)
            .order_by(UserAlert.created_at.asc())
            .all()
        )
        # Désactive les alertes excédentaires
        for alert in alerts[10:]:
            alert.mail_active = False
        db.session.commit()
        print(f"Limité à 10 alertes actives pour l'utilisateur {id_user}")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        limit_user_alerts()