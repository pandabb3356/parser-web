import os
import os.path

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix

from web.queue import instant_jobs_queue
from web.sqlalchemy import get_sqla_database_uri
from .database import db

DEFAULT_COPYRIGHT_TEMPLATE = "Copyright © {year} {copyright_owner} 保留所有權利"


def create_app(dev_mode=False):
    app = Flask(__name__)

    CORS(
        app,
        resources=[r"/(anonymous-)?api/*", r"(/static)?/external-api/*", r"/api/*"],
        origins=[r"https?:.*"],
        headers=["Content-Type", "X-Requested-With", "Authorization", "X-SESSION-ID"],
    )

    # init. app settings
    app.config.from_object(os.environ["APP_SETTINGS"])
    _init_app_settings(app)

    # init. app plugins
    init_plugins(app)

    _migrate_and_upgrade_db(app, db)

    _register_context_processors(app)
    _register_blueprints(app)

    @app.after_request
    def dont_cache_html_and_json(response):
        content_type = response.headers.get("content-type")
        # response.headers['Access-Control-Expose-Headers'] = 'X-SESSION-ID'
        if "text/html" in content_type or "application/json" in content_type:
            response.headers["Cache-Control"] = "no-store, no-cache"
        return response

    return app


def _init_app_settings(app):
    # init. sqlalchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = get_sqla_database_uri(
        db_user=app.config["WEB_DB_USER"],
        db_pwd=app.config["WEB_DB_PASSWORD"],
        db_host=app.config["WEB_DB_HOST"],
        db_port=app.config["WEB_DB_PORT"],
        db_database=app.config["WEB_DB_DATABASE"],
        db_type=app.config["WEB_DB_TYPE"],
    )


def init_plugins(app):
    from . import (
        security,
        session,
        line,
    )

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)

    db.init_app(app)
    security.init_app(app)
    session.init_app(app)
    instant_jobs_queue.init_app(app)
    line.init_app(app)


# for detection
def _migrate_and_upgrade_db(app, app_db):
    Migrate(app, app_db)

    # unmarked modify models when executing 'inv db.migrate'
    from web.models.org import Org
    from web.models.record import Record, RecordData
    from web.models.service import Service
    from web.models.toggle import TronClassToggle
    from web.models.user import User


def _get_context_processor(app):
    def _get_context():
        context = dict(
            app_config=app.config,
        )
        return context

    return _get_context


def _register_context_processors(app):
    app.context_processor(_get_context_processor(app))


def _register_blueprints(app, dev_mode=False):
    from web.api import bp as api_bp
    from web.views.root import bp as root_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(root_bp, url_prefix=None)
