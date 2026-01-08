from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .bus import EventBus
from .messages import KernelEvent
from .registry import SubsystemRegistry
from .scheduler import KernelScheduler


@dataclass(slots=True)
class KernelResult:
    output: str
    handled: bool = True


class Kernel:
    """
    ThothOS kernel coordinator for the daemon build.

    Responsibilities:
    - Maintain shared context (registry)
    - Route events (bus)
    - Run cooperative jobs (scheduler)
    - Provide a single entrypoint for user input handling
    """

    def __init__(
        self,
        *,
        unimind: Optional[Any] = None,
        scrolls: Optional[Any] = None,
        emotions: Optional[Any] = None,
        memory: Optional[Any] = None,
        nlu: Optional[Any] = None,
        bridge: Optional[Any] = None,
    ) -> None:
        self.registry = SubsystemRegistry()
        self.bus = EventBus()
        self.scheduler = KernelScheduler()

        if unimind is not None:
            self.registry.register("unimind", unimind)
        if scrolls is not None:
            self.registry.register("scrolls", scrolls)
        if emotions is not None:
            self.registry.register("emotions", emotions)
        if memory is not None:
            self.registry.register("memory", memory)
        if nlu is not None:
            self.registry.register("nlu", nlu)
        if bridge is not None:
            self.registry.register("bridge", bridge)

    def boot(self) -> None:
        """
        Attach basic kernel jobs and observers.
        """

        def _log_event(ev: KernelEvent) -> None:
            mem = self.registry.get("memory")
            if mem is None:
                return
            # MemoryLogger API
            if hasattr(mem, "log_event"):
                mem.log_event("kernel_event", {"type": ev.type, "payload": dict(ev.payload)}, context={"source": ev.source})

        # Observe all events for memory trace (best-effort).
        self.bus.subscribe("*", _log_event)

        # Tick scroll monitor if present (lightweight).
        scrolls = self.registry.get("scrolls")
        if scrolls is not None and hasattr(scrolls, "monitor_scrolls"):
            self.scheduler.register_interval("scrolls.monitor", 2.0, lambda: scrolls.monitor_scrolls())

    def tick(self) -> None:
        self.scheduler.tick()

    def handle_input(self, text: str) -> KernelResult:
        text = (text or "").strip()
        self.bus.publish(
            "nlu.input",
            KernelEvent(type="nlu.input", payload={"text": text}, source="cli"),
        )

        if not text:
            # Treat empty input as reflection request.
            unimind = self.registry.get("unimind")
            if unimind is not None and hasattr(unimind, "reflect"):
                try:
                    unimind.reflect()
                except Exception as e:
                    return KernelResult(output=f"[Kernel] Reflection failed: {e}", handled=True)
            return KernelResult(output="[Kernel] Idle tick.", handled=True)

        # Emotion update (best-effort).
        emotions = self.registry.get("emotions")
        if emotions is not None:
            try:
                if hasattr(emotions, "update_emotion"):
                    emotions.update_emotion(text)
            except Exception:
                pass

        # Primary route: NLU -> intent/result.
        nlu = self.registry.get("nlu")
        if nlu is not None and hasattr(nlu, "interpret"):
            try:
                out = nlu.interpret(text)
                if out:
                    out_s = str(out)
                    if not out_s.startswith("[NLUEngine] No known intent"):
                        return KernelResult(output=out_s, handled=True)
            except Exception as e:
                self.bus.publish(
                    "nlu.error",
                    KernelEvent(type="nlu.error", payload={"error": str(e)}, source="kernel"),
                )

        # Secondary route: direct scroll invocation by name.
        scrolls = self.registry.get("scrolls")
        if scrolls is not None and hasattr(scrolls, "invoke"):
            try:
                # Common pattern: user types exact scroll name.
                out = scrolls.invoke(text)
                if out is not None:
                    return KernelResult(output=str(out), handled=True)
            except Exception:
                pass

        # Tertiary route: update symbolic state.
        try:
            from lam.symbolic_state import update_state_with_input

            update_state_with_input(text)
            return KernelResult(output="[Kernel] State updated.", handled=True)
        except Exception as e:
            return KernelResult(output=f"[Kernel] No route for input. Error: {e}", handled=False)

