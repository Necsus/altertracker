from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
import requests
from app.models.user import User
from app.extensions import db
from app.config import ConfigEnv

discord_bp = Blueprint('discord', __name__)

@discord_bp.route('/callback', methods=['POST'])
@jwt_required()
def discord_callback():
    code = request.json.get('code')

    token_response = requests.post(
        "https://discord.com/api/oauth2/token",
        data={
            'client_id': ConfigEnv.DISCORD_CLIENT_ID,
            'client_secret': ConfigEnv.DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': ConfigEnv.DISCORD_REDIRECT_URI,
            'scope': 'identify'
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    if token_response.status_code != 200:
        return jsonify({'error': 'Invalid token response'}), 400

    access_token = token_response.json().get('access_token')

    user_response = requests.get(
        "https://discord.com/api/users/@me",
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if user_response.status_code != 200:
        return jsonify({'error': 'Could not fetch user info'}), 400

    user_info = user_response.json()
    discord_id = user_info.get('id')

    # ⬇️ Ici tu enregistres l'ID dans ta base utilisateur
    # (exemple fictif)
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user:
        user.discord_id = discord_id
        db.session.commit()
        return jsonify({'message': 'Discord ID linked successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404
