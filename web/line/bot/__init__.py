import base64
import json
import re
from collections import OrderedDict
from functools import wraps
from typing import List, Tuple, Type, Optional, Callable

from flask import current_app, redirect, session as flask_session
from flask_login import current_user
from linebot import LineBotApi
from linebot.models import (
    Message,
    AccountLinkEvent,
    TextSendMessage,
)

from web.line.bot.command.base import LineBotCommand
from web.line.bot.command.login import LoginLineBotCommand
from web.line.bot.command.org import (
    OrgLineBotCommand,
    OrgListBotCommand,
    OrgDetailBotCommand, OrgVersionBotCommand, OrgToggleBotCommand,
)
from web.user.repository import get_user_by_id


class LineBotLoginHelper:
    nonce_prefix = "line:nonce:"
    user_map_key = "line_user_map"

    def __init__(self, line_user_id: str = "", nonce: str = ""):
        self.redis = getattr(current_app.session_interface, "redis", None)
        if not self.redis:
            raise ValueError

        self.nonce = nonce
        self.line_user_id = line_user_id

        data = self.redis.hget(self.user_map_key, self.line_user_id) or "{}"
        self.user_info = json.loads(data)

    @property
    def is_user_binding(self) -> bool:
        return bool(self.user_info)

    @property
    def is_nonce_map_existed(self) -> bool:
        return bool(self.get_user_id_by_nonce())

    @property
    def user_id(self) -> int:
        return int(self.user_info.get("user_id") or 0)

    def set_user_id_by_nonce(self, new_nonce: str, user_id: int):
        self.redis.set(f"{self.nonce_prefix}{new_nonce}", f"{user_id}", ex=300)

    def get_user_id_by_nonce(self) -> str:
        return str(self.redis.get(f"{self.nonce_prefix}{self.nonce}") or "")

    @classmethod
    def build_nonce(cls, link_token: str, user_id: int) -> str:
        return base64.b64encode(f"{link_token},{user_id}".encode("ascii")).decode(
            "utf-8"
        )

    def set_line_user_info_to_redis(self, user_id: int):
        data = {"user_id": str(user_id)}
        self.redis.hset(self.user_map_key, self.line_user_id, json.dumps(data))


class LineBot:
    def __init__(self, app_config: dict, user, line_user_id: str):
        self.app_config = app_config
        self.user = user
        self.line_user_id = line_user_id

        self.logs = []

    def add_logs(self, info: str):
        self.logs += [info]

    @property
    def commands_map(self) -> OrderedDict:
        return OrderedDict(
            [
                (
                    LoginLineBotCommand.namespace,
                    [
                        LoginLineBotCommand,
                    ],
                ),
                (
                    OrgLineBotCommand.namespace,
                    [
                        OrgListBotCommand,
                        OrgDetailBotCommand,
                        OrgVersionBotCommand,
                        OrgToggleBotCommand,
                    ],
                ),
            ]
        )

    def find_candidate_commands(self, text: str) -> List[Type[LineBotCommand]]:
        for k in self.commands_map.keys():
            if text.startswith(k):
                return self.commands_map[k]
        return []

    @classmethod
    def find_matched_command(
        cls,
        text: str,
        commands: List[Type[LineBotCommand]],
    ) -> Tuple[Optional[Type[LineBotCommand]], Optional[re.Match]]:
        for command in commands:
            result = command.search(text)
            if result is not None:
                return command, result
        return None, None

    def send_login_message(self) -> Message:
        return LoginLineBotCommand.execute(**self.common_variables)

    @property
    def is_login(self) -> bool:
        return self.user is not None

    @property
    def common_variables(self) -> dict:
        return {
            "app_config": self.app_config,
            "user": self.user,
            "line_user_id": self.line_user_id,
        }

    def execute(self, text: str) -> Optional[Message]:
        text = text.lower().strip()

        commands = self.find_candidate_commands(text)

        if not commands:
            self.add_logs("not found matched command namespace")
            return

        command, result = self.find_matched_command(text, commands)
        if not command:
            self.add_logs("not found matched command")
            return

        if command.should_login and not self.is_login:
            return self.send_login_message()

        c = command()
        validator = c.validate_command(result)
        if validator.errors:
            return validator.errors

        variables = self.common_variables
        variables.update(validator.command_variables)
        return c.execute(**variables)


def set_nonce_by_link_token(link_token: str, user_id: int) -> str:
    nonce = LineBotLoginHelper.build_nonce(link_token, user_id)
    helper = LineBotLoginHelper()
    helper.set_user_id_by_nonce(nonce, user_id)
    return nonce


def set_nonce_to_session(session, user_id: int) -> Optional[str]:
    from web.line import get_account_link_uri
    link_token = (session.get("line") or {}).get("link_token")
    if link_token:
        nonce = set_nonce_by_link_token(link_token, user_id)
        return f"{get_account_link_uri(current_app.config)}?linkToken={link_token}&nonce={nonce}"
    return


def account_link_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if current_user.is_authenticated:
            link_url = set_nonce_to_session(flask_session, current_user.id)
            if link_url:
                return redirect(link_url)
        return result
    return wrapper


def get_line_bot_text_mapper(bot_config: dict) -> dict:
    return bot_config.get("text_mapper") or {}


def build_handle_message(
    line_bot_api: LineBotApi,
    app_config: dict,
    bot_config: dict,
) -> Callable:
    text_mapper = get_line_bot_text_mapper(bot_config)
    LineBotCommand.register_text_mapper(text_mapper)

    def handle_message(event):
        line_user_id = event.source.user_id

        login_helper = LineBotLoginHelper(line_user_id=event.source.user_id)
        user = get_user_by_id(login_helper.user_id)
        bot = LineBot(app_config, user, line_user_id)

        message = bot.execute(event.message.text)

        if message is not None:
            line_bot_api.reply_message(
                event.reply_token,
                message,
            )

    return handle_message


def build_handle_account_link(line_bot_api: LineBotApi) -> Callable:
    def handle_account_link(event: AccountLinkEvent):
        nonce = event.link.nonce
        line_user_id = event.source.user_id

        login_helper = LineBotLoginHelper(line_user_id, nonce)

        message = TextSendMessage(text="Success linked!!")

        if not login_helper.is_user_binding:
            if not login_helper.is_nonce_map_existed:
                message = TextSendMessage(text="Failed!!")
            else:
                user_id_by_nonce = login_helper.get_user_id_by_nonce()
                login_helper.set_line_user_info_to_redis(int(user_id_by_nonce))

        return line_bot_api.reply_message(
            event.reply_token,
            message,
        )

    return handle_account_link
