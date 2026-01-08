from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, TypeVar


T = TypeVar("T")


@dataclass(slots=True)
class SubsystemRegistry:
    """
    Named registry for runtime subsystem instances.

    This is the kernel's "service locator": subsystems remain decoupled, while
    still being discoverable by agents/tools that operate through the kernel.
    """

    _items: dict[str, Any] = field(default_factory=dict)

    def register(self, name: str, subsystem: Any) -> None:
        self._items[name] = subsystem

    def get(self, name: str, default: Optional[T] = None) -> Any | T:
        return self._items.get(name, default)

    def require(self, name: str) -> Any:
        if name not in self._items:
            raise KeyError(f"Subsystem not registered: {name}")
        return self._items[name]

    def list(self) -> list[str]:
        return sorted(self._items.keys())

