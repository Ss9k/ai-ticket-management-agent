"""
Flask frontend configuration.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "flask-secret-change-in-prod")
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
