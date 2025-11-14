# 📋 CHECKLIST POUR VALIDATION GOOGLE ADSENSE

Date: 14 novembre 2025
Site: altertracker.com

## 🔴 ACTIONS CRITIQUES À FAIRE IMMÉDIATEMENT

### 1. ✅ COMPLÉTER LES MENTIONS LÉGALES
**Fichier:** `/client/src/app/legal/legal.component.html`

**À remplir obligatoirement:**
- [ ] Votre nom complet ou raison sociale
- [ ] Votre adresse postale complète
- [ ] Votre numéro SIRET (si entreprise) ou mention "auto-entrepreneur" ou "particulier"
- [ ] Nom du directeur de publication (probablement vous)
- [ ] Nom et adresse de l'hébergeur (OVH, AWS, Google Cloud, etc.)

**⚠️ SANS CES INFORMATIONS, VOTRE SITE NE SERA PAS VALIDÉ PAR ADSENSE**

### 2. ✅ AJOUTER DU CONTENU PUBLIC SUBSTANTIEL
AdSense exige du contenu de qualité accessible sans connexion.

**Pages à enrichir:**
- [ ] Page d'accueil (`/`) - Ajouter plus de texte explicatif
- [ ] Page "À propos" (`/about`) - ✅ Déjà améliorée
- [ ] Créer au moins 3-5 articles publics sur Altered TCG
  - Guides de débutants
  - Analyses de cartes
  - Stratégies de jeu
  - Actualités du jeu

**Minimum requis:**
- Au moins 20-30 pages avec du contenu original (300+ mots par page)
- Actuellement beaucoup de pages sont protégées par authentification

### 3. 🔄 RENDRE PLUS DE CONTENU ACCESSIBLE SANS CONNEXION

**Pages actuellement protégées à évaluer:**
```typescript
// Dans app.routes.ts - Routes avec TokenGuard
{ path: 'players', component: LadderComponent, canActivate: [TokenGuard] },
{ path: 'stats', component: StatsComponent },  // Vérifier si accessible
{ path: 'cards', component: CardsComponent },  // Vérifier si accessible
```

**Solutions:**
- [ ] Créer une version "preview" du classement joueurs accessible sans connexion
- [ ] Rendre les statistiques de cartes publiques (au moins partiellement)
- [ ] Créer une galerie de decks publics

### 4. 📝 AMÉLIORER LA VISIBILITÉ DES PAGES LÉGALES

**✅ Déjà fait:**
- Mentions légales ajoutées au footer
- Contact visible dans le header
- Politique de confidentialité accessible

**À vérifier:**
- [ ] Les liens fonctionnent correctement
- [ ] Les pages sont indexables (pas de noindex)

---

## 🟡 RECOMMANDATIONS IMPORTANTES

### 5. CONTENU ORIGINAL ET DE QUALITÉ

**Créer du contenu unique:**
- [ ] Guide complet sur Altered TCG pour débutants
- [ ] Analyses de méta (meta reports hebdomadaires)
- [ ] Top 10 des cartes par faction
- [ ] Guides de construction de deck
- [ ] Actualités et nouveautés du jeu

**Qualité du contenu:**
- 500-1000 mots minimum par article
- Bien structuré avec titres et sous-titres
- Images pertinentes
- Liens internes vers d'autres pages du site

### 6. NAVIGATION ET EXPÉRIENCE UTILISATEUR

**✅ Déjà en place:**
- Menu de navigation clair
- Footer avec liens légaux
- Design responsive

**À améliorer:**
- [ ] Ajouter un sitemap HTML (en plus du sitemap.xml)
- [ ] Créer un plan du site accessible depuis le footer
- [ ] Améliorer le breadcrumb sur les pages profondes

### 7. OPTIMISATION SEO

**robots.txt ✅ Correct:**
```
User-agent: *
Disallow: /api/
Sitemap: https://altertracker.com/sitemap.xml
```

**Vérifier le sitemap.xml:**
- [ ] Contient toutes les pages publiques importantes
- [ ] URL canoniques correctes
- [ ] Dates de mise à jour présentes

**Meta tags:**
- [ ] Chaque page a une meta description unique
- [ ] Titres de pages uniques et descriptifs
- [ ] Open Graph tags pour le partage social

---

## 🟢 BONNES PRATIQUES SUPPLÉMENTAIRES

