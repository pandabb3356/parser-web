from typing import List, Type, Optional

from linebot.models import (
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate, Message,
)
from linebot.models import (
    URITemplateAction,
    MessageTemplateAction,
)
from wtforms import StringField, ValidationError

from web.form import BaseForm
from web.frontend.services import build_frontend_url
from web.line.bot.command.base import LineBotCommand, LineBotCommandValidator
from web.line.bot.enum import CommandNamespaceKey
from web.models.org import Org
from web.models.service import Service
from web.org.repository import get_org_by_code, get_org_list_by_keyword

# Validators & Forms
from web.parser.versions_parser import VersionsParser
from web.tronclass.repository import get_tronclass_services
from web.tronclass.services import build_tronclass_path


class OrgListValidatorForm(BaseForm):
    org_keyword = StringField(default="")

    @property
    def cleaned_org_keyword(self):
        return self.org_keyword.data.strip().lower()


class OrgListBotCommandValidator(LineBotCommandValidator):
    form_cls = OrgListValidatorForm

    @property
    def command_variables(self) -> dict:
        return {
            "org_keyword": self.form.cleaned_org_keyword,
        }


class OrgCodeForm(BaseForm):
    """Org Code Form"""

    org_code = StringField(default="")

    def validate_org_code(self, field):
        from web.models.org import Org
        from sqlalchemy import func

        org = (
            Org.query.with_entities(Org.id)
            .filter(func.lower(Org.code) == self.cleaned_org_code)
            .first()
        )
        if not org:
            raise ValidationError("Invalid org code.")

    @property
    def cleaned_org_code(self):
        return self.org_code.data.strip().lower()


class OrgDetailValidatorForm(OrgCodeForm):
    """Org Detail Validator Form"""


class OrgDetailBotCommandValidator(LineBotCommandValidator):
    form_cls = OrgDetailValidatorForm

    @property
    def command_variables(self) -> dict:
        return {
            "org_code": self.form.cleaned_org_code,
        }


class OrgVersionValidatorForm(OrgCodeForm):
    """Org Version Validator Form"""


class OrgVersionBotCommandValidator(LineBotCommandValidator):
    form_cls = OrgVersionValidatorForm

    @property
    def command_variables(self) -> dict:
        return {
            "org_code": self.form.cleaned_org_code,
        }


class OrgToggleValidatorForm(OrgCodeForm):
    """Org Toggle Validator Form"""


class OrgToggleBotCommandValidator(LineBotCommandValidator):
    form_cls = OrgToggleValidatorForm

    @property
    def command_variables(self) -> dict:
        return {
            "org_code": self.form.cleaned_org_code,
        }


# Commands


class OrgLineBotCommand(LineBotCommand):
    _namespace = CommandNamespaceKey.org.value

    @classmethod
    def execute(cls, **kwargs):
        pass


class OrgListBotCommand(LineBotCommand):
    parent: LineBotCommand = OrgLineBotCommand

    re_patterns: List[str] = [
        "list",
        "(?P<org_keyword>[0-9a-zA-Z-_ \n\r\t]+)?$",
    ]

    validator_cls: Type[LineBotCommandValidator] = OrgListBotCommandValidator

    command_template = "{list}{org_keyword}"

    @classmethod
    def template_variables(cls, **kwargs):
        return {
            "list": cls.transform_text("list"),
            "org_keyword": kwargs.get("org_keyword") or "",
        }

    @classmethod
    def execute(cls, **kwargs) -> TextSendMessage:
        from web.models.org import Org

        org_keyword = kwargs.get("org_keyword") or ""

        fields = [
            Org.id,
            Org.code,
            Org.name,
            Org.public_cloud,
            Org.domain,
            Org.protocol,
        ]
        org_list = get_org_list_by_keyword(org_keyword, fields)

        return TextSendMessage(text=cls.build_org_list_text(org_list))

    @classmethod
    def build_org_list_text(cls, org_list: list) -> str:
        return "\n".join([f"{org.name} ({org.code})" for org in org_list])


