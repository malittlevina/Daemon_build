from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.kernel_types import KernelMessage, KernelResult
from storyrealms.service import StoryrealmsService
from storyrealms.ux_console import StoryrealmsConsole


@dataclass(slots=True)
class StoryrealmsKernelAdapter:
    """
    Kernel adapter for the Storyrealms world engine.
    """

    service: StoryrealmsService
    ux: StoryrealmsConsole
    name: str = "storyrealms"

    def handle(self, msg: KernelMessage) -> Optional[KernelResult]:
        t = msg.type
        if msg.subsystem and msg.subsystem not in ("storyrealms", "input"):
            return None

        # UX: interpret explicit storyrealms commands from input text.
        if t == "input.text":
            text = (msg.payload or {}).get("text") or ""
            out = self.ux.handle(str(text))
            if out is None:
                return None
            return KernelResult(ok=True, text=out, data={"handled_by": "storyrealms.ux"})

        if t == "realm.state":
            return KernelResult(ok=True, data=self.service.query_state(realm=msg.realm))
        if t == "realm.view":
            limit = int((msg.payload or {}).get("limit") or 50)
            return KernelResult(ok=True, data=self.service.get_view(realm=msg.realm, events_limit=limit))
        if t == "realm.events":
            limit = int((msg.payload or {}).get("limit") or 100)
            return KernelResult(ok=True, data=self.service.list_events(realm=msg.realm, limit=limit))
        if t == "realm.event":
            p = msg.payload or {}
            event_type = str(p.get("type") or "")
            payload = p.get("payload") or {}
            return KernelResult(
                ok=True,
                data=self.service.emit_event(
                    event_type,
                    payload if isinstance(payload, dict) else {"value": payload},
                    realm=msg.realm,
                    actor=msg.actor or "kernel",
                    meta={"source": msg.source, "trace_id": msg.trace_id, **(p.get("meta") or {})},
                ),
            )
        if t == "realm.command":
            p = msg.payload or {}
            command = str(p.get("command") or "")
            args = p.get("args") or {}
            return KernelResult(
                ok=True,
                data=self.service.dispatch_command(
                    command,
                    args=args if isinstance(args, dict) else {"value": args},
                    realm=msg.realm,
                    actor=msg.actor or "kernel",
                    meta={"source": msg.source, "trace_id": msg.trace_id, **(p.get("meta") or {})},
                ),
            )

        return None

