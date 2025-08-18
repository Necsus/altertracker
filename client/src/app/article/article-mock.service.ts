import { Injectable } from '@angular/core';
import { delay, Observable, of } from 'rxjs';
import { ArticleListModel, ArticleModel } from '../01_models/03_business/article.model';

@Injectable({
  providedIn: 'root'
})
export class ArticleMockService {

  private mockArticles: ArticleModel[] = [
    {
      id: 1,
      title: "Guide complet : Construire son premier deck Altered",
      slug: "guide-complet-construire-premier-deck-altered",
      content: `
        <h2>Introduction</h2>
        <p>Construire son premier deck dans Altered peut sembler intimidant, mais avec les bonnes bases, vous serez rapidement prêt à affronter vos adversaires.</p>
        
        <h2>Les fondamentaux</h2>
        <p>Un deck Altered se compose de 40 cartes minimum, réparties entre différents types :</p>
        <ul>
          <li><strong>Héros :</strong> 1 carte obligatoire qui définit votre faction</li>
          <li><strong>Permanents :</strong> Vos créatures et sorts permanents</li>
          <li><strong>Sorts :</strong> Actions à usage unique</li>
        </ul>
        
        <h2>Choisir sa faction</h2>
        <p>Chaque faction a ses spécificités :</p>
        <ul>
          <li><strong>Axiom :</strong> Contrôle et magie</li>
          <li><strong>Bravos :</strong> Agression et rapidité</li>
          <li><strong>Lyra :</strong> Synergie et croissance</li>
          <li><strong>Muna :</strong> Manipulation et ruse</li>
          <li><strong>Ordis :</strong> Structure et défense</li>
          <li><strong>Yzmir :</strong> Chaos et imprévisibilité</li>
        </ul>
        
        <h2>Construction de la courbe de mana</h2>
        <p>Une courbe de mana équilibrée est essentielle. Voici une répartition recommandée :</p>
        <ul>
          <li>Coût 1-2 : 8-12 cartes</li>
          <li>Coût 3-4 : 12-16 cartes</li>
          <li>Coût 5+ : 6-8 cartes</li>
        </ul>
        
        <h2>Conseils pour débuter</h2>
        <p>Pour votre premier deck, concentrez-vous sur une stratégie simple et cohérente. Évitez de mélanger trop de mécaniques différentes.</p>
      `,
      excerpt: "Découvrez les bases essentielles pour construire votre premier deck Altered et commencer à jouer avec confiance.",
      author: "Julien",
      featured_image: "https://images.unsplash.com/photo-1606092195730-5d7b9af1efc5?w=800&h=400&fit=crop",
      reading_time: 8,
      views: 1247,
      status: 'published',
      tags: ['débutant', 'deck building', 'guide'],
      category: 'Guide',
      created_at: "2024-12-15T10:00:00Z",
      updated_at: "2024-12-15T10:00:00Z",
      published_at: "2024-12-15T10:00:00Z",
      meta_description: "Guide complet pour construire votre premier deck Altered TCG avec tous les conseils essentiels.",
      meta_keywords: "altered tcg, deck building, guide débutant, faction"
    },
    {
      id: 2,
      title: "Analyse des nouvelles cartes : Set Murmures du Labyrinthe",
      slug: "analyse-nouvelles-cartes-murmures-labyrinthe",
      content: `
        <h2>Vue d'ensemble du set</h2>
        <p>Le set "Murmures du Labyrinthe" apporte 180 nouvelles cartes qui révolutionnent le meta actuel d'Altered.</p>
        
        <h2>Les cartes stars du set</h2>
        <h3>Echo du Labyrinthe</h3>
        <p>Cette carte unique d'Axiom permet de copier n'importe quel sort joué ce tour. Son potentiel de combo est énorme.</p>
        
        <h3>Gardien Ancestral</h3>
        <p>Un permanent Ordis avec 6/8 en stats qui protège tous vos autres permanents. Une carte défensive majeure.</p>
        
        <h3>Lame Chaotique</h3>
        <p>Yzmir reçoit une arme imprévisible qui change d'effet à chaque tour. Risqué mais potentiellement dévastateur.</p>
        
        <h2>Impact sur le meta</h2>
        <p>Ces nouvelles cartes ralentissent le meta et favorisent les stratégies de contrôle. Les decks aggro devront s'adapter.</p>
        
        <h2>Recommandations d'achat</h2>
        <p>Les cartes à surveiller en priorité pour vos investissements :</p>
        <ul>
          <li>Echo du Labyrinthe (Unique) - 45-60€</li>
          <li>Gardien Ancestral (Rare) - 8-12€</li>
          <li>Série des "Murmures" (Communes) - 1-2€</li>
        </ul>
      `,
      excerpt: "Plongez dans l'analyse détaillée des nouvelles cartes du set Murmures du Labyrinthe et leur impact sur le meta.",
      author: "Julien",
      featured_image: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=400&fit=crop",
      reading_time: 12,
      views: 892,
      status: 'published',
      tags: ['analyse', 'nouvelles cartes', 'meta'],
      category: 'Analyse',
      created_at: "2024-12-14T14:30:00Z",
      updated_at: "2024-12-14T14:30:00Z",
      published_at: "2024-12-14T14:30:00Z",
      meta_description: "Analyse complète des nouvelles cartes du set Murmures du Labyrinthe d'Altered TCG.",
      meta_keywords: "altered, murmures labyrinthe, nouvelles cartes, analyse meta"
    },
    {
      id: 3,
      title: "Stratégies avancées : Maîtriser les combos Muna",
      slug: "strategies-avancees-maitriser-combos-muna",
      content: `
        <h2>Introduction aux combos Muna</h2>
        <p>Muna est une faction axée sur la manipulation et les interactions complexes. Maîtriser ses combos demande de la pratique.</p>
        
        <h2>Combo #1 : Boucle Infinie de Résonance</h2>
        <p>Ce combo utilise :</p>
        <ul>
          <li>Cristal de Résonance (2 exemplaires)</li>
          <li>Amplificateur Muna</li>
          <li>Echo Mystique</li>
        </ul>
        <p>L'objectif est de créer une boucle qui génère des manas infinis au tour 6.</p>
        
        <h2>Combo #2 : Vol de Victoire</h2>
        <p>Plus risqué mais dévastateur, ce combo vole la condition de victoire adverse :</p>
        <ul>
          <li>Miroir de l'Âme</li>
          <li>Inversion Temporelle</li>
          <li>Sceau du Destin</li>
        </ul>
        
        <h2>Timing et protection</h2>
        <p>Ces combos nécessitent une protection adéquate. Gardez toujours des contre-sorts en réserve.</p>
        
        <h2>Conseils pour l'exécution</h2>
        <ol>
          <li>Préparez votre main à l'avance</li>
          <li>Attendez le bon timing</li>
          <li>Ayez un plan de secours</li>
          <li>Pratiquez en solo avant les tournois</li>
        </ol>
      `,
      excerpt: "Découvrez les combos les plus puissants de la faction Muna et apprenez à les exécuter avec précision.",
      author: "Sarah",
      featured_image: "https://images.unsplash.com/photo-1551269901-5c5e14c25df7?w=800&h=400&fit=crop",
      reading_time: 15,
      views: 634,
      status: 'published',
      tags: ['stratégie', 'combo', 'muna', 'avancé'],
      category: 'Stratégie',
      created_at: "2024-12-13T16:45:00Z",
      updated_at: "2024-12-13T17:00:00Z",
      published_at: "2024-12-13T16:45:00Z",
      meta_description: "Guide avancé des combos Muna dans Altered TCG pour les joueurs expérimentés.",
      meta_keywords: "muna, combo, stratégie avancée, altered tcg"
    },
    {
      id: 4,
      title: "Économie du marché : Investir dans les cartes Altered",
      slug: "economie-marche-investir-cartes-altered",
      content: `
        <h2>Introduction à l'investissement dans Altered</h2>
        <p>Le marché des cartes Altered présente des opportunités intéressantes pour les investisseurs avisés.</p>
        
        <h2>Types de cartes à surveiller</h2>
        <h3>Les Uniques AAA</h3>
        <p>Ces cartes ultra-rares peuvent atteindre des prix astronomiques. Exemples récents :</p>
        <ul>
          <li>Chronos Primordial - 1200€</li>
          <li>Nexus Éternel - 890€</li>
          <li>Gardien des Origines - 750€</li>
        </ul>
        
        <h3>Les Rares staples</h3>
        <p>Cartes jouées dans de nombreux decks, investissement plus sûr :</p>
        <ul>
          <li>Cristal d'Énergie - 25€</li>
          <li>Sentinelle d'Ordis - 18€</li>
          <li>Lame Dimensionnelle - 22€</li>
        </ul>
        
        <h2>Stratégies d'investissement</h2>
        <h3>Court terme (1-3 mois)</h3>
        <p>Spéculez sur les nouvelles sorties et les changements de meta.</p>
        
        <h3>Long terme (6-12 mois)</h3>
        <p>Investissez dans les cartes iconiques et les formats éternels.</p>
        
        <h2>Outils pour suivre les prix</h2>
        <p>Utilisez AlterTracker pour :</p>
        <ul>
          <li>Alertes de prix personnalisées</li>
          <li>Historique des variations</li>
          <li>Analyse des tendances</li>
          <li>Comparaison entre vendeurs</li>
        </ul>
        
        <h2>Risques à considérer</h2>
        <ul>
          <li>Réimpressions possibles</li>
          <li>Changements de meta</li>
          <li>Nouvelles cartes similaires</li>
          <li>Évolution du format</li>
        </ul>
      `,
      excerpt: "Analyse complète du marché des cartes Altered avec des conseils d'investissement pour maximiser vos profits.",
      author: "Marc",
      featured_image: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=400&fit=crop",
      reading_time: 10,
      views: 1156,
      status: 'published',
      tags: ['économie', 'investissement', 'marché'],
      category: 'Économie',
      created_at: "2024-12-12T09:15:00Z",
      updated_at: "2024-12-12T09:15:00Z",
      published_at: "2024-12-12T09:15:00Z",
      meta_description: "Guide complet pour investir dans les cartes Altered TCG et maximiser vos profits.",
      meta_keywords: "altered, investissement, marché cartes, économie tcg"
    },
    {
      id: 5,
      title: "Tournoi du Weekend : Résultats et decks gagnants",
      slug: "tournoi-weekend-resultats-decks-gagnants",
      content: `
        <h2>Résumé du tournoi</h2>
        <p>Le tournoi du weekend a rassemblé 128 joueurs dans un format Standard. Voici les résultats marquants.</p>
        
        <h2>Top 8 final</h2>
        <ol>
          <li><strong>1er - Alexandre (Ordis Control)</strong></li>
          <li>2ème - Léa (Bravos Aggro)</li>
          <li>3ème - Thomas (Muna Combo)</li>
          <li>4ème - Julie (Axiom Midrange)</li>
          <li>5ème - Pierre (Lyra Tokens)</li>
          <li>6ème - Sophie (Yzmir Chaos)</li>
          <li>7ème - Kevin (Ordis Control)</li>
          <li>8ème - Emma (Bravos Burn)</li>
        </ol>
        
        <h2>Deck gagnant : Ordis Control</h2>
        <p>Le deck d'Alexandre mise sur le contrôle total de la partie :</p>
        
        <h3>Liste de cartes</h3>
        <p><strong>Héros :</strong> Gardien Suprême d'Ordis</p>
        
        <p><strong>Créatures (16) :</strong></p>
        <ul>
          <li>4x Sentinelle de Garde</li>
          <li>3x Protecteur Ordis</li>
          <li>3x Gardien du Nexus</li>
          <li>3x Titan de Métal</li>
          <li>3x Archiviste Ancien</li>
        </ul>
        
        <p><strong>Sorts (20) :</strong></p>
        <ul>
          <li>4x Bouclier Mystique</li>
          <li>4x Contre-sort</li>
          <li>3x Bannissement</li>
          <li>3x Résonance Cristalline</li>
          <li>3x Méditation Profonde</li>
          <li>3x Pluie de Météores</li>
        </ul>
        
        <p><strong>Artefacts (4) :</strong></p>
        <ul>
          <li>2x Cristal d'Énergie</li>
          <li>2x Orbe de Pouvoir</li>
        </ul>
        
        <h2>Métagame observé</h2>
        <p>Répartition des archétypes dans le top 32 :</p>
        <ul>
          <li>Ordis Control : 28%</li>
          <li>Bravos Aggro : 22%</li>
          <li>Muna Combo : 16%</li>
          <li>Axiom Midrange : 15%</li>
          <li>Autres : 19%</li>
        </ul>
      `,
      excerpt: "Découvrez les résultats du tournoi du weekend avec l'analyse du deck Ordis Control qui a dominé la compétition.",
      author: "Julien",
      featured_image: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=400&fit=crop",
      reading_time: 7,
      views: 567,
      status: 'published',
      tags: ['tournoi', 'compétitif', 'résultats'],
      category: 'Actualité',
      created_at: "2024-12-11T18:00:00Z",
      updated_at: "2024-12-11T18:00:00Z",
      published_at: "2024-12-11T18:00:00Z",
      meta_description: "Résultats complets du tournoi Altered du weekend avec l'analyse des decks gagnants.",
      meta_keywords: "tournoi altered, ordis control, compétitif, résultats"
    },
    {
      id: 6,
      title: "Tutoriel : Comment utiliser efficacement AlterTracker",
      slug: "tutoriel-comment-utiliser-efficacement-altertracker",
      content: `
        <h2>Introduction à AlterTracker</h2>
        <p>AlterTracker est votre allié indispensable pour naviguer dans l'univers d'Altered TCG. Ce guide vous explique comment tirer le meilleur parti de toutes ses fonctionnalités.</p>
        
        <h2>Créer votre compte</h2>
        <p>La première étape est de créer un compte gratuit. Cela vous donne accès à :</p>
        <ul>
          <li>Sauvegarde de vos recherches</li>
          <li>Alertes de prix personnalisées</li>
          <li>Gestion de votre collection</li>
          <li>Système de messagerie</li>
        </ul>
        
        <h2>Maîtriser la recherche avancée</h2>
        <h3>Filtres de base</h3>
        <ul>
          <li><strong>Nom/Référence :</strong> Recherchez par nom ou code ALT_</li>
          <li><strong>Faction :</strong> Filtrez par couleur</li>
          <li><strong>Rareté :</strong> Commun, Rare, Unique</li>
          <li><strong>Set :</strong> Choisissez l'extension</li>
        </ul>
        
        <h3>Filtres avancés</h3>
        <ul>
          <li><strong>Coût de mana :</strong> Définissez une fourchette</li>
          <li><strong>Statistiques :</strong> Force, PV, etc.</li>
          <li><strong>Effets :</strong> Recherchez par mots-clés</li>
          <li><strong>Prix :</strong> Fourchette de prix</li>
        </ul>
        
        <h2>Configurer vos alertes</h2>
        <p>Les alertes vous préviennent quand :</p>
        <ol>
          <li>Une carte atteint un prix cible</li>
          <li>De nouvelles cartes correspondent à vos critères</li>
          <li>Des offres intéressantes apparaissent</li>
        </ol>
        
        <h3>Connecter Discord</h3>
        <p>Pour recevoir vos alertes instantanément :</p>
        <ol>
          <li>Rejoignez le serveur Discord AlterTracker</li>
          <li>Liez votre compte dans vos paramètres</li>
          <li>Autorisez les messages privés</li>
        </ol>
        
        <h2>Gérer votre collection</h2>
        <p>Importez votre collection via :</p>
        <ul>
          <li>Extension Chrome/Firefox</li>
          <li>Import manuel</li>
          <li>Scan de cartes (bientôt disponible)</li>
        </ul>
        
        <h2>Utiliser le Live Market</h2>
        <p>Le Live Market vous permet de :</p>
        <ul>
          <li>Voir les prix en temps réel</li>
          <li>Comparer les vendeurs</li>
          <li>Détecter les bonnes affaires</li>
          <li>Suivre l'historique des prix</li>
        </ul>
        
        <h2>Conseils et astuces</h2>
        <ul>
          <li>Sauvegardez vos recherches fréquentes</li>
          <li>Utilisez les groupements pour organiser vos résultats</li>
          <li>Définissez des alertes réalistes</li>
          <li>Consultez régulièrement vos statistiques</li>
        </ul>
      `,
      excerpt: "Guide complet pour maîtriser toutes les fonctionnalités d'AlterTracker et optimiser votre expérience de jeu.",
      author: "Sarah",
      reading_time: 12,
      views: 2341,
      status: 'published',
      tags: ['tutoriel', 'altertracker', 'guide'],
      category: 'Guide',
      created_at: "2024-12-10T11:30:00Z",
      updated_at: "2024-12-15T14:20:00Z",
      published_at: "2024-12-10T11:30:00Z",
      meta_description: "Tutoriel complet pour utiliser efficacement AlterTracker et toutes ses fonctionnalités.",
      meta_keywords: "altertracker, tutoriel, guide utilisation, altered tcg"
    }
  ];

