import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { MarkdownComponent } from 'ngx-markdown';
import { Subject, takeUntil } from 'rxjs';
import { ArticleService } from '../../03_business/article.service';
import { AuthViewService } from '../../authentication/auth-view.service';

@Component({
  selector: 'app-article-edit',
  templateUrl: './article-edit.component.html',
  styleUrls: ['./article-edit.component.css'],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    TranslateModule,
    RouterModule,
    MarkdownComponent
  ]
})
export class ArticleEditComponent implements OnInit, OnDestroy {
  articleForm!: FormGroup;
  isLoading = false;
  isEditMode = false;
  articleId: number | null = null;
  previewMode = false;
  categories: string[] = [];
  availableTags: string[] = [];
  private destroy$ = new Subject<void>();

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private articleService: ArticleService,
    private authViewService: AuthViewService
  ) {
    this.initForm();
  }

  ngOnInit(): void {
    // Vérifier les permissions admin
    if (!this.authViewService.isAdmin()) {
      this.router.navigate(['/articles']);
      return;
    }

    this.loadFormData();

    this.route.params
      .pipe(takeUntil(this.destroy$))
      .subscribe(params => {
        if (params['id']) {
          this.articleId = parseInt(params['id']);
          this.isEditMode = true;
          this.loadArticle();
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private initForm(): void {
    this.articleForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      slug: ['', [Validators.required]],
      content: ['', [Validators.required]],
      excerpt: ['', [Validators.required, Validators.maxLength(500)]],
      author: [this.authViewService.getUsername(), [Validators.required]],
      featured_image: [''],
      reading_time: [1, [Validators.required, Validators.min(1)]],
      status: ['draft', [Validators.required]],
      tags: [[]],
      category: ['', [Validators.required]],
      meta_description: [''],
      meta_keywords: ['']
    });

    // Auto-générer le slug à partir du titre
    this.articleForm.get('title')?.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(title => {
        if (title && !this.isEditMode) {
          const slug = this.articleService.generateSlug(title);
          this.articleForm.patchValue({ slug }, { emitEvent: false });
        }
      });
  }

  private loadFormData(): void {
    // Charger les catégories et tags existants
    this.articleService.getCategories$().subscribe(categories => {
      this.categories = categories;
    });

    this.articleService.getTags$().subscribe(tags => {
      this.availableTags = tags;
    });
  }

  private loadArticle(): void {
    if (!this.articleId) return;

    this.isLoading = true;
    this.articleService.getArticleById$(this.articleId).subscribe({
      next: (article) => {
        this.articleForm.patchValue({
          title: article.title,
          slug: article.slug,
          content: article.content,
          excerpt: article.excerpt,
          author: article.author,
          featured_image: article.featured_image,
          reading_time: article.reading_time,
          status: article.status,
          tags: article.tags,
          category: article.category,
          meta_description: article.meta_description,
          meta_keywords: article.meta_keywords
        });
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading article:', error);
        this.isLoading = false;
        this.router.navigate(['/articles']);
      }
    });
  }

  onSubmit(): void {
    if (this.articleForm.invalid) {
      this.markFormGroupTouched();
      return;
    }

    this.isLoading = true;
    const formData = this.articleForm.value;

    if (this.isEditMode && this.articleId) {
      this.articleService.updateArticle$(this.articleId, formData).subscribe({
        next: (article) => {
          this.router.navigate(['/article', article.slug]);
        },
        error: (error) => {
          console.error('Error updating article:', error);
          this.isLoading = false;
        }
      });
    } else {
      this.articleService.createArticle$(formData).subscribe({
        next: (article) => {
          this.router.navigate(['/article', article.slug]);
        },
        error: (error) => {
          console.error('Error creating article:', error);
          this.isLoading = false;
        }
      });
    }
  }

  onDelete(): void {
    if (!this.isEditMode || !this.articleId) return;

    if (confirm('Êtes-vous sûr de vouloir supprimer cet article ?')) {
      this.articleService.deleteArticle$(this.articleId).subscribe({
        next: () => {
          this.router.navigate(['/articles']);
        },
        error: (error) => {
          console.error('Error deleting article:', error);
        }
      });
    }
  }

  togglePreview(): void {
    this.previewMode = !this.previewMode;
  }

  addTag(event: any): void {
    const input = event.target;
    const tag = input.value.trim();

    if (tag && !this.getCurrentTags().includes(tag)) {
      const currentTags = this.getCurrentTags();
      currentTags.push(tag);
      this.articleForm.patchValue({ tags: currentTags });
      input.value = '';
    }
  }

  removeTag(tagToRemove: string): void {
    const currentTags = this.getCurrentTags().filter(tag => tag !== tagToRemove);
    this.articleForm.patchValue({ tags: currentTags });
  }

  getCurrentTags(): string[] {
    return this.articleForm.get('tags')?.value || [];
  }

  private markFormGroupTouched(): void {
    Object.keys(this.articleForm.controls).forEach(key => {
      const control = this.articleForm.get(key);
      control?.markAsTouched();
    });
  }

  getFieldError(fieldName: string): string {
    const field = this.articleForm.get(fieldName);
    if (field?.errors && field.touched) {
      if (field.errors['required']) return `${fieldName} est requis`;
      if (field.errors['minlength']) return `${fieldName} trop court`;
      if (field.errors['maxlength']) return `${fieldName} trop long`;
      if (field.errors['min']) return `${fieldName} doit être supérieur à 0`;
    }
    return '';
  }
}