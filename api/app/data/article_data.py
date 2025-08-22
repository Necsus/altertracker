from app.extensions import db
from app.models.article import Article
from datetime import datetime, timezone
from sqlalchemy import or_, func
from typing import List, Optional

def get_published_articles_data() -> List[Article]:
    """Récupère tous les articles publiés triés par date de publication"""
    return db.session.query(Article).filter(
        Article.status == 'published'
    ).order_by(
        Article.published_at.desc()
    ).all()

def get_last_published_articles_data() -> List[Article]:
    """Récupère tous les articles publiés triés par date de publication"""
    return db.session.query(Article).filter(
        Article.status == 'published'
    ).order_by(
        Article.published_at.desc()
    ).limit(3).all()

def get_article_by_slug_data(slug: str) -> Optional[Article]:
    """Récupère un article par son slug"""
    return db.session.query(Article).filter(
        Article.slug == slug
    ).first()

def get_article_by_id_data(article_id: int) -> Optional[Article]:
    """Récupère un article par son ID"""
    return db.session.query(Article).filter(
        Article.id == article_id
    ).first()

def get_articles_by_category_data(category: str) -> List[Article]:
    """Récupère les articles d'une catégorie"""
    return db.session.query(Article).filter(
        Article.category == category,
        Article.status == 'published'
    ).order_by(
        Article.published_at.desc()
    ).all()

def get_articles_by_tag_data(tag: str) -> List[Article]:
    """Récupère les articles contenant un tag"""
    return db.session.query(Article).filter(
        Article.tags.contains([tag]),
        Article.status == 'published'
    ).order_by(
        Article.published_at.desc()
    ).all()

def search_articles_data(query: str) -> List[Article]:
    """Recherche dans les articles"""
    search_term = f"%{query}%"
    return db.session.query(Article).filter(
        Article.status == 'published',
        or_(
            Article.title.ilike(search_term),
            Article.excerpt.ilike(search_term),
            Article.content.ilike(search_term),
            Article.category.ilike(search_term)
        )
    ).order_by(
        Article.published_at.desc()
    ).all()

def increment_article_views_data(article_id: int) -> None:
    """Incrémente le nombre de vues d'un article"""
    try:
        db.session.query(Article).filter(
            Article.id == article_id
        ).update({
            Article.views: Article.views + 1
        })
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de l'incrémentation des vues : {e}")

def get_all_categories_data() -> List[str]:
    """Récupère toutes les catégories d'articles"""
    result = db.session.query(Article.category).distinct().all()
    return [cat[0] for cat in result]

def get_all_tags_data() -> List[str]:
    """Récupère tous les tags d'articles"""
    articles = db.session.query(Article.tags).filter(
        Article.tags.isnot(None)
    ).all()
    
    all_tags = set()
    for article in articles:
        if article.tags:
            all_tags.update(article.tags)
    
    return sorted(list(all_tags))

def create_article_data(article_data: dict) -> Article:
    """Crée un nouvel article"""
    try:
        article = Article(
            title=article_data['title'],
            slug=article_data['slug'],
            content=article_data['content'],
            excerpt=article_data['excerpt'],
            author=article_data['author'],
            featured_image=article_data.get('featured_image'),
            reading_time=article_data.get('reading_time', 0),
            category=article_data['category'],
            tags=article_data.get('tags', []),
            status=article_data.get('status', 'draft'),
            meta_description=article_data.get('meta_description'),
            meta_keywords=article_data.get('meta_keywords')
        )
        
        if article_data.get('status') == 'published':
            article.published_at = datetime.now(timezone.utc)
        
        db.session.add(article)
        db.session.commit()
        return article
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Erreur lors de la création de l'article : {str(e)}")

def update_article_data(article_id: int, article_data: dict) -> Optional[Article]:
    """Met à jour un article"""
    try:
        article = db.session.query(Article).filter(Article.id == article_id).first()
        if not article:
            return None
        
        # Mise à jour des champs
        for key, value in article_data.items():
            if hasattr(article, key):
                setattr(article, key, value)
        
        # Si on publie l'article pour la première fois
        if article_data.get('status') == 'published' and not article.published_at:
            article.published_at = datetime.now(timezone.utc)
        
        article.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return article
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Erreur lors de la mise à jour de l'article : {str(e)}")

def delete_article_data(article_id: int) -> bool:
    """Supprime un article"""
    try:
        article = db.session.query(Article).filter(Article.id == article_id).first()
        if not article:
            return False
        
        db.session.delete(article)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Erreur lors de la suppression de l'article : {str(e)}")
    
def get_all_articles_data() -> List[Article]:
    """Récupère tous les articles publiés triés par date de publication"""
    return db.session.query(Article).order_by(
        Article.published_at.desc()
    ).all() 