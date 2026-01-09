from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid4())


@dataclass(slots=True)
class KernelMessage:
    """
    Canonical kernel envelope.

    All subsystems should communicate via this message shape.
    """

    type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    subsystem: Optional[str] = None
    realm: Optional[str] = None
    actor: Optional[str] = None
    source: str = "unknown"

    # Observability
    id: str = field(default_factory=_new_id)
    ts: str = field(default_factory=_utc_now_iso)
    trace_id: str = field(default_factory=_new_id)
    span_id: str = field(default_factory=_new_id)

    # Authorization/provenance
    capabilities: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class KernelResult:
    ok: bool = True
    data: Dict[str, Any] = field(default_factory=dict)
    text: Optional[str] = None
    error: Optional[str] = None
    emitted: List[KernelMessage] = field(default_factory=list)

