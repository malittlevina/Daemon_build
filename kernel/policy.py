from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from core.event_bus import EventBus
from kernel.identity import Principal


@dataclass
class PolicyDecision:
    allow: bool
    reason: str
    obligations: Dict[str, Any] = field(default_factory=dict)


class PolicyEngine:
    """
    Minimal policy gate:
    - allow/deny based on roles + action tags + required caps (caps are checked elsewhere)
    - emits audit events for decisions
    """

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._deny_tags_for_roles: List[Tuple[str, str]] = []
        # Example: ("ui", "danger") would deny principals with role "ui" from "danger"-tagged actions.

    def add_role_tag_deny(self, role: str, tag: str) -> None:
        self._deny_tags_for_roles.append((role, tag))

    def decide(self, *, principal: Principal, action: str, tags: List[str], trace_id: Optional[str] = None) -> PolicyDecision:
        for role, tag in self._deny_tags_for_roles:
            if role in principal.roles and tag in tags:
                d = PolicyDecision(allow=False, reason=f"role '{role}' denied for tag '{tag}'")
                self._audit(principal, action, d, trace_id=trace_id)
                return d

        d = PolicyDecision(allow=True, reason="allowed")
        self._audit(principal, action, d, trace_id=trace_id)
        return d

    def _audit(self, principal: Principal, action: str, decision: PolicyDecision, *, trace_id: Optional[str]) -> None:
        payload: Dict[str, Any] = {
            "principal": {"id": principal.id, "kind": principal.kind, "roles": principal.roles},
            "action": action,
            "allow": decision.allow,
            "reason": decision.reason,
        }
        if trace_id:
            payload["trace_id"] = trace_id
        self._event_bus.publish(
            "policy.decision",
            payload,
            source="kernel",
            severity="info" if decision.allow else "error",
            tags=["policy"] + ([f"trace:{trace_id}"] if trace_id else []),
        )

