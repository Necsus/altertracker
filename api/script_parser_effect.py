import re
from app.models.card import Card
from app.extensions import db
from app import create_app

app = create_app()

# =========================
# REGEX PRE-COMPILÉES
# =========================

# Cas {déclencheur} avec éventuelle condition
pattern_curly_with_condition = re.compile(r"^\{([^}]+)\}\s*(.*?):\s*(.*)$")
pattern_curly_without_condition = re.compile(r"^\{([^}]+)\}\s*(.*)$")

# Cas déclencheur texte suivi de tiret long
pattern_dash = re.compile(r"^(.*?—)\s*(.*)")

# Condition vide []
pattern_empty_condition = re.compile(r'^\[\]\s*(.*)$')

# Split des effets multiples (tu avais bien validé ce split sur espace insécable)
split_regex = re.compile(r'\  \s*')  # attention ici à ton espace insécable, si besoin je peux encore sécuriser

parsed_results = []

with app.app_context():
    cards = db.session.query(
            Card.reference,
            Card.name_en,
            Card.MAIN_EFFECT
        ).filter(Card.MAIN_EFFECT.isnot(None),Card.name == "Dédale").all()

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
            reste = effet

            # =========================
            # DÉTECTION DU DÉCLENCHEUR
            # =========================

            match = pattern_curly_with_condition.match(effet)
            if match:
                declencheur = f"{{{match.group(1)}}}"
                reste = match.group(2).strip() + " : " + match.group(3).strip()
            else:
                match = pattern_curly_without_condition.match(effet)
                if match:
                    declencheur = f"{{{match.group(1)}}}"
                    reste = match.group(2).strip()
                else:
                    match = pattern_dash.match(effet)
                    if match:
                        declencheur = match.group(1).strip()
                        reste = match.group(2).strip()
                    else:
                        reste = effet  # Aucun déclencheur détecté

            # =========================
            # TRAITEMENT DU RESTE
            # =========================

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

            # =========================
            # OUTPUT INTERNE
            # =========================

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