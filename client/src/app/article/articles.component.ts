import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ArticleListModel } from '../01_models/03_business/article.model';
import { ArticleService } from '../03_business/article.service';

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

  constructor(private articleService: ArticleService) { }

  ngOnInit(): void {
    this.loadArticles();
  }

  loadArticles(): void {
    this.isLoading = true;
    this.articleService.getPublishedArticles$().subscribe({
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

  private extractCategoriesAndTags(): void {
    this.categories = [...new Set(this.articles.map(article => article.category))];
    this.tags = [...new Set(this.articles.flatMap(article => article.tags))];
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
}