class OrgDetailBotCommand(LineBotCommand):
    parent: LineBotCommand = OrgLineBotCommand

    re_patterns: List[str] = [
        "detail",
        " (?P<org_code>[0-9a-zA-Z-_ \n\r\t]+)$",
    ]

    validator_cls: Type[LineBotCommandValidator] = OrgDetailBotCommandValidator

    command_template: str = "{detail} {org_code}"

    @classmethod
    def template_variables(cls, **kwargs) -> dict:
        return {
            "detail": cls.transform_text("detail"),
            "org_code": kwargs.get("org_code") or "",
        }

    @classmethod
    def build_message(cls, org: Org, app_config: dict) -> TemplateSendMessage:
        alt_text = f"Org ({org.code}) Detail"

        button_title = f"{org.name}({org.code})"
        button_text = f"{org.server_address}"
        button_actions = [
            URITemplateAction(
                label="Go to detail page",
                uri=build_frontend_url(app_config, "org_detail", {"org_id": org.id}),
            ),
            MessageTemplateAction(
                label="Check versions",
                text=OrgVersionBotCommand.build_command_text(org_code=org.code),
            ),
            MessageTemplateAction(
                label="Check toggles",
                text=OrgToggleBotCommand.build_command_text(org_code=org.code),
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
    def execute(cls, **kwargs) -> Optional[TemplateSendMessage]:
        org_code = kwargs.get("org_code") or ""
        app_config = kwargs.get("app_config") or {}
        org = get_org_by_code(org_code)
        return None if not org else cls.build_message(org, app_config)


class OrgVersionBotCommand(LineBotCommand):
    parent = LineBotCommand = OrgLineBotCommand

    re_patterns: List[str] = [
        "version",
        " (?P<org_code>[0-9a-zA-Z-_ \n\r\t]+)$",
    ]

    validator_cls = OrgVersionBotCommandValidator

    command_template = "{version} {org_code}"

    @classmethod
    def template_variables(cls, **kwargs):
        return {
            "version": cls.transform_text("version"),
            "org_code": kwargs.get("org_code") or "",
        }

    @classmethod
    def build_message(
        cls,
        result_map: dict,
        error: str,
        services: List[Service],
    ) -> TextSendMessage:
        if not result_map:
            text = f"Some errors are occurred!\n" f"Error:\n" f"{error[:50]}..."
        else:
            text = "\n".join(
                [
                    f"{service.name}: {result_map[service.key]}"
                    for service in services
                    if service.key in result_map
                ]
            ) or "Error!"
        return TextSendMessage(text=text)

    @classmethod
    def execute(cls, **kwargs) -> Optional[Message]:
        org_code = kwargs.get("org_code") or ""
        org = get_org_by_code(org_code)

        parser = VersionsParser(record_id=0, selected_org_ids=[org.id])
        result, error = parser.get_health_result(org)
        result_map = {}
        parser.add_result_to_map(result, result_map)
        services = get_tronclass_services()

        return cls.build_message(result_map, error, services) if org else None


class OrgToggleBotCommand(LineBotCommand):
    parent = LineBotCommand = OrgLineBotCommand

    re_patterns: List[str] = [
        "toggle",
        " (?P<org_code>[0-9a-zA-Z-_ \n\r\t]+)$",
    ]

    validator_cls = OrgToggleBotCommandValidator

    command_template = "{toggle} {org_code}"

    @classmethod
    def template_variables(cls, **kwargs):
        return {
            "toggle": cls.transform_text("toggle"),
            "org_code": kwargs.get("org_code") or "",
        }

    @classmethod
    def build_message(cls, org: Org) -> TemplateSendMessage:
        button_title = f"{org.name}({org.code})"
        button_text = f"{org.server_address}"
        button_actions = [
            URITemplateAction(
                label="Go to toggles page",
                uri=build_tronclass_path(org, "toggle"),
            ),
        ]

        return TemplateSendMessage(
            alt_text="Org Toggles",
            template=ButtonsTemplate(
                title=button_title,
                text=button_text,
                actions=button_actions,
            ),
        )

    @classmethod
    def execute(cls, **kwargs) -> Optional[Message]:
        org_code = kwargs.get("org_code") or ""
        org = get_org_by_code(org_code)

        return cls.build_message(org) if org else None
