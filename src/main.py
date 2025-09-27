from __future__ import annotations
import os
from pathlib import Path
from flask import Flask, app, jsonify
from src.conf import settings
from src.conf.errors import DomainError, to_http
from src.record.common.storage import ensure_dir

def create_app() -> Flask:
    app = Flask(__name__)
    app.url_map.strict_slashes = False  # accept /path and /path/

    data_dir = Path(os.getenv("DATA_DIR", settings.DATA_DIR))
    tz = os.getenv("TIMEZONE", settings.TIMEZONE)
    autosave = (os.getenv("AUTOSAVE", str(settings.AUTOSAVE)).lower() == "true")

    app.config.update(
        DATA_DIR=data_dir,
        TIMEZONE=tz,
        API_VERSION=settings.API_VERSION,
        AUTOSAVE=autosave,
    )
    ensure_dir(data_dir)

    @app.errorhandler(DomainError)
    def handle_domain_error(err: DomainError):
        body, status = to_http(err)
        return jsonify(body), status

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "version": app.config["API_VERSION"]})

    #======== Blueprints ========
    # Clients
    from src.record.clients.api import bp as clients_bp
    app.register_blueprint(clients_bp, url_prefix=f"/api/{app.config['API_VERSION']}/clients")

    # Airlines
    from src.record.airlines.api import bp as airlines_bp
    app.register_blueprint(airlines_bp, url_prefix=f"/api/{app.config['API_VERSION']}/airlines")

    return app
