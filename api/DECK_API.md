# 🎴 API Decks - Guide d'utilisation

## 📋 Routes disponibles

### 1. **Récupérer un deck**
```http
GET /api/decks/<deck_id>?include_cards=true
```

**Exemple de réponse :**
```json
{
  "id": "uuid",
  "deck_name": "Post LCQ",
  "faction": "OR",
  "hero": "Sigismar",
  "card_count": 39,
  "unique_count": 2,
  "rare_count": 15,
  "total_games": 5,
  "win_rate": 60.0,
  "cards_by_uid": {
    "ALT_CORE_B_OR_05_R": 3,
    "ALT_CORE_B_OR_16_R": 2
  },
  "unique_cards": ["ALT_SPECIAL_U_123"]
}
```

---

### 2. **Decks d'un joueur**
```http
GET /api/decks/player/<player_id>?season=2&faction=OR&page=1&limit=50
```

**Exemple de réponse :**
```json
{
  "decks": [...],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "total_decks": 125,
    "limit": 50
  }
}
```

---

### 3. **Comparer deux decks**
```http
GET /api/decks/compare?deck1=<uuid1>&deck2=<uuid2>
```

**Exemple de réponse :**
```json
{
  "deck1": {...},
  "deck2": {...},
  "comparison": {
    "similarity": 0.85,
    "same_archetype": true,
    "cards_in_common": 35,
    "cards_different": 4,
    "unique_differences": ["ALT_SPECIAL_U_123"],
    "effect_differences": ["hash1", "hash2"]
  }
}
```

---

### 4. **Snapshot du métagame (type HSReplay)**
```http
GET /api/decks/meta/snapshot?season=2&faction=OR
```

**Exemple de réponse :**
```json
{
  "season": 2,
  "faction": "OR",
  "meta": [
    {
      "archetype": {
        "id": "uuid",
        "name": "Sigismar Tokens",
        "faction": "OR",
        "hero": "Sigismar",
        "total_decks": 250,
        "total_games": 1234,
        "win_rate": 52.3
      },
      "play_rate": 15.5,
      "win_rate": 52.3,
      "total_games": 1234
    }
  ]
}
```

---

### 5. **Statistiques globales**
```http
GET /api/decks/stats?season=2
```

**Exemple de réponse :**
```json
{
  "season": 2,
  "total_decks": 5420,
  "unique_archetypes": 45,
  "top_factions": [
    {"faction": "OR", "count": 1250},
    {"faction": "MU", "count": 980}
  ],
  "top_heroes": [
    {"hero": "Sigismar", "count": 650},
    {"hero": "Teija", "count": 520}
  ]
}
```

---

## 🔧 Script d'import

### Tester sans modifications
```bash
python script_import_decks.py --season 2 --limit 10 --dry-run
```

### Importer une saison
```bash
python script_import_decks.py --season 2 --limit 100
```

### Import complet
```bash
python script_import_decks.py --all --batch-size 50
```

---

## 📊 Architecture technique

### Stockage optimisé
- **Avant :** ~500 KB par deck (JSON complet BGA)
- **Après :** ~5 KB par deck (normalisation)
- **Économie :** ~90% d'espace

### Normalisation des cartes
```json
{
  "cards_by_effect": {
    "hash_abc123": {
      "count": 3,
      "uids": ["ALT_CORE_B_OR_05_R"],
      "rarity": 1,
      "name": "Token Generator"
    }
  },
  "cards_by_uid": {
    "ALT_CORE_B_OR_05_R": 3
  }
}
```

### Signatures de deck
- Hash SHA-256 des effets normalisés
- Permet la comparaison rapide
- Détection automatique des archétypes

---

## 🎯 Cas d'usage

### 1. Voir le deck d'une partie
```typescript
// Dans le frontend
const game = await getGame(gameId);
const deck1 = await getDeck(game.player1_deck_id);
const deck2 = await getDeck(game.player2_deck_id);
```

### 2. Comparer ses decks
```typescript
const myDecks = await getPlayerDecks(playerId, { season: 2 });
const comparison = await compareDecks(myDecks[0].id, myDecks[1].id);
```

### 3. Analyser le méta
```typescript
const meta = await getMetaSnapshot({ season: 2, faction: 'OR' });
// Afficher les archétypes populaires
meta.meta.forEach(archetype => {
  console.log(`${archetype.archetype.name}: ${archetype.play_rate}%`);
});
```

---

## ✅ Système complet

✅ Normalisation automatique des cartes
✅ Détection des cartes uniques (3 max)
✅ Archétypes auto-créés
✅ Comparaison rapide via signatures
✅ Méta snapshot type HSReplay
✅ Import bulk automatisé
✅ Routes API complètes
