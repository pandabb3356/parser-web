from typing import Any

from flask_sqlalchemy import BaseQuery
from sqlalchemy import func

from web.models.org import Org
from web.query import QueryBuilder, escape_sql_like_query


def _generate_filter_for_keyword(query: BaseQuery, value: Any) -> BaseQuery:
    if len(str(value)) == 0:
        return query

    value = "%{}%".format(escape_sql_like_query(value))

    filters = [
        func.lower(Org.name).like(value),
        func.lower(Org.code).like(value),
    ]
    return query.filter(*filters)


class OrgQueryBuilder(QueryBuilder):
    model_cls = Org

    _filter_func = {
        "keyword": _generate_filter_for_keyword
    }
