import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { ArticleListModel, ArticleModel } from '../01_models/03_business/article.model';
import { ArticleMockService } from '../article/article-mock.service';

@Injectable({
  providedIn: 'root'
})
export class ArticleService {
  private apiUrl = `${environment.api_url}/articles`;
  private useMock = true; // Changez à false quand l'API sera prête

  constructor(
    private http: HttpClient,
    private mockService: ArticleMockService
  ) { }

  // Récupérer tous les articles publiés
  getPublishedArticles(): Observable<ArticleListModel[]> {
    if (this.useMock) {
      return this.mockService.getPublishedArticles();
    }
    return this.http.get<ArticleListModel[]>(`${this.apiUrl}/published`);
  }

  // Récupérer un article par son slug
  getArticleBySlug(slug: string): Observable<ArticleModel> {
    if (this.useMock) {
      return this.mockService.getArticleBySlug(slug);
    }
    return this.http.get<ArticleModel>(`${this.apiUrl}/slug/${slug}`);
  }

  // Récupérer un article par son ID
  getArticleById(id: number): Observable<ArticleModel> {
    if (this.useMock) {
      return this.mockService.getArticleById(id);
    }
    return this.http.get<ArticleModel>(`${this.apiUrl}/${id}`);
  }

  // Récupérer les articles par catégorie
  getArticlesByCategory(category: string): Observable<ArticleListModel[]> {
    if (this.useMock) {
      return this.mockService.getArticlesByCategory(category);
    }
    return this.http.get<ArticleListModel[]>(`${this.apiUrl}/category/${category}`);
  }

  // Récupérer les articles par tag
  getArticlesByTag(tag: string): Observable<ArticleListModel[]> {
    if (this.useMock) {
      return this.mockService.getArticlesByTag(tag);
    }
    return this.http.get<ArticleListModel[]>(`${this.apiUrl}/tag/${tag}`);
  }

  // Incrémenter les vues
  incrementViews(id: number): Observable<void> {
    if (this.useMock) {
      return this.mockService.incrementViews(id);
    }
    return this.http.post<void>(`${this.apiUrl}/${id}/view`, {});
  }

  // Rechercher des articles
  searchArticles(query: string): Observable<ArticleListModel[]> {
    if (this.useMock) {
      return this.mockService.searchArticles(query);
    }
    return this.http.get<ArticleListModel[]>(`${this.apiUrl}/search?q=${encodeURIComponent(query)}`);
  }
}