import os


APP_SETTINGS_MAP = {
    "dev": "conf.dev.DevelopmentConfig",
    "prod": "conf.prod.ProductionConfig",
}


def get_web_config_path():
    app_settings = os.environ.get("APP_SETTINGS")
    if not app_settings:
        env = os.environ.get("ENV") or "dev"
        app_settings = APP_SETTINGS_MAP.get(env) or "conf.dev.DevelopmentConfig"
    return app_settings
