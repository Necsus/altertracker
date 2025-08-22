import { CommonModule } from '@angular/common';
import { Component, ElementRef, OnDestroy, OnInit, ViewEncapsulation } from '@angular/core';
import { Meta, Title } from '@angular/platform-browser';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { MarkdownComponent } from 'ngx-markdown';
import { Subject, takeUntil } from 'rxjs';
import { ArticleModel } from '../../01_models/03_business/article.model';
import { ArticleService } from '../../03_business/article.service';
import { AuthViewService } from '../../authentication/auth-view.service';

@Component({
  selector: 'app-article',
  templateUrl: './article.component.html',
  styleUrls: ['./article.component.css'],
  encapsulation: ViewEncapsulation.None,
  imports: [
    CommonModule,
    TranslateModule,
    RouterModule,
    MarkdownComponent
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
    private metaService: Meta,
    private elementRef: ElementRef,
    public authViewService: AuthViewService
  ) { }

  ngOnInit(): void {
    this.route.params
      .pipe(takeUntil(this.destroy$))
      .subscribe(params => {
        const identifier = params['id'];
        this.loadArticle(identifier);
      });
  }

  ngAfterViewInit(): void {
    // Configuration des liens après le rendu du contenu
    this.configureExternalLinks();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private configureExternalLinks(): void {
    setTimeout(() => {
      const links = this.elementRef.nativeElement.querySelectorAll('.prose a[href^="http"], .prose a[href^="https"]');

      links.forEach((link: HTMLAnchorElement) => {
        // Ouvrir dans un nouvel onglet
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');

        // Ajouter des classes pour le style
        link.classList.add('external-link');
      });
    }, 500);
  }

  private loadArticle(identifier: string): void {
    this.isLoading = true;
    this.error = null;

    // Détermine si c'est un ID numérique ou un slug
    const isNumeric = /^\d+$/.test(identifier);
    const request = isNumeric
      ? this.articleService.getArticleById$(parseInt(identifier))
      : this.articleService.getArticleBySlug$(identifier);

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
    if (this.article && this.article.status === 'published') {
      this.articleService.incrementViews$(this.article.id).subscribe({
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

  getStatusConfig(status: string): { label: string, class: string, icon: string } {
    switch (status) {
      case 'published':
        return {
          label: 'Publié',
          class: 'bg-green-600 text-white',
          icon: 'fas fa-check-circle'
        };
      case 'draft':
        return {
          label: 'Brouillon',
          class: 'bg-yellow-600 text-white',
          icon: 'fas fa-edit'
        };
      case 'archived':
        return {
          label: 'Archivé',
          class: 'bg-gray-600 text-white',
          icon: 'fas fa-archive'
        };
      default:
        return {
          label: 'Inconnu',
          class: 'bg-red-600 text-white',
          icon: 'fas fa-question-circle'
        };
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