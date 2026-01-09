from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.kernel_types import KernelMessage, KernelResult
from nlu.nlu_engine import NLUEngine


@dataclass(slots=True)
class NluKernelAdapter:
    nlu: NLUEngine
    name: str = "nlu"

    def handle(self, msg: KernelMessage) -> Optional[KernelResult]:
        if msg.subsystem and msg.subsystem not in ("input", "nlu"):
            return None
        if msg.type != "input.text":
            return None
        text = str((msg.payload or {}).get("text") or "")
        out = self.nlu.interpret(text)
        return KernelResult(ok=True, data={"result": out}, text=str(out) if isinstance(out, str) else None)

