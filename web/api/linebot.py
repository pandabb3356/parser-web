from flask import request, redirect, current_app
from linebot.exceptions import InvalidSignatureError

from web.api import bp
from web.api.response_helper import success, bad_request_error
from web.frontend.services import build_frontend_url
from web.line import handle_request

linebot_namespace = "linebot"


@bp.route(f"/{linebot_namespace}/link")
def linebot_link():
    link_token = request.args.get("lineLinkToken")
    if not link_token:
        return bad_request_error()

    login_url = build_frontend_url(
        current_app.config,
        "login",
        query_strings=[
            ("lineLinkToken", link_token)
        ]
    )
    return redirect(login_url)


@bp.route(f"/{linebot_namespace}/callback", methods=["POST"])
def linebot_callback():
    signature = request.headers["X-Line-Signature"]

    body = request.get_data(as_text=True)

    try:
        handle_request(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        bad_request_error()

    return success()