  constructor() { }

  // Récupérer tous les articles publiés (version simplifiée pour la liste)
  getPublishedArticles(): Observable<ArticleListModel[]> {
    const articleList: ArticleListModel[] = this.mockArticles.map(article => ({
      id: article.id,
      title: article.title,
      slug: article.slug,
      excerpt: article.excerpt,
      author: article.author,
      featured_image: article.featured_image,
      reading_time: article.reading_time,
      views: article.views,
      category: article.category,
      tags: article.tags,
      published_at: article.published_at || article.created_at
    }));

    return of(articleList).pipe(delay(800)); // Simule un délai réseau
  }

  // Récupérer un article par son slug
  getArticleBySlug(slug: string): Observable<ArticleModel> {
    const article = this.mockArticles.find(a => a.slug === slug);
    if (!article) {
      throw new Error('Article not found');
    }
    return of(article).pipe(delay(600));
  }

  // Récupérer un article par son ID
  getArticleById(id: number): Observable<ArticleModel> {
    const article = this.mockArticles.find(a => a.id === id);
    if (!article) {
      throw new Error('Article not found');
    }
    return of(article).pipe(delay(600));
  }

  // Récupérer les articles par catégorie
  getArticlesByCategory(category: string): Observable<ArticleListModel[]> {
    const filtered = this.mockArticles
      .filter(article => article.category.toLowerCase() === category.toLowerCase())
      .map(article => ({
        id: article.id,
        title: article.title,
        slug: article.slug,
        excerpt: article.excerpt,
        author: article.author,
        featured_image: article.featured_image,
        reading_time: article.reading_time,
        views: article.views,
        category: article.category,
        tags: article.tags,
        published_at: article.published_at || article.created_at
      }));

    return of(filtered).pipe(delay(400));
  }

