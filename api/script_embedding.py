import re
import html
import unicodedata
from app.models.card import Card
from app.models.card_embedding import CardEmbedding
from app.extensions import db
from app import create_app
import json

app = create_app()

# REGEXS V6.4 ultra clean
pattern_curly_with_condition = re.compile(r"^\{([^}]+)\}\s*(.*?):\s*(.*)$")
pattern_curly_without_condition = re.compile(r"^\{([^}]+)\}\s*(.*)$")
pattern_dash = re.compile(r"^(.*?—)\s*(.*)")
pattern_empty_condition = re.compile(r'^\[\]\s*(.*)$')
split_regex = re.compile(r'\s{2,}')  # Split sur double espace ou plus

# Nettoyeur HTML/Unicode
def clean_unicode(text):
    if not text:
        return ''
    text = html.unescape(text)
    text = unicodedata.normalize("NFKC", text)
    text = text.replace('\xa0', ' ').replace('\u00a0', ' ')
    return text.strip()

# Normalisation finale pour DB
def normalize_value(text):
    if not text:
        return ''
    text = html.unescape(text)
    text = text.replace('#', '')
    text = text.strip()
    if text.endswith('.'):
        text = text[:-1].strip()
    return text

# Nettoyage pour JSON/dump/API
def sanitize_json_list(lst):
    if not lst:
        return None
    clean = []
    for item in lst:
        if item and item.strip() != '[]':
            cleaned = normalize_value(clean_unicode(item))
            if cleaned:
                # Normalisation supplémentaire pour JSON lisible UTF-8
                cleaned = cleaned.encode('utf-8').decode('utf-8')
                clean.append(cleaned)
    return clean if clean else None

# Parser des effets
def parse_effect_text(effect_text):
    declencheurs, conditions, effets = [], [], []

    full_effect = normalize_value(clean_unicode(effect_text))
    sub_effects = split_regex.split(full_effect)

    for effet in sub_effects:
        effet = effet.strip()
        if not effet:
            continue

        declencheur, condition, effet_value = '[]', '[]', '[]'
        reste = effet

        match = pattern_curly_with_condition.match(effet)
        if match:
            declencheur = f"{{{match.group(1)}}}"
            reste = f"{match.group(2).strip()} : {match.group(3).strip()}"
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

        match_empty = pattern_empty_condition.match(reste)
        if match_empty:
            reste_after_empty = match_empty.group(1).strip()
            if ':' in reste_after_empty:
                parts = reste_after_empty.split(':', 1)
                condition = f"{parts[0].strip()} :"
                effet_value = parts[1].strip()
            else:
                effet_value = reste_after_empty
        elif ':' in reste:
            parts = reste.split(':', 1)
            condition = f"{parts[0].strip()} :"
            effet_value = parts[1].strip()
        else:
            effet_value = reste

        effet_value = re.sub(r'^\[\]\s*', '', effet_value)

        declencheurs.append(normalize_value(declencheur))
        conditions.append(normalize_value(condition))
        effets.append(normalize_value(effet_value))

    return declencheurs, conditions, effets

# Génération des embeddings
with app.app_context():
    existing_refs = {ref for (ref,) in db.session.query(CardEmbedding.reference_card).all()}
    cards = Card.query.filter(~Card.reference.in_(existing_refs)).all()

    for i, card in enumerate(cards):
        if card.MAIN_EFFECT:
            clean_effect = clean_unicode(card.MAIN_EFFECT)
            declencheur, condition, effet = parse_effect_text(clean_effect)



        embedding = CardEmbedding(
            reference_card=card.reference,
            declencheur=sanitize_json_list(declencheur) if declencheur else None,
            condition=sanitize_json_list(condition) if condition else None,
            effet=sanitize_json_list(effet) if effet else None,
            main_cost=card.MAIN_COST or 0,
            reserve_cost=card.RECALL_COST or 0,
            forest=card.FOREST_POWER or 0,
            mountain=card.MOUNTAIN_POWER or 0,
            ocean=card.OCEAN_POWER or 0
        )

        print(f"\rEmbedding... {i+1}/{len(cards)}", end='', flush=True)
        db.session.merge(embedding)

        if i % 500 == 0:
            db.session.commit()

    db.session.commit()
    print()
    print("✅ Embedding terminé (V1.3.2 PROD + CLEAN_JSON + UTF8)")
