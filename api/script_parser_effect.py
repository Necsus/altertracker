import re
from app.models.card import Card
from app.extensions import db
from app import create_app

app = create_app()

# Regex pour les différents patterns
pattern_curly_with_condition = re.compile(r"^\{([^}]+)\}\s*(.*?):\s*(.*)$")
pattern_curly_without_condition = re.compile(r"^\{([^}]+)\}\s*(.*)$")
pattern_dash = re.compile(r"^(.*?—)\s*(.*)")
pattern_empty_condition = re.compile(r'^\[\]\s*(.*)$')

# Séparateur d'effets multiples (tu m’as confirmé qu’il est correct)
split_regex = re.compile(r'\  \s*')  # ton split sur espace insécable confirmé

parsed_results = []

with app.app_context():
    cards = db.session.query(
            Card.reference,
            Card.name_en,
            Card.MAIN_EFFECT
        ).filter(
            Card.MAIN_EFFECT.isnot(None),
            Card.name == "Dédale"
        ).limit(100).all()

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

            # D'abord on teste le pattern {déclencheur} avec condition
            match = pattern_curly_with_condition.match(effet)
            if match:
                declencheur = f"{{{match.group(1)}}}"
                condition = match.group(2).strip() + " :"
                effet_value = match.group(3).strip()
            else:
                # Sinon, pattern {déclencheur} sans condition
                match = pattern_curly_without_condition.match(effet)
                if match:
                    declencheur = f"{{{match.group(1)}}}"
                    reste = match.group(2).strip()

                    # On vérifie si condition vide via []
                    match_empty = pattern_empty_condition.match(reste)
                    if match_empty:
                        condition = '[]'
                        effet_value = match_empty.group(1).strip()
                    else:
                        if ':' in reste:
                            parts = reste.split(':', 1)
                            condition = parts[0].strip() + " :"
                            effet_value = parts[1].strip()
                        else:
                            effet_value = reste

                else:
                    # Sinon pattern texte suivi de —
                    match = pattern_dash.match(effet)
                    if match:
                        declencheur = match.group(1).strip()
                        reste = match.group(2).strip()

                        match_empty = pattern_empty_condition.match(reste)
                        if match_empty:
                            condition = '[]'
                            effet_value = match_empty.group(1).strip()
                        else:
                            if ':' in reste:
                                parts = reste.split(':', 1)
                                condition = parts[0].strip() + " :"
                                effet_value = parts[1].strip()
                            else:
                                effet_value = reste

                    else:
                        # Aucun déclencheur détecté
                        reste = effet

                        match_empty = pattern_empty_condition.match(reste)
                        if match_empty:
                            condition = '[]'
                            effet_value = match_empty.group(1).strip()
                        else:
                            if ':' in reste:
                                parts = reste.split(':', 1)
                                condition = parts[0].strip() + " :"
                                effet_value = parts[1].strip()
                            else:
                                effet_value = reste

            print(f"  déclencheur = {declencheur}")
            print(f"  condition   = {condition}")
            print(f"  effet       = {effet_value}")

            parsed_results.append({
                'reference': card[0],
                'name': card[1],
                'declencheur': declencheur,
                'condition': condition,
                'effet': effet_value
            })

print("Parsing terminé.")