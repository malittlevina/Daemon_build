from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set, Tuple
from uuid import uuid4

from storyrealms.events import RealmEvent


def _default_actor_role(actor: Optional[str]) -> str:
    a = (actor or "").strip()
    if not a:
        return "unknown"
    if a in ("cli", "nlu", "RealmInterface", "storyrealm_bridge"):
        return "user_agent"
    if a == "rule_engine":
        return "system"
    return "unknown"


@dataclass(slots=True)
class PolicyEngine:
    """
    Authorization + provenance for realm events.

    - authorizes by (actor role, event type)
    - enriches meta with provenance fields for audit/replay analysis
    """

    allow_by_role: Dict[str, Set[str]] = field(
        default_factory=lambda: {
            # User-facing agents can mutate most world state.
            "user_agent": {
                "realm.entered",
                "time.tick",
                "scene.set",
                "flag.set",
                "entity.upsert",
                "location.upsert",
                "relationship.adjust",
                "npc.goal.set",
                "scroll.trigger",
                "command.dispatched",
            },
            # System rules can emit derived world events.
            "system": {
                "entity.upsert",
                "npc.intent",
                "npc.act",
                "npc.plan.set",
                "npc.plan.advance",
                "relationship.adjust",
                "flag.set",
                "scene.set",
                "narrative.beat",
            },
            "unknown": set(),
        }
    )
    strict: bool = False

    def authorize(self, ev: RealmEvent) -> Tuple[bool, str]:
        role = _default_actor_role(ev.actor)
        if role == "unknown" and not self.strict and (ev.actor or "").strip():
            # Default to permissive for non-empty actors unless strict mode is enabled.
            role = "user_agent"
        allowed = self.allow_by_role.get(role, set())
        if ev.type in allowed:
            return True, "ok"
        return False, f"denied: role={role} type={ev.type}"

    def enrich_meta(self, meta: Dict[str, Any], *, actor: Optional[str], source: str) -> Dict[str, Any]:
        out = dict(meta or {})
        out.setdefault("source", source)
        out.setdefault("actor_role", _default_actor_role(actor))
        out.setdefault("intent_id", str(uuid4()))
        return out

