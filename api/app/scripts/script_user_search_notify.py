from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import re
import time
from typing import Dict
from urllib.parse import parse_qs, unquote
import requests
from sqlalchemy import func
from app.models.user_alert import UserAlert
from app.services.card_service import is_image_url_accessible
from app.config import ConfigEnv
from app.data.card_data import lower_strip, prepare_like_query
from app.models.new_card import NewCard
from app.models.user import User
from app.models.user_search import UserSearch
from app.models.card import Card
from app.extensions import db, socketio
from sqlalchemy.orm import scoped_session, sessionmaker
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import text


def run_script(workers: int):
    # Démarrer le timer
    start_time = time.time()
    Session = scoped_session(sessionmaker(bind=db.engine))

    def split_list(data, n):
        k, m = divmod(len(data), n)
        return [data[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]
    
    def search_cards_data(name, rarity, faction, set, subtype, main_effect, main_effect_2, echo_effect, exclude_effect,
        main_cost_range, recall_cost_range, forest_power_range, mountain_power_range, ocean_power_range, zero_power,
        no_condition, en, dataset):
        # Vérifier si le nom correspond à la regexp ^ALT_
        if name and re.match(r'^ALT_', name):
            # Si oui, on ne fait pas de recherche
            return None

        query = dataset

        # Utiliser les colonnes en anglais si en=True
        name_column = Card.name_en if en else Card.name
        main_effect_column = Card.main_effect_en if en else Card.MAIN_EFFECT
        echo_effect_column = Card.echo_effect_en if en else Card.ECHO_EFFECT

        if name:
            name = lower_strip(name)
            query = query.filter(func.lower(name_column).like(f'%{prepare_like_query(name)}%', escape='\\'))

        if rarity:
            if isinstance(rarity, str):
                rarity_list = [r.strip() for r in rarity.split(',') if r.strip()]
                query = query.filter(Card.rarity.in_(rarity_list))
            elif isinstance(rarity, list):
                query = query.filter(Card.rarity.in_(rarity))
            else:
                query = query.filter(Card.rarity == rarity)

        if faction:
            if isinstance(faction, str):
                faction_list = [f.strip() for f in faction.split(',') if f.strip()]
                query = query.filter(Card.faction.in_(faction_list))
            elif isinstance(faction, list):
                query = query.filter(Card.faction.in_(faction))
            else:
                query = query.filter(Card.faction == faction)

        if set:
            query = query.filter(Card.set == set)

        if subtype:
            query = query.filter(
                func.concat(',', Card.subtype, ',').like(f'%,{subtype},%')
            )

        if main_effect and not main_effect_2:
            # Si seulement main_effect est fourni
            main_effect = lower_strip(main_effect)
            query = query.filter(func.lower(main_effect_column).like(f'%{prepare_like_query(main_effect)}%', escape='\\'))

        if main_effect and main_effect_2:
            # Si main_effect et main_effect_2 sont fournis
            main_effect = lower_strip(main_effect)
            main_effect_2 = lower_strip(main_effect_2)
            # Échapper les caractères spéciaux pour la regex
            main_effect_regex = re.escape(main_effect)
            main_effect_2_regex = re.escape(main_effect_2)
            query = query.filter(
                func.lower(main_effect_column).like(f'%{prepare_like_query(main_effect)}%', escape='\\'),
                func.regexp_replace(func.lower(main_effect_column), main_effect_regex, '', 1).like(f'%{prepare_like_query(main_effect_2)}%', escape='\\')
            )

        if exclude_effect:
            # Si exclude_effect est fourni, on l'utilise pour exclure les cartes
            # Supporter plusieurs termes séparés par des virgules
            exclude_terms = [term.strip() for term in exclude_effect.split(',') if term.strip()]
            
            for term in exclude_terms:
                term = lower_strip(term)
                query = query.filter(~func.lower(main_effect_column).like(f'%{prepare_like_query(term)}%', escape='\\'))

        if echo_effect:
            echo_effect = lower_strip(echo_effect)
            query = query.filter(func.lower(echo_effect_column).like(f'%{prepare_like_query(echo_effect)}%', escape='\\'))

        # Recherche par plage pour main_cost
        if main_cost_range:
            if 'min' in main_cost_range and 'max' in main_cost_range and main_cost_range['min'] == main_cost_range['max']:
                query = query.filter(Card.MAIN_COST == main_cost_range['min'])
            if 'min' in main_cost_range:
                query = query.filter(Card.MAIN_COST >= main_cost_range['min'])
            if 'max' in main_cost_range:
                query = query.filter(Card.MAIN_COST <= main_cost_range['max'])

        # Recherche par plage pour recall_cost
        if recall_cost_range:
            if 'min' in recall_cost_range and 'max' in recall_cost_range and recall_cost_range['min'] == recall_cost_range['max']:
                query = query.filter(Card.RECALL_COST == recall_cost_range['min'])
            else:
                if 'min' in recall_cost_range:
                    query = query.filter(Card.RECALL_COST >= recall_cost_range['min'])
                if 'max' in recall_cost_range:
                    query = query.filter(Card.RECALL_COST <= recall_cost_range['max'])

        # Recherche par plage pour forest_power
        if forest_power_range and zero_power is not True:
            if 'min' in forest_power_range and 'max' in forest_power_range and forest_power_range['min'] == forest_power_range['max']:
                query = query.filter(Card.FOREST_POWER == forest_power_range['min'])
            else:
                if 'min' in forest_power_range:
                    query = query.filter(Card.FOREST_POWER >= forest_power_range['min'])
                if 'max' in forest_power_range:
                    query = query.filter(Card.FOREST_POWER <= forest_power_range['max'])

        # Recherche par plage pour mountain_power
        if mountain_power_range and zero_power is not True:
            if 'min' in mountain_power_range and 'max' in mountain_power_range and mountain_power_range['min'] == mountain_power_range['max']:
                query = query.filter(Card.MOUNTAIN_POWER == mountain_power_range['min'])
            else:
                if 'min' in mountain_power_range:
                    query = query.filter(Card.MOUNTAIN_POWER >= mountain_power_range['min'])
                if 'max' in mountain_power_range:
                    query = query.filter(Card.MOUNTAIN_POWER <= mountain_power_range['max'])

        # Recherche par plage pour ocean_power
        if ocean_power_range and zero_power is not True:
            if 'min' in ocean_power_range and 'max' in ocean_power_range and ocean_power_range['min'] == ocean_power_range['max']:
                query = query.filter(Card.OCEAN_POWER == ocean_power_range['min'])
            else:
                if 'min' in ocean_power_range:
                    query = query.filter(Card.OCEAN_POWER >= ocean_power_range['min'])
                if 'max' in ocean_power_range:
                    query = query.filter(Card.OCEAN_POWER <= ocean_power_range['max'])

        if zero_power is True:
            query = query.filter(
                (Card.FOREST_POWER == 0) | 
                (Card.MOUNTAIN_POWER == 0) | 
                (Card.OCEAN_POWER == 0)
            )

        if no_condition:
            if not en:
                query = query.filter(
                    ~func.lower(Card.MAIN_EFFECT).like('% si %') &
                    ~func.lower(Card.MAIN_EFFECT).like('% s\'il %')
                )
            else:
                query = query.filter(
                    ~func.lower(Card.MAIN_EFFECT).like('% if %') &
                    ~func.lower(Card.MAIN_EFFECT).like('% when %')
                )

        # Limiter à 10 000 résultats
        query = query.limit(10000)

        # Exécution de la requête
        results = query.all()

        # Transformation des résultats en JSON
        return results
    
    def parse_range_param(range_value):
        if not range_value:
            return None
        
        if '-' in range_value:
            # Cas "1-2"
            parts = range_value.split('-')
            if len(parts) == 2:
                try:
                    min_val = int(parts[0].strip())
                    max_val = int(parts[1].strip())
                    return {"min": min_val, "max": max_val}
                except ValueError:
                    return None
        else:
            # Cas "1" (valeur unique)
            try:
                val = int(range_value.strip())
                return {"min": val, "max": val}
            except ValueError:
                return None
        
        return None

    def parse_search_params(url_search):
        # Enlève le préfixe '/cards?' si présent
        if url_search.startswith('/cards?'):
            url_search = url_search[len('/cards?'):]
        # Parse les paramètres
        params = parse_qs(url_search)
        # Décoder les valeurs et simplifier (prend le premier élément de chaque liste)
        clean_params = {k: unquote(v[0]) if v else None for k, v in params.items()}
        
        # Parser les valeurs de range
        range_fields = ['main_cost_range', 'recall_cost_range', 'forest_power_range', 
                      'mountain_power_range', 'ocean_power_range', 'price_range']
        
        for field in range_fields:
            if field in clean_params:
                clean_params[field] = parse_range_param(clean_params[field])
        
        return clean_params
    
    def save_user_alert_service(data: Dict, session) -> Dict:
        mapped_data = {
            "id_user": data.get("id_user"),
            "reference_card": data.get("reference_card"),
            "id_search": data.get("id_search"),
            "mail_active": True,
            "created_at": datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(timezone.utc)
        }
        saved_alert = save_user_alert_data(mapped_data, session)
        return saved_alert.json()
    
    def save_user_alert_data(data: dict, session) -> UserAlert:
        try:
            user_alert = UserAlert(**data)
            session.add(user_alert)
            session.commit()
            return user_alert
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Erreur lors de la sauvegarde de l'alerte utilisateur : {str(e)}")
        
    def convert_to_boolean(value):
        """Convertit une valeur en boolean de manière sûre."""
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() == 'true'
        return bool(value)

    def process_notify(subset, start_index):
        session = Session()
        try:
            socketio.emit('script_output', {'data': f"\033[94mNb searchs : {len(subset)}\033[0m"})
            new_card_refs = [nc.reference for nc in session.query(NewCard.reference).all()]
            new_cards = session.query(Card).filter(Card.reference.in_(new_card_refs))
            for index, search in enumerate(subset, start=start_index):
                socketio.emit('script_output', {'data': f"Notify ({index}/{len(subset)})"})
                params = parse_search_params(search.url_search)

                if 'dataset_type' in params:
                    socketio.emit('script_output', {'data': f"Skip search with dataset_type : {search.name_search} ({search.id})"})
                    continue
                result = search_cards_data(
                    name=params.get('name'),
                    rarity=params.get('rarity'),
                    faction=params.get('faction'),
                    set=params.get('set'),
                    subtype=params.get('subtype'),
                    main_effect=params.get('main_effect'),
                    main_effect_2=params.get('main_effect_2'),
                    echo_effect=params.get('echo_effect'),
                    exclude_effect=params.get('exclude_effect'),
                    main_cost_range=params.get('main_cost_range'),
                    recall_cost_range=params.get('recall_cost_range'),
                    forest_power_range=params.get('forest_power_range'),
                    mountain_power_range=params.get('mountain_power_range'),
                    ocean_power_range=params.get('ocean_power_range'),
                    zero_power=convert_to_boolean(params.get('zero_power')),
                    no_condition=convert_to_boolean(params.get('no_condition')),
                    en=convert_to_boolean(params.get('en')),
                    dataset=new_cards  # ou ce que tu utilises comme dataset
                )
                if ConfigEnv.FLASK_ENV == 'production':
                    for card in result:
                        user = session.query(User).filter(User.id == search.id_user).first()
                        if user and user.discord_id:
                            if search.active_favorite:
                                alert_data = {
                                    "id_user": user.id,
                                    "id_search": search.id,
                                    "reference_card": card.reference
                                }
                                save_user_alert_service(alert_data, session)
                            socketio.emit('script_output', {'data': f"discord alert send : {card.name_en} {card.reference} {user.username}"})
                            image_url = card.imagePath if is_image_url_accessible(card.imagePath) else "https://altertracker.com/assets/img/cardback.webp"
                            embed_message = {
                                "username": user.username,
                                "name_search": search.name_search,
                                "name_card": card.name,
                                "reference": card.reference,
                                "url_image_card": image_url,
                                "lien_vers_alerts": f"https://altertracker.com/stats/{card.reference}"
                            }
                            response = requests.post(f"{ConfigEnv.DISCORD_BOT_URI}/sendalertnewcard", json={"discord_id": user.discord_id, "embed_message": embed_message})
                else:
                    socketio.emit('script_output', {'data': f"Search : {search.name_search} ({search.id})"})
                    for card in result:
                        user = session.query(User).filter(User.id == search.id_user).first()
                        socketio.emit('script_output', {'data': f"discord alert send : {card.name_en} {card.reference} {user.username}"})


        except Exception as e:
            socketio.emit('script_output', {'data': f"\033[91mError : {e}\033[0m"})
        finally:
            session.close()

    def notify():
        print("----------- USER SEARCH NOTIFY -----------")
        socketio.emit('script_output', {'data': "----------- USER SEARCH NOTIFY -----------"})
        session = Session()
        try:
            query = (
                session.query(UserSearch)
                .join(User, UserSearch.id_user == User.id)
                .filter(
                    UserSearch.active_notification == True,
                    User.discord_id.isnot(None)
                )
            )

            user_searchs = {
                user_search.id: user_search
                for user_search in query.all()
            }
        finally:
            session.close()

        # total_cards = len(existing_cards)
        subsets = split_list(list(user_searchs.values()), workers)

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for i, subset in enumerate(subsets):
                start_index = sum(len(subsets[j]) for j in range(i)) + 1
                futures.append(executor.submit(process_notify, subset, start_index))

            for future in futures:
                future.result()  # Attendre que toutes les tâches soient terminées
        session.execute(text("TRUNCATE TABLE new_cards;"))
        session.commit()

    notify()

    # Fin du timer
    end_time = time.time()
    execution_time = end_time - start_time

    # Conversion en heures, minutes et secondes
    hours, remainder = divmod(execution_time, 3600)
    minutes, seconds = divmod(remainder, 60)


    print(f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
    socketio.emit('script_output', {'data': f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}"})
    print(f"USER SEARCH NOTIFY terminé")