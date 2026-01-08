from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from kernel.identity import Principal


TaskFn = Callable[[Dict[str, Any], Principal], None]


@dataclass
class ScheduledTask:
    id: str
    name: str
    fn: TaskFn
    args: Dict[str, Any] = field(default_factory=dict)
    principal: Principal = field(default_factory=lambda: Principal(id="kernel", kind="service", roles=["kernel"]))
    next_run_monotonic: float = 0.0
    interval_sec: Optional[float] = None  # if set, repeats


class Scheduler:
    """
    Tick-based scheduler:
    - schedule_once(delay)
    - schedule_every(interval)
    - run_due() from daemon loop
    """

    def __init__(self):
        self._tasks: List[ScheduledTask] = []

    def schedule_once(self, name: str, fn: TaskFn, *, delay_sec: float = 0.0, args: Optional[Dict[str, Any]] = None, principal: Optional[Principal] = None) -> str:
        tid = str(uuid.uuid4())
        self._tasks.append(
            ScheduledTask(
                id=tid,
                name=name,
                fn=fn,
                args=args or {},
                principal=principal or Principal(id="kernel", kind="service", roles=["kernel"]),
                next_run_monotonic=time.monotonic() + max(0.0, delay_sec),
                interval_sec=None,
            )
        )
        return tid

    def schedule_every(self, name: str, fn: TaskFn, *, interval_sec: float, args: Optional[Dict[str, Any]] = None, principal: Optional[Principal] = None, jitter_sec: float = 0.0) -> str:
        tid = str(uuid.uuid4())
        self._tasks.append(
            ScheduledTask(
                id=tid,
                name=name,
                fn=fn,
                args=args or {},
                principal=principal or Principal(id="kernel", kind="service", roles=["kernel"]),
                next_run_monotonic=time.monotonic() + max(0.0, jitter_sec),
                interval_sec=max(0.1, interval_sec),
            )
        )
        return tid

    def run_due(self) -> List[str]:
        now = time.monotonic()
        ran: List[str] = []
        keep: List[ScheduledTask] = []
        for t in self._tasks:
            if t.next_run_monotonic <= now:
                try:
                    t.fn(t.args, t.principal)
                finally:
                    ran.append(t.id)
                if t.interval_sec is not None:
                    t.next_run_monotonic = now + t.interval_sec
                    keep.append(t)
            else:
                keep.append(t)
        self._tasks = keep
        return ran

    def list(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": t.id,
                "name": t.name,
                "next_run_in_sec": max(0.0, t.next_run_monotonic - time.monotonic()),
                "interval_sec": t.interval_sec,
            }
            for t in self._tasks
        ]