### 8. PREUVE D'ACTIVITÉ ET DE TRAFIC

**Avant de postuler à AdSense:**
- [ ] Site en ligne depuis au moins 1-2 mois
- [ ] Trafic régulier (même modeste)
- [ ] Contenu mis à jour régulièrement
- [ ] Preuve d'engagement (commentaires, partages, etc.)

### 9. CONFORMITÉ ADSENSE

**Vérifier:**
- [ ] Pas de contenu dupliqué (copié d'autres sites)
- [ ] Pas de contenu pour adultes
- [ ] Pas de contenu illégal ou dangereux
- [ ] Pas de fausses informations
- [ ] Respect des droits d'auteur (surtout pour les images de cartes)

### 10. ASPECTS TECHNIQUES

**Performance:**
- [ ] Site rapide (< 3s de chargement)
- [ ] HTTPS activé ✅ (déjà en place)
- [ ] Pas d'erreurs 404 importantes
- [ ] Mobile-friendly ✅ (déjà en place)

**Monitoring:**
- [ ] Google Search Console configuré
- [ ] Google Analytics installé
- [ ] Vérifier les erreurs d'exploration

---

## 📊 ÉTAT ACTUEL DU SITE

### ✅ Points Forts:
- Design professionnel et moderne
- HTTPS et SSL configurés
- Politique de confidentialité RGPD complète
- Politique de cookies détaillée
- ads.txt présent avec bon publisher ID
- Structure technique solide
- Mobile responsive

### ❌ Points Bloquants Identifiés:
1. **CRITIQUE:** Mentions légales incomplètes (nom, adresse manquants)
2. **CRITIQUE:** Contenu public insuffisant (beaucoup derrière authentification)
3. **IMPORTANT:** Manque d'articles et de contenu original substantiel
4. **IMPORTANT:** Pas assez de pages publiques accessibles aux crawlers

### 🎯 Score Actuel Estimé: 4/10
**Pour validation AdSense, minimum requis: 8/10**

---

## 🚀 PLAN D'ACTION PRIORITAIRE

### Semaine 1 (CRITIQUE):
1. ✅ Compléter les mentions légales avec vos vraies informations
2. ✅ Rendre le classement joueurs accessible sans connexion (au moins top 50)
3. ✅ Créer 5 articles substantiels sur Altered TCG

### Semaine 2:
4. Enrichir la page d'accueil avec plus de contenu explicatif
5. Créer une section "Guides" avec 3-5 guides complets
6. Optimiser le SEO de toutes les pages publiques
7. Vérifier que le sitemap.xml est complet et soumis à Google Search Console

### Semaine 3:
8. Ajouter 5-10 articles supplémentaires
9. Créer une galerie de decks publics
10. Améliorer les meta descriptions de toutes les pages
11. Soumettre à AdSense

---

## 📧 APRÈS CES MODIFICATIONS

**Avant de soumettre à AdSense:**
- [ ] Toutes les mentions légales sont complètes et exactes
- [ ] Au moins 20 pages publiques avec contenu original
- [ ] Navigation fluide sans erreurs
- [ ] Site actif depuis au moins 1 mois
- [ ] Trafic régulier visible dans Analytics

**Processus de soumission:**
1. Connectez-vous à votre compte AdSense
2. Ajoutez votre site altertracker.com
3. Ajoutez le code AdSense dans le head de votre site
4. Attendez la validation (peut prendre 1-2 semaines)

---

## 🆘 EN CAS DE REFUS

**Raisons communes de refus:**
- Contenu insuffisant → Ajouter plus d'articles
- Informations légales manquantes → Compléter les mentions légales
- Contenu dupliqué → Créer du contenu 100% original
- Site trop récent → Attendre et continuer à publier
- Navigation complexe → Simplifier l'accès aux pages principales

**Après correction:**
- Attendre 1-2 semaines avant de resoumettre
- Documenter tous les changements effectués
- Soumettre à nouveau avec une note explicative

---

## 📞 CONTACT GOOGLE ADSENSE

Si refusé, vous pouvez:
- Consulter le Help Center: https://support.google.com/adsense
- Demander un réexamen après corrections
- Contacter le support AdSense pour plus de détails

---

**Note importante:** La validation AdSense peut prendre du temps et nécessite de la patience. 
Concentrez-vous sur la création de contenu de qualité et le respect des politiques AdSense.

Bon courage ! 🚀
