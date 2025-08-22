export interface ArticleModel {
  id: number;
  title: string;
  slug: string;
  content: string;
  excerpt: string;
  author: string;
  featured_image?: string;
  reading_time: number; // en minutes
  views: number;
  status: 'draft' | 'published' | 'archived';
  tags: string[];
  category: string;
  created_at: string;
  updated_at: string;
  published_at?: string;
  meta_description?: string;
  meta_keywords?: string;
}

export interface ArticleListModel {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  author: string;
  featured_image?: string;
  reading_time: number;
  views: number;
  status: 'draft' | 'published' | 'archived';
  category: string;
  tags: string[];
  published_at: string;
}