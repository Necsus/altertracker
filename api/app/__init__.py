from flask import Flask
from app.extensions import db, migrate
from app.routes.example_routes import example_bp

def create_app(config_filename='config.py'):
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(example_bp)

    return app