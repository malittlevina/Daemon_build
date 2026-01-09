from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Protocol

from core.kernel_types import KernelMessage, KernelResult


class Subsystem(Protocol):
    name: str

    def handle(self, msg: KernelMessage) -> Optional[KernelResult]: ...

    def tick(self, phase: str) -> None: ...  # optional


@dataclass(slots=True)
class SubsystemRegistry:
    subsystems: Dict[str, Subsystem] = field(default_factory=dict)

    def register(self, name: str, subsystem: Subsystem) -> None:
        self.subsystems[name] = subsystem

    def get(self, name: str) -> Optional[Subsystem]:
        return self.subsystems.get(name)

