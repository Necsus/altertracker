import sib_api_v3_sdk
from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.security import check_password, hash_password
from app.extensions import mail_api, ApiException, limiter, db
from app.services.user_service import (
    get_user_search_service,
    save_user_search_service,
    delete_user_search_service,
    get_user_count_data,
    get_user_alert_service,
    save_user_alert_service,
    delete_user_alert_service,
    edit_user_alert_service,
    get_user_alert_with_card_service,
    get_user_by_id_service,
    put_user_password_service,
    delete_user_service,
    get_user_by_username_service,
    put_username_service,
    save_user_collections_service,
    get_user_collections_service
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
    
@user_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_user_alerts():
    try:
        user_id = get_jwt_identity()
        alerts = get_user_alert_with_card_service(user_id)
        return jsonify(alerts), 200
    except Exception as e:
        return jsonify({"message": f"Erreur lors de la récupération des alertes : {str(e)}"}), 400


@user_bp.route('/alerts', methods=['POST'])
@jwt_required()
def create_user_alert():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        data["id_user"] = user_id  # Associe l'alerte à l'utilisateur authentifié
        new_alert = save_user_alert_service(data)
        return jsonify(new_alert), 201
    except Exception as e:
        return jsonify({"message": f"Erreur lors de la création de l'alerte : {str(e)}"}), 400


@user_bp.route('/alerts/<int:id_alert>', methods=['DELETE'])
@jwt_required()
def delete_user_alert(id_alert):
    try:
        user_id = get_jwt_identity()
        # Vérifie si l'alerte appartient à l'utilisateur authentifié
        alerts = get_user_alert_service(user_id)
        if not any(alert["id"] == id_alert for alert in alerts):
            return jsonify({"message": "Alerte non trouvée ou non autorisée"}), 403

        delete_user_alert_service(id_alert)
        return jsonify({"code": 200}), 200
    except Exception as e:
        return jsonify({"message": f"Erreur lors de la suppression de l'alerte : {str(e)}"}), 400


@user_bp.route('/alerts', methods=['PUT'])
@jwt_required()
def update_user_alert():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Supprime la clé 'card' si elle est présente
        data.pop('card', None)

        # Vérifie si l'alerte appartient à l'utilisateur authentifié
        alerts = get_user_alert_service(user_id)
        if not any(alert["id"] == data["id"] for alert in alerts):
            return jsonify({"message": "Alerte non trouvée ou non autorisée"}), 403

        updated_alert = edit_user_alert_service(data["id"], data)
        return jsonify(updated_alert), 200
    except Exception as e:
        return jsonify({"message": f"Erreur lors de la mise à jour de l'alerte : {str(e)}"}), 400
    
@user_bp.route('/contact', methods=['POST'])
@jwt_required()
def contact_form():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Vérification des champs requis
        if not data.get('name') or not data.get('email') or not data.get('subject') or not data.get('message'):
            return jsonify({"message": "Tous les champs sont requis"}), 400

        # Envoi d'un email de bienvenue
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": "contact@altertracker.com", "name": "contact"}],
            subject=data.get('subject'),
            html_content= f"{data.get('email')}<br/>{data.get('message')}",
            sender={"name": f"{data.get('name')} id: {user_id}", "email": "noreply@altertracker.com"}
        )
        try:
            response = mail_api.send_transac_email(send_smtp_email)
        except ApiException as e:
            print("Exception lors de l'appel à l’API Sendinblue: %s\n" % e)
        return jsonify({"message": "Votre message a été envoyé avec succès"}), 200
    except Exception as e:
        return jsonify({"message": f"Erreur lors de l'envoi de l'email : {str(e)}"}), 500
    
@user_bp.route('/change-username', methods=['PUT'])
@limiter.limit("3 per minute")  # Limite les requêtes pour éviter les abus
@jwt_required()
def change_username():
    try:
        user_id = get_jwt_identity()  # Récupère l'ID utilisateur depuis le token JWT
        data = request.get_json()

        # Vérification des champs requis
        if not data.get('new_username'):
            return jsonify({"message": "Le champ 'new_username' est requis"}), 400

        new_username = data['new_username']

        # Validation du nouveau username (exemple : longueur minimale et caractères autorisés)
        if len(new_username) < 3 or len(new_username) > 50:
            return jsonify({"message": "Le nom d'utilisateur doit contenir entre 3 et 20 caractères"}), 400
        if not new_username.isalnum():
            return jsonify({"message": "Le nom d'utilisateur ne peut contenir que des lettres et des chiffres"}), 400

        # Vérification de l'unicité du username
        existing_user = get_user_by_username_service(new_username)
        if existing_user:
            return jsonify({"message": "Ce nom d'utilisateur est déjà pris"}), 409

        # Mise à jour du username dans la base de données
        put_username_service(user_id, new_username)

        return jsonify({"message": "Nom d'utilisateur mis à jour avec succès"}), 200

    except Exception as e:
        return jsonify({"message": f"Erreur lors de la mise à jour du nom d'utilisateur : {str(e)}"}), 500
    

