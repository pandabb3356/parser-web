from flask_restful import marshal

from web.api import bp
from web.api.resource_fields import service_fields
from web.api.response_helper import success
from web.models.service import ServiceType, Service


@bp.route("/services")
def get_services():
    services = Service.query.filter(Service.type == ServiceType.TC).all()
    return success({"services": marshal(services, service_fields)})
