from typing import Callable, List

from flask import request, redirect, session, current_app
from flask_login import current_user
from flask_security import (
    SQLAlchemyUserDatastore,
    Security,
    views as flask_security_views,
)
from sqlalchemy.orm.exc import NoResultFound

from web import db
from web.models.user import User
from web.security.services import get_login_url
from web.security.views import login

STATIC_URL_PREFIX = "/static"

PUBLIC_URLS = [
    "/",
    "/login",
    "/logout",
    "/api/login",
    "/api/login-check",
    "/api/microsoft/auth",
    "/api/microsoft/callback",
    "/api/linebot/link",
    "/api/linebot/callback",
]


PUBLIC_URL_REGEXPS = []


DIAGNOSTIC_URL_PREFIX = "/d"
API_PREFIX = "/api"
INTERNAL_API_PREFIX = "/internal-api"


class UserDatastore(SQLAlchemyUserDatastore):
    def find_user(self, **kwargs):
        try:
            if kwargs.get("id") is not None:
                return self.user_model.query.get(kwargs["id"])
            if kwargs.get("user_no") is not None:
                return self.user_model.query.filter(
                    User.user_no == kwargs.get("user_no")
                ).first()
            elif kwargs.get("email") is not None:
                return self.user_model.query.filter(
                    User.email == kwargs.get("email")
                ).first()

        except NoResultFound:
            return None

    def get_user_by_user_name(self, user_name):

        user_query = self.user_model.query
        return user_query.filter(User.user_no == user_name).first()

    def find_role(self, role):
        raise NotImplementedError

    def create_role(self, **kwargs):
        raise NotImplementedError

    def remove_role_from_user(self, user, role):
        raise NotImplementedError

    def add_role_to_user(self, user, role):
        raise NotImplementedError


_user_datastore = UserDatastore(db, User, None)
_security = Security(
    app=None,
    datastore=_user_datastore,
)


flask_security_views.login = login


def init_app(app):
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SECURITY_PASSWORD_HASH"] = "plaintext"
    app.config["SECURITY_PASSWORD_SINGLE_HASH"] = True
    app.config["SECURITY_DEPRECATED_PASSWORD_SCHEMES"] = []
    app.config["SECURITY_MSG_ORG_ID_NOT_PROVIDED"] = ("Org Id not provided", "error")
    app.config["SECURITY_MSG_USER_NO_NOT_PROVIDED"] = ("User No not provided", "error")
    app.config["SECURITY_MSG_USER_NO_DOES_NOT_EXIST"] = (
        "Specified user no does not exist",
        "error",
    )

    state = _security.init_app(app)
    state.principal.skip_static = True

    app.register_blueprint(app.blueprints["security"])

    _register_before_request_actions(app)


def _match_public_url_regexp(path):
    return any(regexp.match(path) for regexp in PUBLIC_URL_REGEXPS)


def _register_before_request_actions(app):
    actions = [
        _check_login,
        _check_line_link_token,
    ]
    for action in actions:
        app.before_request(action)


def _check_line_link_token():
    link_token = request.args.get("lineLinkToken", "")
    if not link_token:
        return

    allow_paths = ["/api/login", "/api/microsoft/auth", "/api/microsoft/callback"]
    for allow_path in allow_paths:
        if request.path.startswith(allow_path):
            session["line"] = {"link_token": link_token}
            break


def _check_login():
    if current_user.is_authenticated and not current_user.is_active():
        session.clear()
        return redirect(get_login_url(current_app))

    if (
        current_user.is_authenticated
        or request.path in PUBLIC_URLS
        or request.path.startswith(STATIC_URL_PREFIX)
        or request.path.startswith(DIAGNOSTIC_URL_PREFIX)
        or _match_public_url_regexp(request.path)
    ):

        return None

    if request.method == "OPTIONS" and request.path.startswith(API_PREFIX):
        return None

    return redirect(get_login_url(current_app))
