from typing import List

from linebot.models import (
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    URITemplateAction,
    Message,
)

from web.config import get_web_host
from web.line.bot.command.base import LineBotCommand
from web.line.bot.enum import CommandNamespaceKey


class LoginLineBotCommand(LineBotCommand):
    _namespace = CommandNamespaceKey.login.value

    re_patterns: List[str] = [
        "(?P<other_word>.*)?$",
    ]

    namespace_pattern_splitter = ""

    command_template = "{login}"

    should_login = False

    @classmethod
    def template_variables(cls, **kwargs):
        return {
            "login": cls.transform_text("login"),
        }

    @classmethod
    def build_message(cls, login_url: str) -> Message:
        alt_text = "Login First"
        button_title = "Login"
        button_text = "Login"
        button_actions = [
            URITemplateAction(
                label=f"Go to login page",
                uri=login_url,
            ),
        ]

        return TemplateSendMessage(
            alt_text=alt_text,
            template=ButtonsTemplate(
                title=button_title,
                text=button_text,
                actions=button_actions,
            ),
        )

    @classmethod
    def execute(cls, **kwargs) -> TextSendMessage:
        from web.line import issue_link_token

        app_config = kwargs.get("app_config") or {}
        line_user_id = kwargs.get("line_user_id")

        link_token = issue_link_token(line_user_id)
        host_name = get_web_host(app_config)
        login_url = f"{host_name}api/linebot/link?lineLinkToken={link_token}"

        return cls.build_message(login_url)
