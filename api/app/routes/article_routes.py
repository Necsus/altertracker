from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.article_service import (
    get_published_articles_service,
    get_article_by_slug_service,
    get_article_by_id_service,
    get_articles_by_category_service,
    get_articles_by_tag_service,
    search_articles_service,
    increment_article_views_service,
    get_all_categories_service,
    get_all_tags_service,
    create_article_service,
    update_article_service,
    delete_article_service
)
from app.decorators.auth_decorator import admin_required

article_bp = Blueprint('articles', __name__)

@article_bp.route('/published', methods=['GET'])
def get_published_articles():
    """Récupère tous les articles publiés"""
    try:
        articles = get_published_articles_service()
        return jsonify(articles), 200
    except Exception as e:
        return make_response(jsonify({'message': f'Erreur : {str(e)}'}), 500)

@article_bp.route('/slug/<string:slug>', methods=['GET'])
def get_article_by_slug(slug: str):
    """Récupère un article par son slug"""
    try:
        article = get_article_by_slug_service(slug)
        if not article:
            return make_response(jsonify({'message': 'Article non trouvé'}), 404)
        return jsonify(article), 200
    except Exception as e:
        return make_response(jsonify({'message': f'Erreur : {str(e)}'}), 500)

@article_bp.route('/<int:article_id>', methods=['GET'])
def get_article_by_id(article_id: int):
    """Récupère un article par son ID"""
    try:
        article = get_article_by_id_service(article_id)
        if not article:
            return make_response(jsonify({'message': 'Article non trouvé'}), 404)
        return jsonify(article), 200
    except Exception as e:
        return make_response(jsonify({'message': f'Erreur : {str(e)}'}), 500)

@article_bp.route('/category/<string:category>', methods=['GET'])
def get_articles_by_category(category: str):
    """Récupère les articles d'une catégorie"""
    try:
        articles = get_articles_by_category_service(category)
        return jsonify(articles), 200
    except Exception as e:
        return make_response(jsonify({'message': f'Erreur : {str(e)}'}), 500)

@article_bp.route('/tag/<string:tag>', methods=['GET'])
def get_articles_by_tag(tag: str):
    """Récupère les articles contenant un tag"""
    try:
        articles = get_articles_by_tag_service(tag)
        return jsonify(articles), 200
    except Exception as e:
        return make_response(jsonify({'message': f'Erreur : {str(e)}'}), 500)

@article_bp.route('/search', methods=['GET'])
def search_articles():
    """Recherche dans les articles"""
    try:
        query = request.args.get('q', '')
        if not query:
            return make_response(jsonify({'message': 'Paramètre de recherche requis'}), 400)
        
        articles = search_articles_service(query)
        return jsonify(articles), 200
    except Exception as e:
        return make_response(jsonify({'message': f'Erreur : {str(e)}'}), 500)

@article_bp.route('/<int:article_id>/view', methods=['POST'])
def increment_views(article_id: int):
    """Incrémente le nombre de vues d'un article"""
    try:
        increment_article_views_service(article_id)
        return jsonify({'message': ''}), 200
    except Exception as e:
        return make_response(jsonify({'message': f'Erreur : {str(e)}'}), 500)

@article_bp.route('/categories', methods=['GET'])
def get_categories():
    """Récupère toutes les catégories"""
    try:
        categories = get_all_categories_service()
        return jsonify(categories), 200
    except Exception as e:
        return make_response(jsonify({'message': f'Erreur : {str(e)}'}), 500)

@article_bp.route('/tags', methods=['GET'])
def get_tags():
    """Récupère tous les tags"""
    try:
        tags = get_all_tags_service()
        return jsonify(tags), 200
    except Exception as e:
        return make_response(jsonify({'message': f'Erreur : {str(e)}'}), 500)

# Routes d'administration (nécessitent les droits admin)
@article_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_article():
    """Crée un nouvel article (admin seulement)"""
    try:
        data = request.get_json()
        article = create_article_service(data)
        return jsonify(article), 201
    except Exception as e:
        return make_response(jsonify({'message': f'Erreur : {str(e)}'}), 500)

@article_bp.route('/<int:article_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_article(article_id: int):
    """Met à jour un article (admin seulement)"""
    try:
        data = request.get_json()
        article = update_article_service(article_id, data)
        if not article:
            return make_response(jsonify({'message': 'Article non trouvé'}), 404)
        return jsonify(article), 200
    except Exception as e:
        return make_response(jsonify({'message': f'Erreur : {str(e)}'}), 500)

@article_bp.route('/<int:article_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_article(article_id: int):
    """Supprime un article (admin seulement)"""
    try:
        success = delete_article_service(article_id)
        if not success:
            return make_response(jsonify({'message': 'Article non trouvé'}), 404)
        return jsonify({'message': 'Article supprimé'}), 200
    except Exception as e:
        return make_response(jsonify({'message': f'Erreur : {str(e)}'}), 500)