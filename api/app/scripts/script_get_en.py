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
          card.image_path_en = jsonCard['imagePath'] if 'imagePath' in jsonCard else None
          card.main_effect_en = jsonCard['elements']['MAIN_EFFECT'] if 'MAIN_EFFECT' in jsonCard['elements'] else None
          card.echo_effect_en = jsonCard['elements']['ECHO_EFFECT'] if 'ECHO_EFFECT' in jsonCard['elements'] else None
        return card

    def split_list(data, n):
        k, m = divmod(len(data), n)
        return [data[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]
    
    def process_en_cards(subset, start_index, count):
        """Traite un sous-ensemble de cartes pour la tâche `get_unique`."""
        session = Session()
        try:
            socketio.emit('script_output', {'data': f"\033[94mNb Cards : {len(subset)}\033[0m"})
            for index, dbcard in enumerate(subset, start=start_index):
                  socketio.emit('script_output', {'data': f"Card {dbcard.name_en} ({index}/{len(subset)}) | {dbcard.id}"})
                  if dbcard.image_path_en is None:
                      detailsEn = card_routine.get_card_by_reference(dbcard.reference, True)
                      if detailsEn:
                          tempCard = map_jsoncard_to_card_en(dbcard, detailsEn)
                          card_to_update = session.query(Card).filter_by(reference=tempCard.reference).first()
                          # Initialiser un drapeau pour suivre les modifications
                          if card_to_update:
                              has_updated = False
                              if tempCard.image_path_en is not None:
                                  if str(card_to_update.image_path_en) != str(tempCard.imagePath) or card_to_update.image_path_en is None:
                                      card_to_update.image_path_en = tempCard.image_path_en
                                      has_updated = True
                              if tempCard.main_effect_en is not None:
                                  if str(card_to_update.main_effect_en) != str(tempCard.main_effect_en) \
                                      or card_to_update.main_effect_en is None or tempCard.main_effect_en is None:
                                      card_to_update.main_effect_en = tempCard.main_effect_en
                                      has_updated = True
                              if tempCard.echo_effect_en is not None:
                                  if str(card_to_update.echo_effect_en) != str(tempCard.echo_effect_en) \
                                      or card_to_update.echo_effect_en is None or tempCard.echo_effect_en is None:
                                      card_to_update.echo_effect_en = tempCard.echo_effect_en
                                      has_updated = True
                              # Si une modification a été effectuée, mettre à jour `edited_at`
                              if has_updated:
                                  socketio.emit('script_output', {'data': f"Mise à jour de la carte : {card_to_update.name_en} ({card_to_update.reference})"})
                                  card_to_update.edited_at = datetime.now(timezone.utc)
                                  session.commit()
                      time.sleep(0.1)

        except Exception as e:
            socketio.emit('script_output', {'data': f"\033[91mError : {e}\033[0m"})
        finally:
            session.close()

    def get_en_cards():
        print("----------- GET EN CARDS -----------")
        socketio.emit('script_output', {'data': "----------- GET EN CARDS -----------"})
        session = Session()
        try:
            query = session.query(Card).filter(Card.image_path_en == None)

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
                futures.append(executor.submit(process_en_cards, subset, start_index, count))

            for future in futures:
                future.result()  # Attendre que toutes les tâches soient terminées


    get_en_cards()

    # Fin du timer
    end_time = time.time()
    execution_time = end_time - start_time

    # Conversion en heures, minutes et secondes
    hours, remainder = divmod(execution_time, 3600)
    minutes, seconds = divmod(remainder, 60)


    print(f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
    socketio.emit('script_output', {'data': f"Temps d'exécution : {int(hours):02}:{int(minutes):02}:{int(seconds):02}"})
    print(f"GET EN terminé")