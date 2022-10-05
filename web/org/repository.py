from typing import Optional, List

from sqlalchemy import func

from web.models.org import Org
from web.org.query import OrgQueryBuilder


def get_org_by_code(code: str) -> Optional[Org]:
    return Org.query.filter(func.lower(Org.code) == code.lower()).first()


def get_org_list_by_keyword(keyword: str, fields: Optional[list] = None) -> List[Org]:
    query_builder = OrgQueryBuilder(fields=fields, conditions={"keyword": keyword})
    return query_builder.build_query().all()
