from flask import Flask
from app.extensions import db, migrate
from app.routes.example_routes import example_bp
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(example_bp)

    return app