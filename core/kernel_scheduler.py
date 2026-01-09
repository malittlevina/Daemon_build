from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from core.kernel_registry import SubsystemRegistry


@dataclass(slots=True)
class KernelScheduler:
    """
    Deterministic phase scheduler.
    """

    registry: SubsystemRegistry
    phases: List[str] = field(
        default_factory=lambda: [
            "INGEST",
            "INTERPRET",
            "DECIDE",
            "ACT",
            "INTEGRATE",
            "OBSERVE",
        ]
    )

    def tick(self) -> None:
        for phase in self.phases:
            for subsystem in list(self.registry.subsystems.values()):
                tick_fn = getattr(subsystem, "tick", None)
                if callable(tick_fn):
                    try:
                        tick_fn(phase)
                    except Exception:
                        # Fault containment: scheduler continues even if a subsystem errors.
                        continue

