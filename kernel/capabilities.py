from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from kernel.identity import Principal


@dataclass
class CapabilityGrant:
    principal_id: str
    caps: Set[str] = field(default_factory=set)


class CapabilityManager:
    """
    Extremely small capability system:
    - grant/revoke caps by principal_id
    - check requested caps
    """

    def __init__(self):
        self._grants: Dict[str, CapabilityGrant] = {}

    def grant(self, principal: Principal, *caps: str) -> None:
        g = self._grants.get(principal.id) or CapabilityGrant(principal_id=principal.id)
        for c in caps:
            g.caps.add(c)
        self._grants[principal.id] = g

    def revoke(self, principal: Principal, *caps: str) -> None:
        g = self._grants.get(principal.id)
        if not g:
            return
        for c in caps:
            g.caps.discard(c)

    def has_all(self, principal: Principal, required: List[str]) -> bool:
        if not required:
            return True
        g = self._grants.get(principal.id)
        if not g:
            return False
        return all(c in g.caps for c in required)

    def snapshot(self) -> Dict[str, List[str]]:
        return {pid: sorted(list(grant.caps)) for pid, grant in self._grants.items()}