@user_bp.route('/change-password', methods=['PUT'])
@limiter.limit("3 per minute")
@jwt_required()
def update_user_password():
    try:
        user_id = get_jwt_identity()  # Récupère l'ID utilisateur depuis le token JWT
        data = request.get_json()

        # Vérification des champs requis
        if not data.get('old_password') or not data.get('new_password'):
            return jsonify({"message": "Les champs 'old_password' et 'new_password' sont requis"}), 400

        # Récupération de l'utilisateur
        user = get_user_by_id_service(user_id)
        if not user:
            return jsonify({"message": "Utilisateur non trouvé"}), 404

        # Vérification de l'ancien mot de passe
        if not check_password(data['old_password'], user['password_hash']):
            return jsonify({"message": "L'ancien mot de passe est incorrect"}), 403

        # Validation du nouveau mot de passe (exemple : longueur minimale)
        if len(data['new_password']) < 8:
            return jsonify({"message": "Le nouveau mot de passe doit contenir au moins 8 caractères"}), 400

        # Hachage du nouveau mot de passe
        hashed_password = hash_password(data['new_password'])

        # Mise à jour du mot de passe dans la base de données
        put_user_password_service(user_id, hashed_password)

        return jsonify({"message": "Mot de passe mis à jour avec succès"}), 200

    except Exception as e:
        return jsonify({"message": f"Erreur lors de la mise à jour du mot de passe : {str(e)}"}), 500
    
@user_bp.route('/delete-account', methods=['PUT'])
@limiter.limit("3 per minute")  # Limite les requêtes pour éviter les abus
@jwt_required()
def delete_user_account():
    try:
        user_id = get_jwt_identity()  # Récupère l'ID utilisateur depuis le token JWT
        data = request.get_json()

        # Vérification du mot de passe pour confirmer l'identité
        if not data.get('password'):
            return jsonify({"message": "Le mot de passe est requis pour supprimer le compte"}), 400

        # Récupération de l'utilisateur
        user = get_user_by_id_service(user_id)
        if not user:
            return jsonify({"message": "Utilisateur non trouvé"}), 404

        # Vérification du mot de passe
        if not check_password(data['password'], user['password_hash']):
            return jsonify({"message": "Mot de passe incorrect"}), 403

        # Suppression de l'utilisateur
        delete_user_service(user_id)

        return jsonify({"message": "Compte utilisateur supprimé avec succès"}), 200

    except Exception as e:
        return jsonify({"message": f"Erreur lors de la suppression du compte : {str(e)}"}), 500

@user_bp.route('/collection', methods=['POST'])
@jwt_required()
def post_collection():
    try:
        user_id = get_jwt_identity()  # Récupère l'ID utilisateur depuis le token JWT
        data = request.get_json()

        # Récupération de l'utilisateur
        user = get_user_by_id_service(user_id)
        if not user:
            return jsonify({"message": "Utilisateur non trouvé"}), 404
        
        if user.sub is None:
            user.sub = data['sub']
            db.session.commit()

        collection = save_user_collections_service(user_id, data['collection'])
        return jsonify(collection), 200

    except Exception as e:
        return jsonify({"message": f"Erreur lors de la suppression du compte : {str(e)}"}), 500
    
@user_bp.route('/collection', methods=['GET'])
@jwt_required()
def get_collection():
    try:
        user_id = get_jwt_identity()  # Récupère l'ID utilisateur depuis le token JWT

        # Récupération de l'utilisateur
        user = get_user_by_id_service(user_id)
        if not user:
            return jsonify({"message": "Utilisateur non trouvé"}), 404
        
        collection = get_user_collections_service(user_id)
        return jsonify(collection), 200

    except Exception as e:
        return jsonify({"message": f"Erreur lors de la suppression du compte : {str(e)}"}), 500