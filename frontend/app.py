"""
SupportPilot — Flask Frontend Application Entry Point
"""
import sys
import os

# Ensure project root is on path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from frontend.config import Config
from frontend.routes import auth, user, admin, engineer, analytics


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(engineer.bp)
    app.register_blueprint(analytics.bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
