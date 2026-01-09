from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from storyrealms.commands import ParsedCommand, parse_storyrealms_command
from storyrealms.service import StoryrealmsService


@dataclass(slots=True)
class StoryrealmsRouter:
    """
    Command router for agent/user inputs into realm events.

    This is the "next layer" above raw event emission:
    - parses UX/bridge strings into normalized commands
    - chooses event types and payloads
    - keeps policy centralized (what commands are allowed, how they map)
    """

    engine: StoryrealmsService

    def dispatch_text(self, text: str, *, actor: Optional[str] = None, realm: Optional[str] = None) -> Optional[Dict[str, Any]]:
        cmd = parse_storyrealms_command(text)
        if cmd is None:
            return None
        return self.dispatch(cmd, actor=actor, realm=realm)

    def dispatch(self, cmd: ParsedCommand, *, actor: Optional[str] = None, realm: Optional[str] = None) -> Dict[str, Any]:
        actor = actor or "router"
        target_realm = realm or cmd.realm or self.engine.current_realm

        if cmd.name == "realm.enter":
            realm_name = str(cmd.args.get("realm") or "default")
            return self.engine.enter_realm(realm_name, actor=actor)

        if cmd.name == "realm.state":
            return self.engine.query_state(realm=cmd.args.get("realm") or target_realm)

        if cmd.name == "realm.events":
            return self.engine.list_events(
                realm=cmd.args.get("realm") or target_realm,
                limit=cmd.args.get("limit", 100),
            )

        if cmd.name == "time.tick":
            return self.engine.tick(int(cmd.args.get("delta") or 1), realm=target_realm, actor=actor)

        if cmd.name == "entity.show":
            entity_id = str(cmd.args.get("entity_id") or "")
            state = self.engine.query_state(realm=target_realm)["state"]
            ent = (state.get("entities") or {}).get(entity_id)
            return {"realm": target_realm, "entity_id": entity_id, "entity": ent}

        if cmd.name == "npc.list":
            state = self.engine.query_state(realm=target_realm)["state"]
            entities = state.get("entities") or {}
            npc_ids = []
            for eid, data in entities.items():
                if isinstance(data, dict) and (data.get("kind") == "npc" or str(eid).startswith("npc:")):
                    npc_ids.append(eid)
            npc_ids = sorted(npc_ids)
            return {"realm": target_realm, "npcs": [{"id": eid, **(entities.get(eid) or {})} for eid in npc_ids]}

        # Default mapping: emit the command name as event type.
        return self.engine.emit_event(cmd.name, dict(cmd.args), realm=target_realm, actor=actor)

