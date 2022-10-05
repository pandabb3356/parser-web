from typing import Optional, List, Tuple

FRONTEND_SETTINGS_KEY = "FRONTEND_SETTINGS"


def get_frontend_settings(app_config: dict) -> dict:
    return app_config.get(f"{FRONTEND_SETTINGS_KEY}") or {}


def get_frontend_host(app_config: dict) -> str:
    return get_frontend_settings(app_config).get("host_name")


def build_frontend_url(
    app_config: dict,
    endpoint_key: str,
    endpoint_variables: Optional[dict] = None,
    query_strings: Optional[List[Tuple[str, str]]] = None,
) -> str:
    settings = get_frontend_settings(app_config)

    host_name = get_frontend_host(app_config)
    endpoint_map = settings.get("endpoint") or {}

    endpoint = endpoint_map.get(endpoint_key)
    if endpoint_variables:
        endpoint = endpoint.format(**endpoint_variables)

    url = f"{host_name}#{endpoint}"
    if query_strings:
        qs = "&".join([f"{k}={v}" for k, v in query_strings])
        url += f"?{qs}"
    return url
