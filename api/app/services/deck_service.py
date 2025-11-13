from typing import Dict, List, Optional
from datetime import datetime, timezone
from app.models.deck import (
    PlayerDeck, 
    DeckArchetype, 
    DeckCardEffect,  # ✅ Renommé
    compute_deck_signature,
    normalize_card_effect
)
from app.extensions import db
import uuid

class DeckService:
    """
    Service pour parser, normaliser et comparer les decks d'Altered TCG
    Inspiré de HSReplay pour Hearthstone
    """
    
    @staticmethod
    def parse_bga_deck(bga_deck_data: dict, player_id: uuid.UUID) -> Optional[PlayerDeck]:
        """
        Parse un deck depuis le format BGA et le transforme en PlayerDeck
        
        Args:
            bga_deck_data: Dict depuis l'API BGA (voir deck.json)
            player_id: UUID du joueur
            
        Returns:
            PlayerDeck créé ou None si erreur
        """
        try:
            api_data = bga_deck_data.get('API', {})
            
            # Métadonnées du deck
            deck_name = api_data.get('deckName')
            bga_deck_id = api_data.get('id')
            faction = api_data.get('faction')
            hero_uid = api_data.get('hero')
            
            # Récupérer le hero
            hero_card = api_data.get('cards', {}).get('hero', {}).get('card', {})
            hero_name = hero_card.get('properties', {}).get('name', '').split('&')[0].strip()
            
            cards = api_data.get('cards', {})
            
            # ✅ NORMALISATION DES CARTES
            cards_by_effect = {}
            cards_by_uid = {}
            unique_cards = []
            rare_count = 0
            common_count = 0
            
            for key, card_entry in cards.items():
                if key == 'hero':
                    continue  # Le hero est à part
                
                card_data = card_entry.get('card', {})
                card_props = card_data.get('properties', {})
                count = card_entry.get('n', 1)
                
                uid = card_props.get('uid')
                rarity = card_props.get('rarity', 0)  # 0=C, 1=R, 2=U
                
                if not uid:
                    continue
                
                # Compter les raretés
                if rarity == 0:
                    common_count += count
                elif rarity == 1:
                    rare_count += count
                
                # ✅ Détecter les uniques : rarity == 2
                is_unique = (rarity == 2)
                
                if is_unique:
                    unique_cards.append(uid)
                
                # ✅ Normaliser l'effet
                effect_hash = normalize_card_effect(card_props)
                
                # Stocker par effet
                if effect_hash not in cards_by_effect:
                    cards_by_effect[effect_hash] = {
                        'count': 0,
                        'uids': [],
                        'rarity': rarity,
                        'name': card_props.get('name')
                    }
                
                cards_by_effect[effect_hash]['count'] += count
                if uid not in cards_by_effect[effect_hash]['uids']:
                    cards_by_effect[effect_hash]['uids'].append(uid)
                
                # Stocker par UID exact
                cards_by_uid[uid] = count
                
                # ✅ Enregistrer l'effet en DB si nouveau
                DeckService._register_card_effect(effect_hash, card_props, uid)
            
            # ✅ Calculer la signature du deck
            deck_signature = compute_deck_signature(cards_by_effect)
            
            # ✅ Chercher ou créer l'archétype
            archetype = DeckService._find_or_create_archetype(
                faction=faction,
                hero=hero_name,
                effect_signature=deck_signature
            )
            
            # ✅ Vérifier si le deck existe déjà
            existing_deck = PlayerDeck.query.filter_by(
                player_id=player_id,
                deck_signature=deck_signature
            ).first()
            
            if existing_deck:
                # Mettre à jour last_used_at
                existing_deck.last_used_at = datetime.now(timezone.utc)
                existing_deck.deck_name = deck_name or existing_deck.deck_name
                existing_deck.bga_deck_id = bga_deck_id or existing_deck.bga_deck_id
                db.session.commit()
                return existing_deck
            
            # ✅ Créer le nouveau deck
            new_deck = PlayerDeck(
                player_id=player_id,
                bga_deck_id=bga_deck_id,
                deck_name=deck_name,
                archetype_id=archetype.id if archetype else None,
                faction=faction,
                hero=hero_name,
                hero_uid=hero_uid,
                card_count=len(cards) - 1,  # -1 pour le hero
                cards_by_effect=cards_by_effect,
                cards_by_uid=cards_by_uid,
                unique_cards=unique_cards,
                unique_count=len(unique_cards),
                rare_count=rare_count,
                common_count=common_count,
                deck_signature=deck_signature,
                last_used_at=datetime.now(timezone.utc)
            )
            
            db.session.add(new_deck)
            db.session.commit()
            
            # Incrémenter le compteur d'archétype
            if archetype:
                archetype.total_decks += 1
                db.session.commit()
            
            print(f"✅ Deck créé: {deck_name} ({faction}/{hero_name})")
            print(f"   - Signature: {deck_signature[:16]}...")
            print(f"   - Uniques: {len(unique_cards)}")
            print(f"   - Rares: {rare_count}, Communes: {common_count}")
            
            return new_deck
            
        except Exception as e:
            print(f"❌ Erreur parse_bga_deck: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return None
    
    @staticmethod
    def _register_card_effect(effect_hash: str, card_props: dict, uid: str) -> None:
        """
        Enregistre un effet de carte en DB si nouveau
        """
        try:
            existing = DeckCardEffect.query.filter_by(effect_hash=effect_hash).first()
            
            if existing:
                # Ajouter l'UID s'il n'existe pas déjà
                if uid not in existing.variant_uids:
                    existing.variant_uids.append(uid)
                    db.session.commit()
            else:
                # Créer le nouvel effet
                new_effect = DeckCardEffect(
                    effect_hash=effect_hash,
                    card_name=card_props.get('name'),
                    card_type=card_props.get('type'),
                    faction=card_props.get('faction'),
                    variant_uids=[uid],
                    normalized_effect={
                        'costHand': card_props.get('costHand'),
                        'costReserve': card_props.get('costReserve'),
                        'type': card_props.get('type'),
                        'subtypes': card_props.get('subtypes', []),
                        'effectDesc': card_props.get('effectDesc')
                    }
                )
                db.session.add(new_effect)
                db.session.commit()
                
        except Exception as e:
            print(f"⚠️  Erreur _register_card_effect: {e}")
            db.session.rollback()
    
    @staticmethod
    def _find_or_create_archetype(faction: str, hero: str, effect_signature: str) -> Optional[DeckArchetype]:
        """
        Trouve ou crée un archétype de deck
        """
        try:
            # Chercher un archétype existant avec la même signature
            archetype = DeckArchetype.query.filter_by(
                faction=faction,
                hero=hero,
                effect_signature=effect_signature
            ).first()
            
            if not archetype:
                # Créer un nouvel archétype
                archetype = DeckArchetype(
                    name=f"{hero} #{effect_signature[:8]}",  # Nom temporaire
                    faction=faction,
                    hero=hero,
                    effect_signature=effect_signature
                )
                db.session.add(archetype)
                db.session.commit()
                print(f"🆕 Nouvel archétype créé: {archetype.name}")
            
            return archetype
            
        except Exception as e:
            print(f"❌ Erreur _find_or_create_archetype: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def compare_decks(deck1: PlayerDeck, deck2: PlayerDeck) -> Dict:
        """
        Compare deux decks et retourne les différences
        
        Returns:
            {
                'similarity': 0.85,  # Score de similarité (0-1)
                'same_archetype': True,
                'cards_in_common': 35,
                'cards_different': 4,
                'unique_differences': [...],  # Cartes uniques différentes
                'effect_differences': [...]   # Effets différents
            }
        """
        try:
            # Comparaison par signature
            same_archetype = deck1.deck_signature == deck2.deck_signature
            
            # Comparaison par effets
            effects1 = set(deck1.cards_by_effect.keys())
            effects2 = set(deck2.cards_by_effect.keys())
            
            common_effects = effects1 & effects2
            different_effects = effects1 ^ effects2
            
            # Compter les cartes en commun
            cards_in_common = 0
            for effect_hash in common_effects:
                count1 = deck1.cards_by_effect[effect_hash]['count']
                count2 = deck2.cards_by_effect[effect_hash]['count']
                cards_in_common += min(count1, count2)
            
            # Similarité (Jaccard)
            total_cards = deck1.card_count + deck2.card_count
            similarity = (2 * cards_in_common) / total_cards if total_cards > 0 else 0
            
            # Différences dans les uniques
            uniques1 = set(deck1.unique_cards)
            uniques2 = set(deck2.unique_cards)
            unique_differences = list(uniques1 ^ uniques2)
            
            return {
                'similarity': round(similarity, 2),
                'same_archetype': same_archetype,
                'cards_in_common': cards_in_common,
                'cards_different': deck1.card_count - cards_in_common,
                'unique_differences': unique_differences,
                'effect_differences': list(different_effects)
            }
            
        except Exception as e:
            print(f"❌ Erreur compare_decks: {e}")
            return {}
    
    @staticmethod
    def get_meta_snapshot(season: int, faction: str = None) -> List[Dict]:
        """
        Retourne un snapshot du métagame (comme HSReplay)
        
        Returns:
            [
                {
                    'archetype': {...},
                    'play_rate': 15.5,  # %
                    'win_rate': 52.3,   # %
                    'total_games': 1234
                },
                ...
            ]
        """
        try:
            query = db.session.query(DeckArchetype)
            
            if faction:
                query = query.filter_by(faction=faction)
            
            archetypes = query.all()
            
            # Calculer les stats globales
            total_games = sum(a.total_games for a in archetypes)
            
            meta = []
            for archetype in archetypes:
                if archetype.total_games == 0:
                    continue
                
                play_rate = (archetype.total_games / total_games * 100) if total_games > 0 else 0
                
                meta.append({
                    'archetype': archetype.json(),
                    'play_rate': round(play_rate, 1),
                    'win_rate': round(archetype.win_rate, 1),
                    'total_games': archetype.total_games
                })
            
            # Trier par popularité
            meta.sort(key=lambda x: x['play_rate'], reverse=True)
            
            return meta
            
        except Exception as e:
            print(f"❌ Erreur get_meta_snapshot: {e}")
            return []
