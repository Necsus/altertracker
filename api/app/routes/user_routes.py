import sib_api_v3_sdk
from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import mail_api, ApiException
from app.services.user_service import (
    get_user_search_service,
    save_user_search_service,
    delete_user_search_service,
    get_user_count_data,
    get_user_alert_service,
    save_user_alert_service,
    delete_user_alert_service,
    edit_user_alert_service,
    get_user_alert_with_card_service
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


@user_bp.route('/alerts/<int:id_alert>', methods=['PUT'])
@jwt_required()
def update_user_alert(id_alert):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Vérifie si l'alerte appartient à l'utilisateur authentifié
        alerts = get_user_alert_service(user_id)
        if not any(alert["id"] == id_alert for alert in alerts):
            return jsonify({"message": "Alerte non trouvée ou non autorisée"}), 403

        updated_alert = edit_user_alert_service(id_alert, data)
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
            html_content=data.get('message'),
            sender={"name": f"{data.get('name')} id: {user_id}", "email": data.get('email')}
        )
        try:
            response = mail_api.send_transac_email(send_smtp_email)
        except ApiException as e:
            print("Exception lors de l'appel à l’API Sendinblue: %s\n" % e)
        return jsonify({"message": "Votre message a été envoyé avec succès"}), 200
    except Exception as e:
        return jsonify({"message": f"Erreur lors de l'envoi de l'email : {str(e)}"}), 500