import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { ArticleListModel, ArticleModel } from '../01_models/03_business/article.model';
import { ArticleApiService } from '../02_api/article-api.service';

@Injectable({
  providedIn: 'root'
})
export class ArticleService {
  constructor(
    private articleApiService: ArticleApiService,
  ) { }

  // Récupérer tous les articles publiés
  getPublishedArticles$(): Observable<ArticleListModel[]> {
    return this.articleApiService.getPublishedArticles$().pipe(
      map((dbModel: ArticleListModel[]) => {
        return dbModel;
      })
    );
  }

  getLastPublishedArticles$(): Observable<ArticleListModel[]> {
    return this.articleApiService.getLastPublishedArticles$().pipe(
      map((dbModel: ArticleListModel[]) => {
        return dbModel;
      })
    );
  }

  // Récupérer un article par son slug
  getArticleBySlug$(slug: string): Observable<ArticleModel> {
    return this.articleApiService.getArticleBySlug$(slug).pipe(
      map((dbModel: ArticleModel) => {
        return dbModel;
      })
    );
  }

  // Récupérer un article par son ID
  getArticleById$(id: number): Observable<ArticleModel> {
    return this.articleApiService.getArticleById$(id).pipe(
      map((dbModel: ArticleModel) => {
        return dbModel;
      })
    );
  }

  // Récupérer les articles par catégorie
  getArticlesByCategory$(category: string): Observable<ArticleListModel[]> {
    return this.articleApiService.getArticlesByCategory$(category).pipe(
      map((dbModel: ArticleListModel[]) => {
        return dbModel;
      })
    );
  }

  // Récupérer les articles par tag
  getArticlesByTag$(tag: string): Observable<ArticleListModel[]> {
    return this.articleApiService.getArticlesByTag$(tag).pipe(
      map((dbModel: ArticleListModel[]) => {
        return dbModel;
      })
    );
  }

  // Incrémenter les vues
  incrementViews$(id: number): Observable<void> {
    return this.articleApiService.incrementViews$(id).pipe(
      map(() => void 0)
    );
  }

  // Rechercher des articles
  searchArticles$(query: string): Observable<ArticleListModel[]> {
    return this.articleApiService.searchArticles$(query).pipe(
      map((dbModel: ArticleListModel[]) => {
        return dbModel;
      })
    );
  }

  // Récupérer les catégories
  getCategories$(): Observable<string[]> {
    return this.articleApiService.getCategories$().pipe(
      map((dbModel: string[]) => {
        return dbModel;
      })
    );
  }

  // Récupérer les tags
  getTags$(): Observable<string[]> {
    return this.articleApiService.getTags$().pipe(
      map((dbModel: string[]) => {
        return dbModel;
      })
    );
  }

  createArticle$(article: Partial<ArticleModel>): Observable<ArticleModel> {
    return this.articleApiService.createArticle$(article).pipe(
      map((dbModel: ArticleModel) => {
        return dbModel;
      })
    );
  }

  updateArticle$(id: number, article: Partial<ArticleModel>): Observable<ArticleModel> {
    return this.articleApiService.updateArticle$(id, article).pipe(
      map((dbModel: ArticleModel) => {
        return dbModel;
      })
    );
  }

  deleteArticle$(id: number): Observable<void> {
    return this.articleApiService.deleteArticle$(id).pipe(
      map(() => void 0)
    );
  }

  // Récupérer tous les articles (y compris drafts) - Admin seulement
  getAllArticles$(): Observable<ArticleListModel[]> {
    return this.articleApiService.getAllArticles$().pipe(
      map((dbModel: ArticleListModel[]) => {
        return dbModel;
      })
    );
  }

  // Générer un slug à partir du titre
  generateSlug(title: string): string {
    return title
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9\s-]/g, '')
      .trim()
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-');
  }

}