"""
Expense Receipt Manager — Flask application factory.
"""
import logging
import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import RequestEntityTooLarge

from app.config import config

db = SQLAlchemy()
csrf = CSRFProtect()


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])

    # Logging: structured, no secrets
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
    app.logger.setLevel(logging.INFO)

    # Instance folder for SQLite and overrides
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)

    @app.errorhandler(RequestEntityTooLarge)
    def request_entity_too_large(e):
        app.logger.warning("Upload rejected: body too large")
        return render_template("errors/413.html"), 413

    with app.app_context():
        from app import models  # noqa: F401 — register models before create_all
        from app.routes import export, home, receipts, reports, search, tags

        app.register_blueprint(home.bp)
        app.register_blueprint(receipts.bp)
        app.register_blueprint(search.bp)
        app.register_blueprint(export.bp)
        app.register_blueprint(reports.bp)
        app.register_blueprint(tags.bp)
        db.create_all()

    return app
