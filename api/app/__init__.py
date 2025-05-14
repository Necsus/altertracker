from flask import Flask, jsonify, request
from flask_cors import CORS
from app.extensions import db, migrate
from app.routes.global_routes import global_bp
from app.routes.card_routes import card_bp
from app.routes.auth_routes import auth_bp, mail
from app.config import Config, ConfigEnv
from flask_jwt_extended import JWTManager, get_jwt
from app.models.token_blacklist import TokenBlacklist

def create_app():
    app = Flask(__name__)
    CORS(app, origins=ConfigEnv.CORS_ORIGINS)
    app.config.from_object(Config)

    db.init_app(app)
    #mail.init_app(app)
    jwt = JWTManager(app)
    migrate.init_app(app, db)

    app.register_blueprint(global_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(card_bp)

    @app.before_request
    def check_blacklist():
        if request.endpoint in ['auth.logout', 'auth.refresh']:
            jti = get_jwt().get("jti")
            if jti and TokenBlacklist.query.filter_by(jti=jti).first():
                return jsonify({"msg": "Token revoked"}), 401

    # with app.app_context():
    #     db.create_all()

    return app