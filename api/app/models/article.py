from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy import Text

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    content = db.Column(Text, nullable=False)
    excerpt = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    featured_image = db.Column(db.String(500), nullable=True)
    reading_time = db.Column(db.Integer, default=0)  # en minutes
    views = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('draft', 'published', 'archived', name='article_status'), default='draft')
    tags = db.Column(db.JSON, nullable=True)  # Liste de tags
    category = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    published_at = db.Column(db.DateTime, nullable=True)
    meta_description = db.Column(db.String(500), nullable=True)
    meta_keywords = db.Column(db.String(500), nullable=True)
    
    def __repr__(self):
        return f'<Article {self.title}>'
    
    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'excerpt': self.excerpt,
            'author': self.author,
            'featured_image': self.featured_image,
            'reading_time': self.reading_time,
            'views': self.views,
            'status': self.status,
            'tags': self.tags or [],
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'meta_description': self.meta_description,
            'meta_keywords': self.meta_keywords
        }
    
    def json_list(self):
        """Version simplifiée pour les listes d'articles"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'author': self.author,
            'featured_image': self.featured_image,
            'reading_time': self.reading_time,
            'views': self.views,
            'category': self.category,
            'tags': self.tags or [],
            'published_at': self.published_at.isoformat() if self.published_at else self.created_at.isoformat()
        }