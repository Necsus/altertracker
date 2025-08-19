import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { delay, map, Observable, of, throwError } from 'rxjs';
import { ArticleListModel, ArticleModel } from '../01_models/03_business/article.model';

@Injectable({
  providedIn: 'root'
})
export class ArticleMockService {

  private mockArticlesMetadata: Omit<ArticleModel, 'content'>[] = [
    {
      id: 1,
      title: "Guide complet : Construire son premier deck Altered",
      slug: "guide-complet-construire-premier-deck-altered",
      excerpt: "Découvrez les bases essentielles pour construire votre premier deck Altered et commencer à jouer avec confiance.",
      author: "Julien Martinez",
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
      excerpt: "Plongez dans l'analyse détaillée des nouvelles cartes du set Murmures du Labyrinthe et leur impact sur le meta.",
      author: "Sarah Chen",
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
      title: "Tutoriel : Comment utiliser efficacement AlterTracker",
      slug: "tutoriel-comment-utiliser-efficacement-altertracker",
      excerpt: "Guide complet pour maîtriser toutes les fonctionnalités d'AlterTracker et optimiser votre expérience de jeu.",
      author: "Marc Dubois",
      featured_image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=400&fit=crop",
      reading_time: 10,
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

  constructor(private http: HttpClient) { }

  getPublishedArticles(): Observable<ArticleListModel[]> {
    const articleList: ArticleListModel[] = this.mockArticlesMetadata
      .filter(article => article.status === 'published')
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
      }))
      .sort((a, b) => new Date(b.published_at).getTime() - new Date(a.published_at).getTime());

    // Délai réduit à 200ms pour la liste
    return of(articleList).pipe(delay(200));
  }

  getArticleBySlug(slug: string): Observable<ArticleModel> {
    const metadata = this.mockArticlesMetadata.find(a => a.slug === slug && a.status === 'published');
    if (!metadata) {
      return throwError(() => new Error('Article not found'));
    }

    // Charge le contenu Markdown depuis le fichier (raw)
    return this.http.get(`assets/articles/${slug}.md`, { responseType: 'text' })
      .pipe(
        map(markdown => ({
          ...metadata,
          content: markdown // On garde le markdown brut !
        } as ArticleModel)),
        delay(300)
      );
  }

  getArticleById(id: number): Observable<ArticleModel> {
    const metadata = this.mockArticlesMetadata.find(a => a.id === id && a.status === 'published');
    if (!metadata) {
      return throwError(() => new Error('Article not found'));
    }

    return this.getArticleBySlug(metadata.slug);
  }

  getArticlesByCategory(category: string): Observable<ArticleListModel[]> {
    const filtered = this.mockArticlesMetadata
      .filter(article =>
        article.category.toLowerCase() === category.toLowerCase() &&
        article.status === 'published'
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

    return of(filtered).pipe(delay(100)); // Très rapide pour les filtres
  }

  getArticlesByTag(tag: string): Observable<ArticleListModel[]> {
    const filtered = this.mockArticlesMetadata
      .filter(article =>
        article.tags.some(t => t.toLowerCase().includes(tag.toLowerCase())) &&
        article.status === 'published'
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

    return of(filtered).pipe(delay(100)); // Très rapide pour les filtres
  }

  incrementViews(id: number): Observable<void> {
    const article = this.mockArticlesMetadata.find(a => a.id === id);
    if (article) {
      article.views++;
    }
    return of(void 0).pipe(delay(50)); // Quasi-instantané
  }

  searchArticles(query: string): Observable<ArticleListModel[]> {
    const lowerQuery = query.toLowerCase();
    const filtered = this.mockArticlesMetadata
      .filter(article =>
        article.status === 'published' && (
          article.title.toLowerCase().includes(lowerQuery) ||
          article.excerpt.toLowerCase().includes(lowerQuery) ||
          article.tags.some(tag => tag.toLowerCase().includes(lowerQuery)) ||
          article.category.toLowerCase().includes(lowerQuery)
        )
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

    return of(filtered).pipe(delay(150)); // Rapide pour la recherche
  }
}