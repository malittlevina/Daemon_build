from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from core.kernel_types import KernelMessage


def _default_caps_for_actor(actor: Optional[str]) -> Set[str]:
    a = (actor or "").strip()
    if not a:
        return set()
    if a in ("cli", "nlu", "http", "RealmInterface", "storyrealm_bridge"):
        return {"world:read", "world:write", "scroll:trigger", "memory:write"}
    if a == "rule_engine":
        return {"world:write", "memory:write"}
    return {"world:read"}


@dataclass(slots=True)
class KernelAuthz:
    """
    Capability-based authorization at the kernel boundary.
    """

    strict: bool = False
    caps_by_actor: Dict[str, Set[str]] = field(default_factory=dict)

    def caps_for(self, actor: Optional[str]) -> Set[str]:
        a = (actor or "").strip()
        if a and a in self.caps_by_actor:
            return set(self.caps_by_actor[a])
        return _default_caps_for_actor(actor)

    def required_caps(self, msg: KernelMessage) -> Set[str]:
        t = msg.type
        if t.startswith("realm.") or t.startswith("world."):
            # reads vs writes
            if t in ("realm.state", "realm.view", "realm.events"):
                return {"world:read"}
            return {"world:write"}
        if t.startswith("scroll."):
            return {"scroll:trigger"}
        if t.startswith("memory."):
            return {"memory:write"}
        return set()

    def authorize(self, msg: KernelMessage) -> Tuple[bool, str]:
        required = self.required_caps(msg)
        if not required:
            return True, "ok"
        granted = self.caps_for(msg.actor)
        if required.issubset(granted):
            return True, "ok"
        if not self.strict and (msg.actor or "").strip():
            # permissive default unless strict mode is enabled
            return True, "ok"
        return False, f"missing caps: {sorted(list(required - granted))}"

