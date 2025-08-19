import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit, ViewEncapsulation } from '@angular/core';
import { Meta, Title } from '@angular/platform-browser';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { Subject, takeUntil } from 'rxjs';
import { ArticleModel } from '../../01_models/03_business/article.model';
import { ArticleService } from '../../03_business/article.service';

@Component({
  selector: 'app-article',
  templateUrl: './article.component.html',
  styleUrls: ['./article.component.css'],
  encapsulation: ViewEncapsulation.None,
  imports: [
    CommonModule,
    TranslateModule,
    RouterModule
  ]
})
export class ArticleComponent implements OnInit, OnDestroy {
  article: ArticleModel | null = null;
  isLoading = true;
  error: string | null = null;
  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private articleService: ArticleService,
    private titleService: Title,
    private metaService: Meta
  ) { }

  ngOnInit(): void {
    this.route.params
      .pipe(takeUntil(this.destroy$))
      .subscribe(params => {
        const identifier = params['id'];
        this.loadArticle(identifier);
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadArticle(identifier: string): void {
    this.isLoading = true;
    this.error = null;

    // Détermine si c'est un ID numérique ou un slug
    const isNumeric = /^\d+$/.test(identifier);
    const request = isNumeric
      ? this.articleService.getArticleById(parseInt(identifier))
      : this.articleService.getArticleBySlug(identifier);

    request.subscribe({
      next: (article) => {
        this.article = article;
        this.setupSEO();
        this.incrementViews();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading article:', error);
        this.error = 'Article non trouvé';
        this.isLoading = false;
      }
    });
  }

  private setupSEO(): void {
    if (!this.article) return;

    // Titre de la page
    this.titleService.setTitle(`${this.article.title} | AlterTracker`);

    // Meta description
    this.metaService.updateTag({
      name: 'description',
      content: this.article.meta_description || this.article.excerpt
    });

    // Meta keywords
    if (this.article.meta_keywords) {
      this.metaService.updateTag({
        name: 'keywords',
        content: this.article.meta_keywords
      });
    }

    // Open Graph
    this.metaService.updateTag({ property: 'og:title', content: this.article.title });
    this.metaService.updateTag({
      property: 'og:description',
      content: this.article.meta_description || this.article.excerpt
    });

    if (this.article.featured_image) {
      this.metaService.updateTag({
        property: 'og:image',
        content: this.article.featured_image
      });
    }
  }

  private incrementViews(): void {
    if (this.article) {
      this.articleService.incrementViews(this.article.id).subscribe({
        next: () => {
          if (this.article) {
            this.article.views++;
          }
        },
        error: (error) => {
          console.error('Error incrementing views:', error);
        }
      });
    }
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  getReadingTimeText(minutes: number): string {
    return minutes === 1 ? '1 minute de lecture' : `${minutes} minutes de lecture`;
  }

  shareArticle(): void {
    if (navigator.share && this.article) {
      navigator.share({
        title: this.article.title,
        text: this.article.excerpt,
        url: window.location.href
      }).catch(console.error);
    } else {
      // Fallback: copier le lien
      navigator.clipboard.writeText(window.location.href);
    }
  }
}