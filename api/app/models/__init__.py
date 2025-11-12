# ✅ ORDRE D'IMPORT IMPORTANT : Importer deck.py AVANT player.py
# Car Player a une relation vers PlayerDeck
from app.models.deck import DeckArchetype, PlayerDeck, DeckCardEffect

# Ensuite importer les autres modèles
from app.models.player import Player, PlayerSeasonStats, Team, Tournament, TournamentParticipant
from app.models.game import Game
from app.models.season import Season
from app.models.user import User
from app.models.card import Card
from app.models.offer import Offer
from app.models.offer_purchase import OfferPurchase
from app.models.user_collection import UserCollection
from app.models.user_alert import UserAlert
from app.models.user_search import UserSearch
from app.models.cookie_manager import CookieManager
from app.models.chat_room import ChatRoom
from app.models.chat_message import ChatMessage
from app.models.article import Article
from app.models.new_card import NewCard
from app.models.effect import Effect
from app.models.card_effect import CardEffect
from app.models.card_embedding import CardEmbedding
from app.models.notification import Notification

__all__ = [
    # Decks (en premier)
    'DeckArchetype',
    'PlayerDeck',
    'DeckCardEffect',
    # Autres modèles
    'Player',
    'PlayerSeasonStats',
    'Team',
    'Tournament',
    'TournamentParticipant',
    'Game',
    'Season',
    'User',
    'Card',
    'Offer',
    'OfferPurchase',
    'UserCollection',
    'UserAlert',
    'UserSearch',
    'CookieManager',
    'ChatRoom',
    'ChatMessage',
    'Article',
    'NewCard',
    'Effect',
    'CardEffect',
    'CardEmbedding',
    'Notification'
]
