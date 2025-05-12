from datetime import datetime
import time
from app import create_app
from app.scripts import auth, card_routine
from app.models.card import Card
from app.extensions import db

# Créer l'application Flask
app = create_app()

# Démarrer le timer
start_time = time.time()

with app.app_context():  # Activer le contexte de l'application
    token = auth.get_token()

    nb_cards = 0

    print(f"----------- GET OFFRES -----------")