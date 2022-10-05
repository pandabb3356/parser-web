from web.models.org import Org
from web.tronclass import TronClassEndPoint, get_tronclass_endpoint


def build_tronclass_path(org: Org, path_key: str) -> str:
    endpoint: TronClassEndPoint = get_tronclass_endpoint()
    path = endpoint.get(path_key) or ""
    return f"{org.server_address}/{path}"
