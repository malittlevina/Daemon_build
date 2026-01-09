from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.kernel_types import KernelMessage, KernelResult
from scrolls.scroll_engine import ScrollEngine
from scrolls.trigger_manager import trigger_scroll


@dataclass(slots=True)
class ScrollsKernelAdapter:
    engine: ScrollEngine
    name: str = "scrolls"

    def handle(self, msg: KernelMessage) -> Optional[KernelResult]:
        if msg.subsystem and msg.subsystem != "scrolls":
            return None

        if msg.type == "scroll.trigger":
            name = str((msg.payload or {}).get("name") or "")
            reason = str((msg.payload or {}).get("reason") or msg.source or "kernel")
            trigger_scroll(name, reason=reason)
            return KernelResult(ok=True, data={"status": "triggered", "scroll": name})

        if msg.type == "scroll.invoke":
            name = str((msg.payload or {}).get("name") or "")
            args = (msg.payload or {}).get("args") or []
            kwargs = (msg.payload or {}).get("kwargs") or {}
            if not isinstance(args, list):
                args = [args]
            if not isinstance(kwargs, dict):
                kwargs = {"value": kwargs}
            out = self.engine.invoke(name, *args, **kwargs)
            return KernelResult(ok=True, data={"result": out})

        return None

