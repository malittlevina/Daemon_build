from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.kernel_types import KernelMessage, KernelResult
from memory_tree.memory_logger import MemoryLogger


@dataclass(slots=True)
class MemoryKernelAdapter:
    logger: MemoryLogger
    name: str = "memory"

    def handle(self, msg: KernelMessage) -> Optional[KernelResult]:
        if msg.subsystem and msg.subsystem != "memory":
            return None
        if msg.type == "memory.log":
            p = msg.payload or {}
            content = str(p.get("content") or "")
            context = p.get("context")
            self.logger.log_event("memory", content, context=context)
            return KernelResult(ok=True, data={"status": "logged"})
        if msg.type == "memory.query":
            count = int((msg.payload or {}).get("count") or 50)
            return KernelResult(ok=True, data={"events": self.logger.get_latest_events(count)})
        return None

