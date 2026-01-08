from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass(slots=True)
class ScheduledJob:
    name: str
    interval_s: float
    fn: Callable[[], object]
    next_run_at: float = field(default_factory=lambda: time.time())
    enabled: bool = True
    last_error: Optional[str] = None


class KernelScheduler:
    """
    Cooperative, tick-driven scheduler.

    The daemon currently runs a CLI loop; this scheduler is designed to run
    inside that loop (no background threads required).
    """

    def __init__(self) -> None:
        self._jobs: dict[str, ScheduledJob] = {}

    def register_interval(self, name: str, interval_s: float, fn: Callable[[], object]) -> None:
        if interval_s <= 0:
            raise ValueError("interval_s must be > 0")
        self._jobs[name] = ScheduledJob(name=name, interval_s=interval_s, fn=fn)

    def enable(self, name: str, enabled: bool = True) -> None:
        if name in self._jobs:
            self._jobs[name].enabled = enabled

    def tick(self) -> None:
        now = time.time()
        for job in list(self._jobs.values()):
            if not job.enabled:
                continue
            if now < job.next_run_at:
                continue
            try:
                job.fn()
                job.last_error = None
            except Exception as e:  # pragma: no cover - containment by design
                job.last_error = str(e)
                print(f"[KernelScheduler] Job '{job.name}' failed: {e}")
            finally:
                job.next_run_at = now + job.interval_s

