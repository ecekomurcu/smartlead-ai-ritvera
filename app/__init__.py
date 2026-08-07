import os

from flask import Flask
from flask_cors import CORS

from config import config_by_name
from . import database
from .routes import api_bp, pages_bp


def create_app():
    app = Flask(__name__)

    # Yerelde development, Render'da production ayarlarını yükler.
    config_name = os.environ.get("FLASK_ENV", "development")
    app.config.from_object(
        config_by_name.get(config_name, config_by_name["development"])
    )

    # JSON çıktılarında Türkçe karakterlerin düzgün görünmesini sağlar.
    app.json.ensure_ascii = False

    # Wix gibi farklı bir domainde çalışan arayüzlerin API'ye erişmesine izin verir.
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"]
            }
        }
    )

    database.init_app(app)

    with app.app_context():
        database.init_db()

    # API ve sayfa rotalarını uygulamaya kaydederiz.
    app.register_blueprint(api_bp)
    app.register_blueprint(pages_bp)

    @app.route("/health")
    def health():
        return {
            "status": "aktif",
            "message": "SmartLead backend çalışıyor.",
            "ai_provider": app.config["AI_PROVIDER"],
        }

    return app