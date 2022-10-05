from web import db
from web.api_service import TronClassApiService
from web.parser.base_parser import BaseParser
from web.models.service import Service, ServiceType


class VersionsParser(BaseParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_enabled_service_keys():
        keys = db.session.query(Service.key).filter(Service.type == ServiceType.TC).all()
        return [k[0] for k in keys]

    @classmethod
    def get_health_result(cls, org):
        try:
            api_service = TronClassApiService(org_code=org.code, server_url=org.server_address)
            health_check_response = api_service.get_health_check(timeout=cls.DEFAULT_TIMEOUT, verify=False)
            if health_check_response.ok:
                return health_check_response.json(), None

            error = 'Status Code({}) {}:'.format(health_check_response.status_code, health_check_response.text)
            print(error, flush=True)
            return None, error

        except Exception as ex:
            print(f'Error: {str(ex)}', flush=True)
            return None, f'Error: {str(ex)}'

    @classmethod
    def add_result_to_map(cls, result: dict, result_map: dict):
        if result:
            services = [result] + result.get('dependencies', [])
            for service in services:
                service_name, service_version = service.get('name'), service.get('version')
                result_map[service_name] = service_version

    def fetch_data(self):
        for o_idx, org in enumerate(self.orgs):
            org_service_version_map = {}

            result, error = self.get_health_result(org)
            if not result:
                self.failed_orgs += [(org, error)]
                org_service_version_map['health-check-error'] = str(error)
            else:
                self.add_result_to_map(result, org_service_version_map)

                self.finished_orgs += [org]

            self.add_record_data(data=org_service_version_map, org_id=org.id)

            import time
            time.sleep(1)

            self.update_record_completeness()
            db.session.commit()

        self.record.completeness = 100
        db.session.commit()
