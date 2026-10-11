import logging
import os
import time

from flask import Flask, g, request

from . import db, metrics
from .logging_config import setup_logging
from .routes import bp


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.environ.get(
            "DATABASE_PATH", os.path.join(app.instance_path, "students.db")
        ),
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        APP_VERSION=os.environ.get("APP_VERSION", "dev"),
        APP_ENV=os.environ.get("APP_ENV", "dev"),
    )
    if config:
        app.config.update(config)

    os.makedirs(os.path.dirname(app.config["DATABASE"]) or ".", exist_ok=True)
    setup_logging(os.environ.get("LOG_LEVEL", "INFO"))

    db.init_app(app)
    with app.app_context():
        db.init_db()

    app.register_blueprint(bp)
    _register_request_hooks(app)
    return app


def _register_request_hooks(app):
    log = logging.getLogger("student-app")

    @app.before_request
    def _start_timer():
        g.start = time.perf_counter()

    @app.after_request
    def _record(response):
        duration = time.perf_counter() - getattr(g, "start", time.perf_counter())
        endpoint = request.url_rule.rule if request.url_rule else "unmatched"
        metrics.REQUESTS.labels(request.method, endpoint, response.status_code).inc()
        metrics.LATENCY.labels(endpoint).observe(duration)
        # Probe and scrape traffic is noisy; keep it out of the log stream.
        if endpoint not in ("/health", "/ready", "/metrics"):
            log.info(
                "request",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                },
            )
        return response
