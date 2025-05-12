from app.models.card import Card
from app.extensions import db
from app import create_app

def initialize_incremental_id():
    with db.session.begin():
        # Récupérer toutes les cartes triées par leur clé primaire
        cards = db.session.query(Card).order_by(Card.id).all()
        
        # Initialiser l'incremental_id
        for index, card in enumerate(cards, start=1):
            card.incremental_id = index
        
        # Commit des modifications
        db.session.commit()

    print("Initialisation de incremental_id terminée.")

app = create_app()


with app.app_context():
    # Appeler la fonction pour initialiser incremental_id
    initialize_incremental_id()