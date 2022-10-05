from web.frontend.services import build_frontend_url


def get_login_url(app) -> str:
    return build_frontend_url(app.config, "login")
