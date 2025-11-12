from flask import Flask, jsonify, request
from flask_cors import CORS
from app.extensions import db, migrate
from app.routes.global_routes import global_bp
from app.routes.card_routes import card_bp
from app.routes.offer_routes import offer_bp
from app.routes.user_routes import user_bp
from app.routes.discord_routes import discord_bp
from app.routes.auth_routes import auth_bp
from app.routes.script_routes import script_bp
from app.routes.purchase_routes import purchase_bp
from app.routes.cookie_manager_routes import cookiemanager_bp
from app.routes.chat_routes import chat_bp
from app.routes.article_routes import article_bp
from app.routes.player_routes import player_bp
from app.config import Config, ConfigEnv
from flask_jwt_extended import JWTManager
from app.extensions import socketio
from app.extensions import limiter
from app.extensions import cache
from flask_socketio import SocketIO

def create_app():
    app = Flask(__name__)
    CORS(app, origins=ConfigEnv.CORS_ORIGINS, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], supports_credentials=True)
    app.config.from_object(Config)

    db.init_app(app)
    jwt = JWTManager(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins=ConfigEnv.CORS_ORIGINS, async_mode='gevent')
    limiter.init_app(app)
    cache.init_app(app)

    app.register_blueprint(global_bp, url_prefix="/api/global")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(card_bp, url_prefix="/api/card")
    app.register_blueprint(offer_bp, url_prefix="/api/offer")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(discord_bp, url_prefix="/api/discord")
    app.register_blueprint(script_bp, url_prefix="/api/script")
    app.register_blueprint(purchase_bp, url_prefix="/api/purchase")
    app.register_blueprint(cookiemanager_bp, url_prefix="/api/cookie-manager")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(article_bp, url_prefix='/api/article')
    app.register_blueprint(player_bp, url_prefix='/api/player')

    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
          origin = request.headers.get("Origin")
          allowed_origins = ConfigEnv.CORS_ORIGINS

          if origin in allowed_origins:
              response = jsonify({"message": "CORS preflight passed"})
              response.headers.add("Access-Control-Allow-Origin", origin)
              response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
              response.headers.add("Access-Control-Allow-Headers", "Authorization, Content-Type")
              response.headers.add("Access-Control-Allow-Credentials", "true")
              return response, 200
          else:
              return jsonify({"message": "Origin not allowed"}), 403

    # @app.before_request
    # def check_blacklist():
    #     if request.endpoint in ['auth.refresh']:
    #         verify_jwt_in_request()
    #         jti = get_jwt().get("jti")
    #         if jti and TokenBlacklist.query.filter_by(jti=jti).first():
    #             return jsonify({"message": "Token revoked"}), 401

    # with app.app_context():
    #     db.create_all()

    return app