from typing import Optional

from flask import Flask
from linebot import (
    LineBotApi,
    WebhookHandler,
)
from linebot.models import MessageEvent, TextMessage, AccountLinkEvent

_line_bot_api: Optional[LineBotApi] = None
_handler: Optional[WebhookHandler] = None


def get_line_config(app_config: dict) -> dict:
    return app_config.get("LINE") or {}


def get_line_channel_secret(app_config: dict) -> str:
    return get_line_config(app_config).get("channel_secret") or ""


def get_line_channel_token(app_config: dict) -> str:
    return get_line_config(app_config).get("channel_token") or ""


def get_line_bot_config(app_config) -> dict:
    return get_line_config(app_config).get("bot") or {}


def get_account_link_uri(app_config) -> str:
    return get_line_config(app_config).get("account_link_uri") or ""


def issue_link_token(user_id: str, timeout: int = 300) -> str:
    return _line_bot_api.issue_link_token(user_id, timeout=timeout).link_token


def handle_request(body, signature):
    _handler.handle(body, signature)


def init_app(app: Flask):
    globals()["_line_bot_api"]: LineBotApi = LineBotApi(
        get_line_channel_token(app.config)
    )
    globals()["_handler"]: WebhookHandler = WebhookHandler(
        get_line_channel_secret(app.config)
    )

    from .bot import (
        build_handle_message,
        build_handle_account_link,
    )

    bot_config = get_line_bot_config(app.config)

    _handler.add(MessageEvent, message=TextMessage)(
        build_handle_message(
            _line_bot_api,
            app_config=app.config,
            bot_config=bot_config,
        )
    )

    _handler.add(AccountLinkEvent)(
        build_handle_account_link(
            _line_bot_api,
        )
    )
