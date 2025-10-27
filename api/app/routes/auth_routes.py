import os
import re
import sib_api_v3_sdk
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, get_jwt_identity, jwt_required, unset_jwt_cookies
)
from app.config import Config, ConfigEnv
from app.utils.emails import render_template_with_data
from app.models.user import User
from app.extensions import db, mail_api, ApiException, limiter
from app.utils.security import hash_password, check_password
import itsdangerous
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)
REFRESH_TOKEN_EXPIRATION = 86400  # 30 jours
serializer = itsdangerous.URLSafeTimedSerializer(Config.SECRET_KEY)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    # Trimer les espaces en début et en fin pour chaque champ
    data = {key: value.strip() if isinstance(value, str) else value for key, value in data.items()}

    # Vérifier que tous les champs requis sont présents
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing fields"}), 400

    # Vérifier que l'email est valide
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, data['email']):
        return jsonify({"message": "Invalid email format"}), 400

    # Vérifier que le mot de passe contient plus de 9 caractères
    if len(data['password']) <= 9:
        return jsonify({"message": "Password must be longer than 9 characters"}), 400

    # Vérifier si l'email est déjà utilisé
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already used"}), 400
    # Vérifier si le pseudo est déjà utilisé
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Pseudo already used"}), 400
    hashed = hash_password(data['password'])
    user = User(username=data['username'], email=data['email'], password_hash=hashed)
    
    db.session.add(user)
    db.session.commit()

    # Générer un jeton de validation
    token = serializer.dumps(user.email, salt=Config.SECRET_KEY)
    validation_url = f"{ConfigEnv.ANGULAR_URL}/validate-email/{token}"

    # Envoi d'un email de bienvenue
    template_path = os.path.join(os.path.dirname(__file__), '../templates/register.html')
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": data['email'], "name": data['username']}],
        subject="Bienvenue sur AlterTracker.com",
        html_content=render_template_with_data(template_path, {
            "USERNAME": data['username'],
            "LIEN_DE_VALIDATION": validation_url,
            "YEAR": str(datetime.now(timezone.utc).year)
        }),
        sender={"name": "AlterTracker", "email": "noreply@altertracker.com"}
    )
    try:
        response = mail_api.send_transac_email(send_smtp_email)
        print(response)
    except ApiException as e:
        print("Exception lors de l'appel à l’API Sendinblue: %s\n" % e)
    return jsonify({"message": "Un email vient de vous être envoyé pour la suite de l'inscription"}), 201

@auth_bp.route('/validate-email/<token>', methods=['GET'])
@limiter.limit("5 per minute")
def validate_email(token):
    try:
        email = serializer.loads(token, salt=Config.SECRET_KEY, max_age=86400)  # 24 heure
    except itsdangerous.SignatureExpired:
        return jsonify({"message": "The token has expired"}), 400
    except itsdangerous.BadSignature:
        return jsonify({"message": "Invalid token"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.is_email_verified:
        return jsonify({"message": "Email already validated"}), 400

    user.is_email_verified = True
    db.session.commit()
    return jsonify({"message": "Email validated successfully"}), 200

@auth_bp.route('/resend-validation/<token>', methods=['GET'])
@limiter.limit("5 per minute")
def resend_validation_email(token):
    try:
        email = serializer.loads(token, salt=Config.SECRET_KEY, max_age=86400)  # 1 heure
        if not email:
            return jsonify({"message": "Email is required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        if user.is_email_verified:
            return jsonify({"message": "Email is already validated"}), 400

        # Générer un nouveau jeton de validation
        token = serializer.dumps(user.email, salt=Config.SECRET_KEY)
        validation_url = f"{ConfigEnv.ANGULAR_URL}/validate-email/{token}"

        # Envoi d'un email de bienvenue
        template_path = os.path.join(os.path.dirname(__file__), '../templates/register.html')
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": user.email, "name": user.username}],
            subject="Bienvenue sur AlterTracker.com",
            html_content=render_template_with_data(template_path, {
                "USERNAME": user.username,
                "LIEN_DE_VALIDATION": validation_url,
                "YEAR": str(datetime.now(timezone.utc).year)
            }),
            sender={"name": "AlterTracker", "email": "noreply@altertracker.com"}
        )
        try:
            response = mail_api.send_transac_email(send_smtp_email)
            print(response)
        except ApiException as e:
            print("Exception lors de l'appel à l’API Sendinblue: %s\n" % e)
    except itsdangerous.SignatureExpired:
        return jsonify({"message": "The token has expired"}), 400
    except itsdangerous.BadSignature:
        return jsonify({"message": "Invalid token"}), 400

    
    return jsonify({"message": "Validation email resent successfully"}), 200

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password(data['password'], user.password_hash):
        return jsonify({"message": "Invalid credentials"}), 401
    if not user.is_email_verified:
        return jsonify({"message": "Email not verified"}), 401
    additional_claims = {
        "is_admin": user.is_admin,
        "is_publisher": user.is_publisher,
        "username": user.username,
        "did_linked": True if user.discord_id else False
    }
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    return jsonify(access_token=access_token), 200

@auth_bp.route('/refresh-token', methods=['GET'])
@limiter.limit("10 per minute")
@jwt_required()  # Nécessite un refresh token
def refresh_token():
    user_id = get_jwt_identity()  # Récupère l'identité de l'utilisateur à partir du refresh token
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    additional_claims = {
        "is_admin": user.is_admin,
        "is_publisher": user.is_publisher,
        "username": user.username,
        "did_linked": True if user.discord_id else False
    }
    new_access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    return jsonify(access_token=new_access_token), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response

@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("5 per minute")
def forgot_password():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"message": "Email not found"}), 404

    # Générer un nouveau jeton de validation
    token = serializer.dumps(user.email, salt=Config.SECRET_KEY)
    reset_url = f"{ConfigEnv.ANGULAR_URL}/reset-password/{token}"

    template_path = os.path.join(os.path.dirname(__file__), '../templates/reset-password.html')
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": user.email, "name": user.username}],
        subject="Changement de mot de passe AlterTracker",
        html_content=render_template_with_data(template_path, {
            "USERNAME": user.username,
            "RESET_LINK": reset_url,
            "YEAR": str(datetime.now(timezone.utc).year)
        }),
        sender={"name": "AlterTracker", "email": "noreply@altertracker.com"}
    )
    try:
        response = mail_api.send_transac_email(send_smtp_email)
        print(response)
    except ApiException as e:
        print("Exception lors de l'appel à l’API Sendinblue: %s\n" % e)
    return jsonify({"message": "Reset Password email sent"}), 200

@auth_bp.route('/reset-password/<token>', methods=['POST'])
@limiter.limit("5 per minute")
def reset_password(token):
    try:
        email = serializer.loads(token, salt=Config.SECRET_KEY, max_age=3600)
    except itsdangerous.BadSignature:
        return jsonify({"message": "Invalid or expired token"}), 400
    data = request.get_json()
    user = User.query.filter_by(email=email).first()
    user.password_hash = hash_password(data['password'])
    db.session.commit()
    return jsonify({"message": "Password updated"}), 200