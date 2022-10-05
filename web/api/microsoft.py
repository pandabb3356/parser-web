from flask import current_app, redirect, session, request, abort
from flask_login import login_user

from web import db
from web.api import bp
from web.api.response_helper import success
from web.line.bot import set_nonce_to_session, account_link_login
from web.microsoft.msal import init_msal_app, MSUser

microsoft_namespace = "microsoft"


@bp.route(f"/{microsoft_namespace}/auth", methods=["GET", "OPTIONS"])
def microsoft_auth():
    msal_app = init_msal_app(current_app)
    flow = msal_app.init_auth_code_flow(state="microsoft")
    session["flow"] = flow
    return success({"auth_uri": flow["auth_uri"]})


@bp.route(f"/{microsoft_namespace}/callback")
@account_link_login
def microsoft_callback():
    from web.user.services import UserInfo, get_or_generate_user
    from web.security import get_login_url

    msql_app = init_msal_app(current_app)

    result = msql_app.get_token_by_auth_code_flow(
        flow=session.get("flow") or {},
        auth_response=request.args,
    )

    ms_user: MSUser = msql_app.init_user_from_id_token_claims(
        result.get("id_token_claims") or {}
    )

    user_info: UserInfo = UserInfo(
        user_no=ms_user.email,
        email=ms_user.email,
        name=ms_user.email,
        active=True,
    )

    if not user_info.user_no:
        abort(500)

    is_existed, user = get_or_generate_user(user_info)

    if not is_existed:
        db.session.add(user)
        db.session.commit()

    login_user(user)

    # link_url = set_nonce_to_session(session, user.id)
    # if link_url:
    #     return redirect(link_url)

    return redirect(get_login_url(current_app))
