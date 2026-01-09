from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class UnimindSignals:
    """
    Normalized signals from subsystems for a single cycle.

    This intentionally stays schema-light (dict-first) because many subsystems
    in this repo are placeholders and evolve quickly.
    """

    emotion: Dict[str, Any] = field(default_factory=dict)
    memory: Dict[str, Any] = field(default_factory=dict)
    ethics: Dict[str, Any] = field(default_factory=dict)
    language: Dict[str, Any] = field(default_factory=dict)
    logic: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UnimindContext:
    """
    The shared, agent-native context object passed across subsystems.

    - `input_text` is the raw user input (if any)
    - `intent` is an optional interpreted intent label/structure from NLU
    - `symbolic_state` is a snapshot of LAM state (if available)
    - `signals` contains normalized subsystem observations
    - `notes` contains ephemeral reasoning notes and intermediate artifacts
    """

    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    input_text: Optional[str] = None
    intent: Optional[Any] = None
    symbolic_state: Dict[str, Any] = field(default_factory=dict)
    signals: UnimindSignals = field(default_factory=UnimindSignals)
    notes: Dict[str, Any] = field(default_factory=dict)

    def with_note(self, key: str, value: Any) -> "UnimindContext":
        merged = dict(self.notes)
        merged[key] = value
        return UnimindContext(
            timestamp=self.timestamp,
            input_text=self.input_text,
            intent=self.intent,
            symbolic_state=dict(self.symbolic_state),
            signals=self.signals,
            notes=merged,
        )


@dataclass(frozen=True)
class UnimindPlan:
    """
    A minimal plan representation: what to do next + why.
    """

    action: str
    rationale: str
    score: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConceptGraph:
    """
    Lightweight concept graph suitable for symbolic expansion.
    """

    seed: str
    nodes: List[str]
    edges: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
