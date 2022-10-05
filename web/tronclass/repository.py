from typing import List

from web.models.service import Service, ServiceType


def get_tronclass_services(fields=None) -> List[Service]:
    query = Service.query.filter(Service.type == ServiceType.TC)
    if fields:
        query = query.with_entities(*fields)
    return query.all()
