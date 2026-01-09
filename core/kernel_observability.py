from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.kernel_types import KernelMessage


@dataclass(slots=True)
class KernelLogger:
    log_path: str = "logs/kernel.log"

    def log(self, level: str, event: str, *, msg: Optional[KernelMessage] = None, extra: Optional[Dict[str, Any]] = None) -> None:
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        record: Dict[str, Any] = {"level": level, "event": event}
        if msg is not None:
            record.update(
                {
                    "msg_id": msg.id,
                    "trace_id": msg.trace_id,
                    "span_id": msg.span_id,
                    "type": msg.type,
                    "subsystem": msg.subsystem,
                    "realm": msg.realm,
                    "actor": msg.actor,
                    "source": msg.source,
                }
            )
        if extra:
            record["extra"] = extra
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

