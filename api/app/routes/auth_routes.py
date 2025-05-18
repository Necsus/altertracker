import os
import re
import sib_api_v3_sdk
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt, unset_jwt_cookies
)
from app.utils.emails import render_template_with_data
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.extensions import db
from app.utils.security import hash_password, check_password
from flask_mail import Message, Mail
import itsdangerous
from datetime import datetime
from app.extensions import mail_api, ApiException

auth_bp = Blueprint('auth', __name__)
mail = Mail()
serializer = itsdangerous.URLSafeTimedSerializer('secret-reset-token')

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

    # Envoi d'un email de bienvenue
    template_path = os.path.join(os.path.dirname(__file__), '../templates/register.html')
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": data['email'], "name": data['username']}],
        subject="Bienvenue sur AlterTracker.com",
        html_content=render_template_with_data(template_path, {
            "USERNAME": data['username'],
            "LIEN_DE_VALIDATION": "https://altertracker.com/",
            "YEAR": str(datetime.now().year)
        }),
        sender={"name": "AlterTracker", "email": "noreply@altertracker.com"}
    )
    try:
        response = mail_api.send_transac_email(send_smtp_email)
        print(response)
    except ApiException as e:
        print("Exception lors de l'appel à l’API Sendinblue: %s\n" % e)
    return jsonify({"message": "User created"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password(data['password'], user.password_hash):
        return jsonify({"message": "Invalid credentials"}), 401
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify(access_token=access_token, refresh_token=refresh_token)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    db.session.add(TokenBlacklist(jti=jti))
    db.session.commit()
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"message": "Email not found"}), 404
    token = serializer.dumps(user.email, salt='reset')
    reset_url = f"http://frontend/reset-password/{token}"
    msg = Message("Password Reset", recipients=[user.email])
    msg.body = f"Click to reset: {reset_url}"
    mail.send(msg)
    return jsonify({"message": "Reset email sent"}), 200

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='reset', max_age=3600)
    except itsdangerous.BadSignature:
        return jsonify({"message": "Invalid or expired token"}), 400
    data = request.get_json()
    user = User.query.filter_by(email=email).first()
    user.password_hash = hash_password(data['password'])
    db.session.commit()
    return jsonify({"message": "Password updated"}), 200