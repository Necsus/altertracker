# import pandas as pd
import re
from app.models.card import Card
from app.extensions import db
from app import create_app

# Charger ton fichier CSV
# file_path = 'data-1750015266682.csv'  # Mets ici ton chemin exact
# df = pd.read_csv(file_path)

# On ne garde que la colonne des effets
app = create_app()
with app.app_context():
    cards = db.session.query(
            Card.reference,
            Card.name_en,
            Card.MAIN_EFFECT
        ).filter(Card.MAIN_EFFECT.isnot(None)).limit(100).all()
    
    # Les regex pour identifier les patterns
    pattern_curly = re.compile(r"^\{([^}]+)\}\s*(.*?):\s*(.*)$")
    pattern_dash = re.compile(r"^(.*?—)\s*(.*)")

    # Séparateur d'effets multiples (les points)
    split_regex = re.compile(r'\  \s*')

    parsed_results = []

    for card in cards:
        print(f"\033[94mTraitement de la carte : {card[1]} ({card[0]})\033[0m")
        full_effect = card[2].strip('.')
        sub_effects = split_regex.split(full_effect)

        for effet in sub_effects:
            effet = effet.strip()
            if not effet:
                continue
            print(f"\033[92mEffet à parser : {effet}\033[0m")
            declencheur, condition, effet_value = '[]', '[]', '[]'

            # 1. Cherche déclencheur type {}
            match = pattern_curly.match(effet)
            if match:
                declencheur = f"{{{match.group(1)}}}"
                reste = match.group(2).strip() + ": " + match.group(3).strip()
            else:
                # 2. Cherche déclencheur type texte suivi de —
                match = pattern_dash.match(effet)
                if match:
                    declencheur = match.group(1).strip()
                    reste = match.group(2).strip()
                else:
                    # Aucun déclencheur détecté
                    reste = effet

            reste = reste.strip()

            # 3. Vérifie si le reste commence par []
            if reste.startswith('[]'):
                condition = '[]'
                effet_value = reste[2:].strip()
            else:
                # 4. Cherche un ':' pour séparer condition et effet
                if ':' in reste:
                    parts = reste.split(':', 1)
                    condition = parts[0].strip() + " :"
                    effet_value = parts[1].strip()
                else:
                    effet_value = reste
            print(f'déclencheur = {declencheur}')
            print(f'condition = {condition}')
            print(f'effet = {effet_value}')
            parsed_results.append({
                'declencheur': declencheur,
                'condition': condition,
                'effet': effet_value
            })

    # Convertir en dataframe pour visualiser le résultat
    # parsed_df = pd.DataFrame(parsed_results)

    # # Sauvegarde des résultats en CSV pour inspection
    # parsed_df.to_csv("parsed_output.csv", index=False)

    print("Parsing terminé. Résultat sauvegardé dans 'parsed_output.csv'")