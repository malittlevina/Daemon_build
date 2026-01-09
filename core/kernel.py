from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4

from core.kernel_bus import KernelBus
from core.kernel_caps import KernelAuthz
from core.kernel_observability import KernelLogger
from core.kernel_registry import SubsystemRegistry
from core.kernel_scheduler import KernelScheduler
from core.kernel_types import KernelMessage, KernelResult


def _new_id() -> str:
    return str(uuid4())


@dataclass(slots=True)
class Kernel:
    """
    Kernel orchestrator: single routing point.
    """

    bus: KernelBus = field(default_factory=KernelBus)
    authz: KernelAuthz = field(default_factory=KernelAuthz)
    registry: SubsystemRegistry = field(default_factory=SubsystemRegistry)
    scheduler: KernelScheduler = field(init=False)
    logger: KernelLogger = field(default_factory=KernelLogger)

    def __post_init__(self) -> None:
        self.scheduler = KernelScheduler(self.registry)

    def register(self, name: str, subsystem) -> None:
        self.registry.register(name, subsystem)

        def _filt(msg: KernelMessage) -> bool:
            # Explicit subsystem match
            if msg.subsystem and msg.subsystem == name:
                return True
            # Otherwise, allow subsystem to self-select in handle().
            return True

        def _handler(msg: KernelMessage) -> Optional[KernelResult]:
            return subsystem.handle(msg)

        self.bus.subscribe(_filt, _handler)

    def _route_hint(self, msg: KernelMessage) -> str:
        t = msg.type
        if t.startswith("realm.") or t.startswith("world."):
            return "storyrealms"
        if t.startswith("scroll."):
            return "scrolls"
        if t.startswith("memory."):
            return "memory"
        if t == "input.text":
            return "input"
        return "misc"

    def handle(self, msg: KernelMessage) -> KernelResult:
        # Ensure trace/span IDs exist.
        if not msg.trace_id:
            msg.trace_id = _new_id()
        if not msg.span_id:
            msg.span_id = _new_id()

        ok, reason = self.authz.authorize(msg)
        if not ok:
            self.logger.log("warn", "authz.denied", msg=msg, extra={"reason": reason})
            return KernelResult(ok=False, error=reason)

        self.logger.log("info", "msg.in", msg=msg, extra={"route_hint": self._route_hint(msg)})
        results = self.bus.publish(msg)

        # Choose the first successful handler response; otherwise return merged failure.
        for r in results:
            if r.ok:
                if r.emitted:
                    for e in r.emitted:
                        self.handle(e)
                self.logger.log("info", "msg.out", msg=msg, extra={"ok": True})
                return r

        if results:
            err = "; ".join([r.error or "handler failed" for r in results if not r.ok])[:800]
            self.logger.log("error", "msg.out", msg=msg, extra={"ok": False, "error": err})
            return KernelResult(ok=False, error=err)

        self.logger.log("warn", "msg.unhandled", msg=msg)
        return KernelResult(ok=False, error="unhandled")

    def tick(self) -> None:
        self.scheduler.tick()

    def handle_text(self, text: str, *, actor: str = "cli", source: str = "cli") -> KernelResult:
        return self.handle(
            KernelMessage(
                type="input.text",
                subsystem="input",
                actor=actor,
                source=source,
                payload={"text": text},
            )
        )

