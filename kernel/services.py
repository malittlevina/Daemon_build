from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol


class Service(Protocol):
    """
    Kernel service contract.
    Services may optionally implement any of these.
    """

    name: str

    def start(self) -> None: ...

    def stop(self) -> None: ...

    def health(self) -> Dict[str, Any]: ...

    def state(self) -> Dict[str, Any]: ...


@dataclass(frozen=True)
class ServiceInfo:
    name: str
    kind: str
    provides: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)


class ServiceRegistry:
    def __init__(self):
        self._services: Dict[str, Service] = {}
        self._info: Dict[str, ServiceInfo] = {}

    def register(self, info: ServiceInfo, svc: Service) -> None:
        self._services[info.name] = svc
        self._info[info.name] = info

    def get(self, name: str) -> Optional[Service]:
        return self._services.get(name)

    def list(self) -> List[ServiceInfo]:
        return list(self._info.values())

