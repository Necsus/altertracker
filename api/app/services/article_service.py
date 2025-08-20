from app.data.article_data import (
    get_published_articles_data,
    get_article_by_slug_data,
    get_article_by_id_data,
    get_articles_by_category_data,
    get_articles_by_tag_data,
    search_articles_data,
    increment_article_views_data,
    get_all_categories_data,
    get_all_tags_data,
    create_article_data,
    update_article_data,
    delete_article_data
)
from typing import List, Optional

def get_published_articles_service() -> List[dict]:
    """Service pour récupérer tous les articles publiés"""
    articles = get_published_articles_data()
    return [article.json_list() for article in articles]

def get_article_by_slug_service(slug: str) -> Optional[dict]:
    """Service pour récupérer un article par son slug"""
    article = get_article_by_slug_data(slug)
    return article.json() if article else None

def get_article_by_id_service(article_id: int) -> Optional[dict]:
    """Service pour récupérer un article par son ID"""
    article = get_article_by_id_data(article_id)
    return article.json() if article else None

def get_articles_by_category_service(category: str) -> List[dict]:
    """Service pour récupérer les articles d'une catégorie"""
    articles = get_articles_by_category_data(category)
    return [article.json_list() for article in articles]

def get_articles_by_tag_service(tag: str) -> List[dict]:
    """Service pour récupérer les articles contenant un tag"""
    articles = get_articles_by_tag_data(tag)
    return [article.json_list() for article in articles]

def search_articles_service(query: str) -> List[dict]:
    """Service pour rechercher dans les articles"""
    articles = search_articles_data(query)
    return [article.json_list() for article in articles]

def increment_article_views_service(article_id: int) -> None:
    """Service pour incrémenter les vues d'un article"""
    increment_article_views_data(article_id)

def get_all_categories_service() -> List[str]:
    """Service pour récupérer toutes les catégories"""
    return get_all_categories_data()

def get_all_tags_service() -> List[str]:
    """Service pour récupérer tous les tags"""
    return get_all_tags_data()

def create_article_service(article_data: dict) -> dict:
    """Service pour créer un article"""
    article = create_article_data(article_data)
    return article.json()

def update_article_service(article_id: int, article_data: dict) -> Optional[dict]:
    """Service pour mettre à jour un article"""
    article = update_article_data(article_id, article_data)
    return article.json() if article else None

def delete_article_service(article_id: int) -> bool:
    """Service pour supprimer un article"""
    return delete_article_data(article_id)