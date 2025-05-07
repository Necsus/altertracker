from flask import Flask
from .extensions import db, migrate

def create_app(config_filename='config.py'):
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes.example_routes import example_bp
    app.register_blueprint(example_bp)

    return app