  // Récupérer les articles par tag
  getArticlesByTag(tag: string): Observable<ArticleListModel[]> {
    const filtered = this.mockArticles
      .filter(article => article.tags.some(t => t.toLowerCase().includes(tag.toLowerCase())))
      .map(article => ({
        id: article.id,
        title: article.title,
        slug: article.slug,
        excerpt: article.excerpt,
        author: article.author,
        featured_image: article.featured_image,
        reading_time: article.reading_time,
        views: article.views,
        category: article.category,
        tags: article.tags,
        published_at: article.published_at || article.created_at
      }));

    return of(filtered).pipe(delay(400));
  }

  // Incrémenter les vues
  incrementViews(id: number): Observable<void> {
    const article = this.mockArticles.find(a => a.id === id);
    if (article) {
      article.views++;
    }
    return of(void 0).pipe(delay(100));
  }

  // Rechercher des articles
  searchArticles(query: string): Observable<ArticleListModel[]> {
    const lowerQuery = query.toLowerCase();
    const filtered = this.mockArticles
      .filter(article =>
        article.title.toLowerCase().includes(lowerQuery) ||
        article.excerpt.toLowerCase().includes(lowerQuery) ||
        article.tags.some(tag => tag.toLowerCase().includes(lowerQuery)) ||
        article.category.toLowerCase().includes(lowerQuery)
      )
      .map(article => ({
        id: article.id,
        title: article.title,
        slug: article.slug,
        excerpt: article.excerpt,
        author: article.author,
        featured_image: article.featured_image,
        reading_time: article.reading_time,
        views: article.views,
        category: article.category,
        tags: article.tags,
        published_at: article.published_at || article.created_at
      }));

    return of(filtered).pipe(delay(500));
  }
}