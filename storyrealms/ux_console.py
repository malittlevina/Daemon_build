from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from storyrealms.commands import parse_storyrealms_command
from storyrealms.service import StoryrealmsService


def _fmt_kv(d: Dict[str, Any], *, indent: int = 2) -> str:
    pad = " " * indent
    if not d:
        return f"{pad}(none)"
    lines = []
    for k in sorted(d.keys()):
        v = d[k]
        lines.append(f"{pad}{k}: {v}")
    return "\n".join(lines)


def _truncate(s: str, n: int = 140) -> str:
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


@dataclass(slots=True)
class StoryrealmsConsole:
    """
    Simple UX layer for interactive CLI usage.

    Returns strings to print, or None when the input isn't a Storyrealms command.
    """

    engine: StoryrealmsService

    def handle(self, user_input: str) -> Optional[str]:
        cmd = parse_storyrealms_command(user_input)
        if cmd is None:
            return None

        name = cmd.name
        args = cmd.args or {}

        if name == "realm.help":
            return (
                "Storyrealms commands:\n"
                "  realm enter <name>\n"
                "  realm state [name]\n"
                "  realm events [limit] [name]\n"
                "  realm view\n"
                "  tick [delta]\n"
                "  scene set <scene>\n"
                "  flag set <key> <value>\n"
                "  entity set <id> k=v k=v ...\n"
                "  entity show <id>\n"
                "  npc list\n"
                "  npc goal add <npc_id> <goal>\n"
                "  location set <id> k=v k=v ...\n"
                "  scroll trigger <scroll name>\n"
            )

        if name == "realm.enter":
            realm = str(args.get("realm") or "default")
            out = self.engine.enter_realm(realm, actor="cli")
            return f"[Storyrealms] entered realm: {out.get('realm')}"

        if name == "realm.state":
            realm = args.get("realm")
            out = self.engine.query_state(realm=realm)
            s = out["state"]
            return (
                f"[Storyrealms] realm: {out['realm']}\n"
                f"  time: {s.get('time')}\n"
                f"  scene: {s.get('current_scene')}\n"
                f"  flags:\n{_fmt_kv(s.get('flags') or {}, indent=4)}\n"
                f"  entities: {len(s.get('entities') or {})}\n"
                f"  locations: {len(s.get('locations') or {})}\n"
            )

        if name == "realm.view":
            out = self.engine.get_view(events_limit=50)
            v = out["view"]
            return (
                f"[Storyrealms] view: realm={out['realm']}\n"
                f"  scene: {v.get('scene', {}).get('current')}\n"
                f"  time: {v.get('time', {}).get('tick')}\n"
                f"  counts: {v.get('counts')}\n"
                f"  npcs: {len(v.get('npcs') or [])}\n"
                f"  timeline: {len(v.get('timeline') or [])}\n"
            )

        if name == "entity.show":
            entity_id = str(args.get("entity_id") or "")
            out = self.engine.query_state()
            s = out["state"]
            ent = (s.get("entities") or {}).get(entity_id)
            if ent is None:
                return f"[Storyrealms] entity not found: {entity_id}"
            if not isinstance(ent, dict):
                return f"[Storyrealms] entity {entity_id}: {ent}"
            return f"[Storyrealms] entity {entity_id}:\n{_fmt_kv(ent, indent=2)}"

        if name == "npc.list":
            out = self.engine.query_state()
            s = out["state"]
            entities = s.get("entities") or {}
            npc_ids = []
            for eid, data in entities.items():
                if isinstance(data, dict) and (data.get("kind") == "npc" or str(eid).startswith("npc:")):
                    npc_ids.append(eid)
            npc_ids = sorted(npc_ids)
            if not npc_ids:
                return "[Storyrealms] no NPCs"
            lines = [f"[Storyrealms] NPCs ({len(npc_ids)}):"]
            for eid in npc_ids:
                d = entities.get(eid) or {}
                if isinstance(d, dict):
                    lines.append(f"  - {eid}: name={d.get('name')} mood={d.get('mood')}")
                else:
                    lines.append(f"  - {eid}: {d}")
            return "\n".join(lines)

        if name == "realm.events":
            limit = args.get("limit", 50)
            realm = args.get("realm")
            out = self.engine.list_events(realm=realm, limit=limit)
            lines = [f"[Storyrealms] events (realm={out['realm']}, n={len(out['events'])}):"]
            for e in out["events"]:
                lines.append(
                    f"  - {e.get('ts')} :: {e.get('type')} "
                    f"(id={str(e.get('id'))[:8]}) payload={_truncate(str(e.get('payload') or {}), 120)}"
                )
            return "\n".join(lines)

        if name == "time.tick":
            delta = int(args.get("delta") or 1)
            self.engine.tick(delta, actor="cli")
            return f"[Storyrealms] ticked +{delta}"

        if name in ("scene.set", "flag.set", "entity.upsert", "location.upsert", "scroll.trigger", "npc.goal.set"):
            self.engine.emit_event(name, dict(args), actor="cli")
            return f"[Storyrealms] ok: {name}"

        # Fallback: emit generic command event
        self.engine.dispatch_command(name, args=dict(args), actor="cli")
        return f"[Storyrealms] dispatched: {name}"

