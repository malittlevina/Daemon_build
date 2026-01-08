from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Principal:
    """
    Who is requesting an action.
    Keep this minimal; expand later with keys/sessions/attestations.
    """

    id: str
    kind: str  # e.g. "human", "agent", "service", "ui"
    roles: List[str] = field(default_factory=list)

