import re
from app.models.card import Card
from app.models.effect import Effect
from app.extensions import db
from app import create_app

app = create_app()

# REGEXS
pattern_curly_with_condition = re.compile(r"^\{([^}]+)\}\s*(.*?):\s*(.*)$")
pattern_curly_without_condition = re.compile(r"^\{([^}]+)\}\s*(.*)$")
pattern_dash = re.compile(r"^(.*?—)\s*(.*)")
pattern_empty_condition = re.compile(r'^\[\]\s*(.*)$')
split_regex = re.compile(r'\  \s*')  # Split sur l’espace insécable double

# Super nettoyeur final
def normalize_value(text):
    if not text:
        return text
    text = text.replace('#', '')  # supprime les #
    text = text.strip()

    if text.endswith('.'):
        text = text[:-1].strip()

    return text

# Parser principal
def parse_effect_text(effect_text):
    parsed_entries = []

    full_effect = effect_text.strip('.')
    sub_effects = split_regex.split(full_effect)

    for effet in sub_effects:
        effet = effet.strip()
        if not effet:
            continue

        declencheur, condition, effet_value = '[]', '[]', '[]'
        reste = effet

        # Déclencheur {X} Condition : Effet
        match = pattern_curly_with_condition.match(effet)
        if match:
            declencheur = f"{{{match.group(1)}}}"
            reste = match.group(2).strip() + " :" + match.group(3).strip()
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
                    reste = effet

        match_empty = pattern_empty_condition.match(reste)
        if match_empty:
            reste_after_empty = match_empty.group(1).strip()
            if ':' in reste_after_empty:
                parts = reste_after_empty.split(':', 1)
                condition = parts[0].strip() + " :"
                effet_value = parts[1].strip()
            else:
                condition = '[]'
                effet_value = reste_after_empty
        else:
            if ':' in reste:
                parts = reste.split(':', 1)
                condition = parts[0].strip() + " :"
                effet_value = parts[1].strip()
            else:
                effet_value = reste

        effet_value = re.sub(r'^\[\]\s*', '', effet_value)

        # On normalise AVANT insertion
        parsed_entries.append(('declencheur', normalize_value(declencheur)))
        parsed_entries.append(('condition', normalize_value(condition)))
        parsed_entries.append(('effet', normalize_value(effet_value)))

    return parsed_entries

# Insertion ORM dédupliquée
def insert_effect(type_value, value, language='en'):
    value = normalize_value(value)
    if value.strip() == '[]' or value.strip() == '':
        return
    existing = Effect.query.filter_by(type=type_value, value=value, language=language).first()
    if not existing or existing.language == 'fr':
        effect = Effect(type=type_value, value=value, language=language)
        print(f"Add : {type_value} = {value}")
        db.session.add(effect)

with app.app_context():
    cards = db.session.query(
            Card.reference,
            Card.name_en,
            Card.main_effect_en
        ).filter(Card.main_effect_en.isnot(None)).all()

    for i, card in enumerate(cards):
        parsed_effects = parse_effect_text(card.main_effect_en)
        for type_value, value in parsed_effects:
            insert_effect(type_value, value)

        if i % 500 == 0:
            print(f"Processed {i} cards, committing changes...")
            db.session.commit()
            db.session.expunge_all()

    db.session.commit()
    print("Insertion terminée avec succès (V6.4 ULTRA CLEAN FINAL ✅)")