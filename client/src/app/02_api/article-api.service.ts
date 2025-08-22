import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ArticleListModel, ArticleModel } from '../01_models/03_business/article.model';
import { WebApiService } from './web-api.service';

@Injectable({
  providedIn: 'root'
})
export class ArticleApiService {

  private controller = 'article';

  constructor(private wabApiService: WebApiService) { }
  // Récupérer tous les articles publiés
  getPublishedArticles$(): Observable<ArticleListModel[]> {
    return this.wabApiService.callGet$(this.controller, 'published');
  }

  getLastPublishedArticles$(): Observable<ArticleListModel[]> {
    return this.wabApiService.callGet$(this.controller, 'lastpublished');
  }

  // Récupérer un article par son slug
  getArticleBySlug$(slug: string): Observable<ArticleModel> {
    return this.wabApiService.callGet$(this.controller, `slug/${slug}`);
  }

  // Récupérer un article par son ID
  getArticleById$(id: number): Observable<ArticleModel> {
    return this.wabApiService.callGet$(this.controller, `${id}`);
  }

  // Récupérer les articles par catégorie
  getArticlesByCategory$(category: string): Observable<ArticleListModel[]> {
    return this.wabApiService.callGet$(this.controller, `category/${category}`);
  }

  // Récupérer les articles par tag
  getArticlesByTag$(tag: string): Observable<ArticleListModel[]> {
    return this.wabApiService.callGet$(this.controller, `tag/${tag}`);
  }

  // Incrémenter les vues
  incrementViews$(id: number): Observable<void> {
    return this.wabApiService.callPost$(this.controller, `${id}/view`);
  }

  // Rechercher des articles
  searchArticles$(query: string): Observable<ArticleListModel[]> {
    return this.wabApiService.callGet$(this.controller, `search?q=${encodeURIComponent(query)}`);
  }

  // Récupérer les catégories
  getCategories$(): Observable<string[]> {
    return this.wabApiService.callGet$(this.controller, 'categories');
  }

  // Récupérer les tags
  getTags$(): Observable<string[]> {
    return this.wabApiService.callGet$(this.controller, 'tags');
  }

  createArticle$(article: Partial<ArticleModel>): Observable<ArticleModel> {
    return this.wabApiService.callPost$(this.controller, '', article);
  }

  updateArticle$(id: number, article: Partial<ArticleModel>): Observable<ArticleModel> {
    return this.wabApiService.callPut$(this.controller, `${id}`, article);
  }

  deleteArticle$(id: number): Observable<void> {
    return this.wabApiService.callDelete$(this.controller, `${id}`);
  }

  getAllArticles$(): Observable<ArticleListModel[]> {
    return this.wabApiService.callGet$(this.controller, 'all');
  }
}
