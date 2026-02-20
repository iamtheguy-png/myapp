"""
Application configuration. Secrets from environment; no hardcoded credentials.
"""
import os
from pathlib import Path


class Config:
    """Base config."""
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        # Dev-only fallback; set SECRET_KEY in env for production
        SECRET_KEY = "dev-secret-change-in-production"

    # SQLite in instance folder
    BASE_DIR = Path(__file__).resolve().parent.parent
    INSTANCE_PATH = BASE_DIR / "instance"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URI"
    ) or f"sqlite:///{INSTANCE_PATH / 'receipts.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads (Phase 2): store outside web root
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or str(INSTANCE_PATH / "uploads")
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"


class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"
    # Require SECRET_KEY in production
    if Config.SECRET_KEY == "dev-secret-change-in-production":
        raise ValueError("Set SECRET_KEY in environment for production")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
