from enum import Enum

from web.api_service.base_api_service import BaseApiService
from web.tronclass import get_tronclass_endpoint


class TronClassApiService(BaseApiService):
    def __init__(self, org_code, *args, **kwargs):
        self.org_code = org_code
        super().__init__(*args, **kwargs)

    def get_health_check(self, *args, **kwargs):
        return self.get(get_tronclass_endpoint().health_check, *args, **kwargs)

    def get_version(self, *args, **kwargs):
        return self.get(get_tronclass_endpoint().version, *args, **kwargs)

    def get_toggles(self, *args, **kwargs):
        return self.get(get_tronclass_endpoint().toggles, *args, **kwargs)
