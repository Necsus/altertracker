from flask import Flask
from flask_cors import CORS
from app.extensions import db, migrate
from api.app.routes.global_routes import global_bp
from api.app.routes.card_routes import card_bp
from app.config import Config

def create_app():
    app = Flask(__name__)
    CORS(app, origins='*')
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(global_bp)
    app.register_blueprint(card_bp)

    return app