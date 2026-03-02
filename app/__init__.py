from flask import Flask

from app.extensions import db, migrate
from app.routes import api_bp, ui_bp


def create_app(config_object: str = "config.Config") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(api_bp)
    app.register_blueprint(ui_bp)

    return app
