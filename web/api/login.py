from typing import NamedTuple

from flask import session, redirect
from flask_login import current_user, login_user
from flask_security.forms import get_form_field_label, _datastore, Form
from flask_security.utils import (
    verify_and_update_password,
    get_message,
    logout_user,
)
from wtforms import StringField, PasswordField

from web.api import bp
from web.api.response_helper import validation_failed, success, bad_request_error
from web.line.bot import set_nonce_to_session, account_link_login
from web.models.user import User


class EmailLoginForm(Form):  # pylint: disable=too-many-ancestors
    org_id = StringField(get_form_field_label("org_id"), default="")
    email = StringField(get_form_field_label("email"), default="")
    password = PasswordField(get_form_field_label("password"), default="")

    def __init__(self, *args, **kwargs):
        super(EmailLoginForm, self).__init__(*args, **kwargs)

    # def validate_email(self, field):
    #     _validate_email(field.data)

    def validate_data(self):
        if not super().validate() and len(self.errors) > 1:
            return False

        if self.password.data.strip() == "":
            self.password.errors.append(get_message("PASSWORD_NOT_PROVIDED")[0])
            return False

        self.user = _datastore.find_user(email=self.email.data)

        if self.user is None:
            self.email.errors.append(get_message("USER_DOES_NOT_EXIST")[0])
            return False
        if not verify_and_update_password(self.password.data, self.user):
            self.password.errors.append(get_message("INVALID_PASSWORD")[0])
            return False
        if not self.user.is_active:
            self.email.errors.append(get_message("DISABLED_ACCOUNT")[0])
            return False
        return True

    def validate(self):
        result = self.validate_data()
        return result


class LoggedInUser(NamedTuple):
    id: int
    name: str
    email: str

    @classmethod
    def init_from_user(cls, user: User) -> "LoggedInUser":
        return LoggedInUser(id=user.id, name=user.name, email=user.email)


@bp.route("/login", methods=["POST"])
@account_link_login
def login():
    if current_user.is_authenticated and current_user.is_active:
        logged_in_user = LoggedInUser.init_from_user(current_user)
        return success({"user": logged_in_user._asdict()})

    form = EmailLoginForm()
    if not form.validate():
        return validation_failed(form.errors)

    login_user(form.user)

    # link_url = set_nonce_to_session(session, form.user.id)
    # if link_url:
    #     return redirect(link_url)

    return success(
        {
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
            }
        }
    )


@bp.route("/login-check", methods=["GET"])
def login_check():
    if current_user.is_authenticated and current_user.is_active:
        logged_in_user = LoggedInUser.init_from_user(current_user)
        return success({"user": logged_in_user._asdict()})
    return success({"user": None})


@bp.route("/logout", methods=["GET", "POST"])
def logout():
    if current_user.is_authenticated:
        logout_user()
    return success()
