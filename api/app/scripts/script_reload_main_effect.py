from datetime import datetime, timezone
import time
from app.scripts import card_routine
from app.models.card import Card
from app.extensions import db, socketio
from sqlalchemy.orm import scoped_session, sessionmaker
from concurrent.futures import ThreadPoolExecutor




def run_script(faction: str, workers: int):
    # Démarrer le timer
    start_time = time.time()
    Session = scoped_session(sessionmaker(bind=db.engine))

    def map_jsoncard_to_card_en(card: Card, jsonCard) -> Card:
        if 'cardType' in jsonCard:
          card.MAIN_EFFECT = jsonCard['elements']['MAIN_EFFECT'] if 'MAIN_EFFECT' in jsonCard['elements'] else None
          card.ECHO_EFFECT = jsonCard['elements']['ECHO_EFFECT'] if 'ECHO_EFFECT' in jsonCard['elements'] else None
        return card

    def split_list(data, n):
        k, m = divmod(len(data), n)
        return [data[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]
    
    def process_effect_cards(subset, start_index, count):
        session = Session()
        try:
            socketio.emit('script_output', {'data': f"\033[94mNb Cards : {len(subset)}\033[0m"})
            for index, dbcard in enumerate(subset, start=start_index):
                  socketio.emit('script_output', {'data': f"Card {dbcard.name_en} ({index}/{len(subset)}) | {dbcard.id}"})
                  details = card_routine.get_card_by_reference(dbcard.reference)
                  if details:
                      tempCard = map_jsoncard_to_card_en(dbcard, details)
                      card_to_update = session.query(Card).filter_by(reference=tempCard.reference).first()
                      # Initialiser un drapeau pour suivre les modifications
                      if card_to_update:
                          has_updated = False
                          if tempCard.MAIN_EFFECT != card_to_update.MAIN_EFFECT:
                              card_to_update.MAIN_EFFECT = tempCard.MAIN_EFFECT
                              has_updated = True
                          if tempCard.ECHO_EFFECT != card_to_update.ECHO_EFFECT:
                              card_to_update.ECHO_EFFECT = tempCard.ECHO_EFFECT
                              has_updated = True
                          # Si une modification a été effectuée, mettre à jour `edited_at`
                          if has_updated:
                              detailsEn = card_routine.get_card_by_reference(dbcard.reference, True)
                              card_to_update.main_effect_en = None if 'MAIN_EFFECT' not in detailsEn['elements'] else detailsEn['elements']['MAIN_EFFECT']
                              card_to_update.echo_effect_en = None if 'ECHO_EFFECT' not in detailsEn['elements'] else detailsEn['elements']['ECHO_EFFECT']
                              socketio.emit('script_output', {'data': f"Mise à jour de la carte : {card_to_update.name_en} ({card_to_update.reference})"})
                              session.commit()


        except Exception as e:
            socketio.emit('script_output', {'data': f"\033[91mError : {e}\033[0m"})
        finally:
            session.close()

    def get_effect_cards():
        print("----------- FIX EFFECT CARDS -----------")
        socketio.emit('script_output', {'data': "----------- FIX EFFECT CARDS -----------"})
        session = Session()
        try:
            query = session.query(Card).filter((Card.rarity == 'COMMON') | (Card.rarity == 'RARE'))

            # Appliquer le filtre de faction si fourni
            if faction:
                socketio.emit('script_output', {'data': f"Filtrage des cartes pour la faction : {faction}"})
                query = query.filter(Card.faction == faction)

            existing_cards = {
                card.id: card
                for card in query.order_by(Card.id.asc()).all()
            }
        finally:
            session.close()

        # total_cards = len(existing_cards)
        subsets = split_list(list(existing_cards.values()), workers)

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for i, subset in enumerate(subsets):
                count = 0
                start_index = sum(len(subsets[j]) for j in range(i)) + 1
                futures.append(executor.submit(process_effect_cards, subset, start_index, count))

            for future in futures:
                future.result()  # Attendre que toutes les tâches soient terminées


    get_effect_cards()

    # Fin du timer
    end_time = time.time()
    execution_time = end_time - start_time

    # Conversion en heures, minutes et secondes
    hours, remainder = divmod(execution_time, 3600)
    minutes, seconds = divmod(remainder, 60)


    print(f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
    socketio.emit('script_output', {'data': f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}"})
    print(f"FIX EFFECT terminé")