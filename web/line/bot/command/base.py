import re
from typing import Optional, Dict, List, re as re_type, Type

from web.form import BaseForm

CommandTextMapper = Dict[str, str]
CommandValidateErrors = Dict[str, List[str]]


class LineBotCommandMeta(type):
    """
    The metaclass for `LineBotCommand` and any subclasses of `LineBotCommand`.

    `LineBotCommandMeta`'s responsibility is to build `namespace` and `re_pattern`.

    """

    @property
    def namespace(cls):
        namespaces = []

        parent = cls
        while parent is not None:
            ns_key = getattr(parent, "_namespace", "")
            namespaces += [
                cls.transform_text(ns_key),
            ]
            parent = parent.parent

        namespaces.reverse()

        return "".join(namespaces)

    @property
    def re_pattern(cls) -> re_type:
        namespace: str = cls.namespace

        pattern_str_list: List[str] = []

        re_patterns: List[str] = cls.get_re_patterns()
        for pattern_key in re_patterns:
            pattern_str_list += [
                cls.transform_text(pattern_key),
            ]

        pattern_str = "".join(pattern_str_list)
        return re.compile(
            fr"{namespace}{cls.get_namespace_pattern_splitter()}{pattern_str}", re.I
        )

    def get_re_patterns(cls) -> List[str]:
        return getattr(cls, "re_patterns", [])

    def get_text_mapper(cls) -> CommandTextMapper:
        return getattr(cls, "text_mapper", {}) or {}

    def get_parent(cls) -> Optional["LineBotCommand"]:
        return getattr(cls, "parent", None)

    def get_children(cls) -> List["LineBotCommand"]:
        return getattr(cls, "children", [])

    def search(cls, text: str) -> Optional[re_type]:
        return cls.re_pattern.search(text)

    def get_namespace_pattern_splitter(cls) -> str:
        return getattr(cls, "namespace_pattern_splitter", " ")

    def transform_text(cls, text_key: str) -> str:
        return cls.get_text_mapper().get(text_key) or text_key


class LineBotCommandValidator:
    """
    Declarative LineBotCommandValidator base class.
    """

    form_cls: Type[BaseForm] = BaseForm

    def __init__(self, **kwargs):
        self.form: BaseForm = self.form_cls.from_json(kwargs)

    def validate(self) -> bool:
        return self.form.validate()

    @property
    def errors(self):
        return self.form.errors

    @property
    def command_variables(self) -> dict:
        return {}


class LineBotCommand(metaclass=LineBotCommandMeta):
    """
    Declarative LineBotCommand base class.

    """

    _namespace: str = ""

    re_patterns: List[str] = []

    namespace_pattern_splitter: str = " "

    text_mapper: CommandTextMapper = {}

    parent: Optional["LineBotCommand"] = None

    children: List["LineBotCommand"] = []

    validator_cls: Type[LineBotCommandValidator] = LineBotCommandValidator

    command_template: str = ""

    should_login: bool = True

    @classmethod
    def register_text_mapper(cls, text_mapper: dict):
        cls.text_mapper = text_mapper

    def validate_command(self, result: re.Match) -> Optional[LineBotCommandValidator]:
        command_variables = result.groupdict()

        if not self.validator_cls:
            return

        validator = self.validator_cls(**command_variables)
        if not validator.validate():
            return

        return validator

    @property
    def re_pattern(self) -> re_type:
        return self.__class__.re_pattern

    @property
    def namespace(self) -> str:
        return getattr(self.__class__, "namespace", "")

    @classmethod
    def execute(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def template_variables(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def build_command_text(cls, **kwargs) -> str:
        template_variables = cls.template_variables(**kwargs)
        return f"{cls.namespace} {cls.command_template.format(**template_variables)}"
