import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ArticleListModel } from '../01_models/03_business/article.model';
import { ArticleService } from '../03_business/article.service';
import { AuthViewService } from '../authentication/auth-view.service';

@Component({
  selector: 'app-articles',
  templateUrl: './articles.component.html',
  styleUrls: ['./articles.component.css'],
  imports: [
    CommonModule,
    TranslateModule,
    RouterModule,
    FormsModule
  ]
})
export class ArticlesComponent implements OnInit {
  articles: ArticleListModel[] = [];
  filteredArticles: ArticleListModel[] = [];
  isLoading = true;
  searchQuery = '';
  selectedCategory = '';
  selectedTag = '';
  categories: string[] = [];
  tags: string[] = [];

  constructor(
    private articleService: ArticleService,
    public authViewService: AuthViewService) { }

  ngOnInit(): void {
    this.loadArticles();
  }

  loadArticles(): void {
    this.isLoading = true;

    const request = this.authViewService.isPublisher()
      ? this.articleService.getAllArticles$()
      : this.articleService.getPublishedArticles$();

    request.subscribe({
      next: (articles) => {
        this.articles = articles;
        this.filteredArticles = articles;
        this.extractCategoriesAndTags();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading articles:', error);
        this.isLoading = false;
      }
    });
  }

  onSearch(): void {
    if (this.searchQuery.trim()) {
      this.articleService.searchArticles$(this.searchQuery).subscribe({
        next: (results) => {
          this.filteredArticles = results;
        },
        error: (error) => {
          console.error('Error searching articles:', error);
        }
      });
    } else {
      this.applyFilters();
    }
  }

  onCategoryChange(): void {
    this.applyFilters();
  }

  onTagChange(): void {
    this.applyFilters();
  }

  clearFilters(): void {
    this.searchQuery = '';
    this.selectedCategory = '';
    this.selectedTag = '';
    this.filteredArticles = [...this.articles];
  }

  getReadingTimeText(minutes: number): string {
    return minutes === 1 ? '1 min' : `${minutes} mins`;
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  getStatusConfig(status: string): { label: string, class: string, icon: string } {
    switch (status) {
      case 'published':
        return { label: 'Publié', class: 'bg-green-600 text-white', icon: 'fas fa-check-circle' };
      case 'draft':
        return { label: 'Brouillon', class: 'bg-yellow-600 text-white', icon: 'fas fa-edit' };
      case 'archived':
        return { label: 'Archivé', class: 'bg-gray-600 text-white', icon: 'fas fa-archive' };
      default:
        return { label: 'Inconnu', class: 'bg-red-600 text-white', icon: 'fas fa-question-circle' };
    }
  }

  private extractCategoriesAndTags(): void {
    this.categories = [...new Set(this.articles.map(article => article.category))];
    this.tags = [...new Set(this.articles.flatMap(article => article.tags))];
  }

  private applyFilters(): void {
    let filtered = [...this.articles];

    if (this.selectedCategory) {
      filtered = filtered.filter(article => article.category === this.selectedCategory);
    }

    if (this.selectedTag) {
      filtered = filtered.filter(article => article.tags.includes(this.selectedTag));
    }

    this.filteredArticles = filtered;
  }
}