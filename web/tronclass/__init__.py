from dataclasses import dataclass
from typing import Any, Optional

_end_point_map: Optional["TronClassEndPoint"] = None


@dataclass
class TronClassEndPoint:
    version: str = ""
    toggles: str = ""
    health_check: str = ""

    def get(self, key: str, default: Optional[Any] = None) -> Optional[str]:
        return getattr(self, key, default)


class TronClassEndPointLoader:
    def load(self, endpoint_map: dict) -> TronClassEndPoint:
        return TronClassEndPoint(**endpoint_map)


def init_app(app):
    endpoint_loader = TronClassEndPointLoader()
    globals()["_end_point_map"] = endpoint_loader.load(
        app.config.get("endpoint_map") or {}
    )


def get_tronclass_endpoint() -> TronClassEndPoint:
    return _end_point_map or TronClassEndPoint()
