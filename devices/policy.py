from __future__ import annotations

from typing import Any, Callable

from devices.events import DeviceEvent


PolicyHandler = Callable[[DeviceEvent], None]


class DevicePolicyEngine:
    """
    Agent-native policy layer.

    For now this is a simple handler registry. As the OS evolves, this can become:
    - a rule DSL
    - a learned policy model
    - a trust-gated action planner that emits scrolls/tasks
    """

    def __init__(self):
        self._handlers: list[PolicyHandler] = []

    def register_handler(self, handler: PolicyHandler) -> None:
        self._handlers.append(handler)

    def handle(self, event: DeviceEvent) -> None:
        for handler in list(self._handlers):
            try:
                handler(event)
            except Exception:
                # Policy failures must never kill the daemon.
                continue


def summarize_event(event: DeviceEvent) -> str:
    p = event.passport
    ident = p.identity or {}
    ip = ident.get("ip")
    mac = ident.get("mac")
    usn = ident.get("usn")

    parts: list[str] = [event.kind, f"id={p.device_id}", f"source={p.source}"]
    if ip:
        parts.append(f"ip={ip}")
    if mac:
        parts.append(f"mac={mac}")
    if usn:
        parts.append(f"usn={usn}")
    if p.capabilities:
        parts.append("caps=" + ",".join(sorted(p.capabilities))[:200])
    return " ".join(parts)

