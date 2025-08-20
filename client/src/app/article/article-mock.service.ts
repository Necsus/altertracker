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
      title: "Guide de rédaction d'articles",
      slug: "guide-markdown",
      excerpt: "Apprenez à rédiger des articles avec Markdown pour AlterTracker. Guide complet des syntaxes et bonnes pratiques.",
      author: "Équipe AlterTracker",
      featured_image: "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&h=400&fit=crop",
      reading_time: 5,
      views: 42,
      status: 'published',
      tags: ['guide', 'markdown', 'rédaction'],
      category: 'Guide',
      created_at: "2025-08-19T10:00:00Z",
      updated_at: "2025-08-19T10:00:00Z",
      published_at: "2025-08-19T10:00:00Z",
      meta_description: "Guide complet pour rédiger des articles avec Markdown sur AlterTracker.",
      meta_keywords: "markdown, guide, rédaction, articles, altertracker"
    },
    {
      id: 2,
      title: "Découvrez 39cards.com : l'outil incontournable pour suivre les tournois Altered TCG",
      slug: "promotion-39cards",
      excerpt: "Découvrez 39cards.com, la référence pour suivre les résultats de tournois Altered TCG en temps réel. Un complément idéal à AlterTracker.",
      author: "Équipe AlterTracker",
      featured_image: "https://39cards.com/assets/logo-header.png",
      reading_time: 7,
      views: 124,
      status: 'draft',
      tags: ['tournois', '39cards', 'compétition', 'communauté'],
      category: 'Partenaires',
      created_at: "2025-08-19T14:30:00Z",
      updated_at: "2025-08-19T14:30:00Z",
      published_at: "2025-08-19T14:30:00Z",
      meta_description: "39cards.com est la référence pour suivre les tournois Altered TCG. Découvrez comment ce site complète parfaitement AlterTracker.",
      meta_keywords: "39cards, tournois, altered tcg, compétition, résultats, altertracker, partenaires"
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
    const metadata = this.mockArticlesMetadata.find(a => a.slug === slug);
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