"""
WSGI entry point for Gunicorn (production) or other WSGI servers.
"""
from app import create_app

app = create_app()
