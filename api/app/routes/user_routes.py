from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import (
    get_user_search_service,
    save_user_search_service,
    delete_user_search_service,
    get_user_count_data
)

user_bp = Blueprint('user', __name__)

@user_bp.route('/count', methods=['GET'])
def count_cards_route():
    try:
        count = get_user_count_data()
        return jsonify({'count': count}), 200
    except Exception as e:
        return make_response(jsonify({'message': 'An error occurred: ' + str(e)}), 500)

@user_bp.route('/searches', methods=['GET'])
@jwt_required()
def get_user_searches():
    try:
        id_user = get_jwt_identity()
        searches = get_user_search_service(id_user)
        if not searches:
            return make_response(jsonify({'message': 'Aucune recherche trouvée'}), 404)
        return jsonify(searches), 200
    except Exception as e:
        return make_response(jsonify({'message': f'Une erreur est survenue : {str(e)}'}), 500)

@user_bp.route('/searches', methods=['POST'])
@jwt_required()
def save_user_search_route():
    try:
        id_user = get_jwt_identity()  # Récupère l'ID utilisateur depuis le token JWT
        data = request.get_json()
        data['id_user'] = id_user  # Associe la recherche à l'utilisateur connecté
        saved_search = save_user_search_service(data)
        return jsonify(saved_search), 201
    except Exception as e:
        return make_response(jsonify({'message': f'Une erreur est survenue : {str(e)}'}), 500)

@user_bp.route('/searches/<int:id_search>', methods=['DELETE'])
@jwt_required()
def delete_user_search_route(id_search: int):
    try:
        id_user = get_jwt_identity()  # Récupère l'ID utilisateur depuis le token JWT
        # Vérifie si la recherche appartient à l'utilisateur connecté
        searches = get_user_search_service(id_user)
        if not any(search['id'] == id_search for search in searches):
            return make_response(jsonify({'message': 'Recherche non autorisée ou inexistante'}), 403)
        delete_user_search_service(id_search)
        return jsonify({'message': 'Recherche supprimée avec succès'}), 200
    except Exception as e:
        return make_response(jsonify({'message': f'Une erreur est survenue : {str(e)}'}), 500)