import os


class BaseConfig(object):
    DEBUG = True

    WEB_HOST = "0.0.0.0"
    WEB_HOST_NAME = "http://localhost:5300/"

    # Web database settings
    WEB_DB_HOST = "localhost"
    WEB_DB_PORT = 5432
    WEB_DB_USER = "postgres"
    WEB_DB_PASSWORD = ""
    WEB_DB_DATABASE = "parser_web"
    WEB_DB_TYPE = "postgresql"

    # Redis Config
    REDIS_PASSWORD = ""
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379

    SESSION_REDIS_DB = 5
    SESSION_BACKEND = "redis"
    SESSION_ANONYMOUS_TIME = 60
    SESSION_NON_PERMANENT_TIME = 86400

    # Rq Worker Config
    QUEUE_BACKEND = "redis"
    QUEUE_REDIS_DB = 3

    SECRET_KEY = "secret"

    # SqlAlchemy Settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UTC_TIME_OFFSET = 8

    MICROSOFT_TENANT_ID = ""
    MICROSOFT_SETTINGS = {
        "tenant_id": "",
        "client_id": "",
        "client_secret": "",
        "authority": f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}",
        "scopes": [
            "User.ReadBasic.All",
            "email",
        ],
        "redirect_uri": "",
    }

    # front-end
    FRONTEND_SETTINGS = {
        "host_name": "",
        "endpoint": {"login": "/login", "org_detail": "/org/{org_id}"},
    }

    # line
    LINE = {
        "channel_token": "",
        "channel_secret": "",
        "bot": {
            "text_mapper": {
                "org": "機構",
                "list": "列表",
                "login": "登入",
                "version": "版本",
                "toggle": "toggle",
            }
        },
        "account_link_uri": "https://access.line.me/dialog/bot/accountLink",
    }

    TRONCLASS = {
        "endpoint_map": {
            "version": os.environ.get("TRONCLASS_PATH_VERSION"),
            "health_check": os.environ.get("TRONCLASS_PATH_HEALTH_CHECK"),
            "toggles": os.environ.get("TRONCLASS_PATH_TOGGLES"),
        }
    }
