from typing import Type, Optional, Dict, Callable, List

from flask_sqlalchemy import BaseQuery

from web.database import db
from web.util import remove_emoji


def escape_sql_like_query(value):
    if len(value) == 0:
        return remove_emoji(value)
    return remove_emoji(value).replace("%", r"\%").replace("_", r"\_")


class QueryBuilder:
    model_cls: Optional[Type[db.Model]] = None

    _filter_func: Dict[str, Callable] = {}

    default_page_settings: dict = {
        "page": 1,
        "page_size": 10,
        "with_page": False,
    }

    def __init__(
        self,
        fields: Optional[List[db.Column]],
        conditions: Optional[dict] = None,
        page_settings: Optional[dict] = None,
    ):
        if self.model_cls is None:
            raise NotImplementedError("Model class is not declared")

        self.base_query: BaseQuery = self.model_cls.query
        self.fields: List[db.Column] = fields or []
        self.conditions = conditions

        self.page_settings = self.init_page_settings(page_settings or {})

    def init_page_settings(self, page_settings: dict) -> dict:
        settings = self.default_page_settings.copy()
        settings.update(page_settings)
        return settings

    @classmethod
    def query_with_filters(
        cls, query: BaseQuery, filter_func: dict, conditions: Optional[dict] = None
    ):
        conditions = conditions or {}

        if not conditions:
            return query

        for key in conditions:
            func = filter_func.get(key, None)
            if func is not None:
                query = func(query, conditions[key])

        return query

    @classmethod
    def query_with_pagination(cls, query: BaseQuery, page, page_size) -> BaseQuery:
        return query.paginate(page, page_size, False).query

    def build_query(self) -> BaseQuery:
        query = self.base_query

        # query fields
        if self.fields:
            query = query.with_entities(*self.fields)

        # query with filters
        if self._filter_func:
            query = self.query_with_filters(
                query,
                self._filter_func,
                self.conditions,
            )

        # query with pagination
        if self.page_settings["with_page"]:
            query = self.query_with_pagination(
                query,
                self.page_settings["page"],
                self.page_settings["page_size"],
            )

        return query
