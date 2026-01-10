from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

from ..context import UnimindContext


class BrainStructure(Protocol):
    """
    A brain structure takes context and produces updates/artifacts.
    """

    name: str

    def process(self, ctx: UnimindContext, state: Dict[str, Any]) -> Dict[str, Any]:
        ...


@dataclass(frozen=True)
class ThoughtProposal:
    """
    A single candidate action proposal produced by a structure/hemisphere.
    """

    key: str
    action: str
    scores: Dict[str, float]
    rationale: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BrainTrace:
    """
    Debuggable trace of the brain pipeline for a cycle.
    """

    attention: Dict[str, Any] = field(default_factory=dict)
    proposals: List[Dict[str, Any]] = field(default_factory=list)
    selected: Optional[Dict[str, Any]] = None
    notes: Dict[str, Any] = field(default_factory=dict)

