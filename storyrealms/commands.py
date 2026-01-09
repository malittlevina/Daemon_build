from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True, slots=True)
class ParsedCommand:
    """
    Normalized command structure for Storyrealms UX + bridges.
    """

    name: str
    args: Dict[str, Any]
    realm: Optional[str] = None


def _parse_kv(token: str) -> Tuple[str, Any]:
    if "=" not in token:
        return token, True
    k, v = token.split("=", 1)
    k = k.strip()
    v = v.strip()
    # Basic type coercion
    if v.lower() in ("true", "false"):
        return k, v.lower() == "true"
    try:
        if "." in v:
            return k, float(v)
        return k, int(v)
    except Exception:
        return k, v


def parse_storyrealms_command(text: str) -> Optional[ParsedCommand]:
    """
    Lightweight, deterministic command parser.

    Supported UX forms (examples):
    - realm enter <name>
    - realm state [<name>]
    - realm events [<limit>] [<name>]
    - tick [<delta>]
    - scene set <scene>
    - flag set <key> <value>
    - entity set <entity_id> k=v k=v ...
    - entity show <entity_id>
    - npc list
    - location set <location_id> k=v k=v ...
    - scroll trigger "<scroll name>"
    """

    raw = (text or "").strip()
    if not raw:
        return None

    parts = raw.split()
    if len(parts) < 1:
        return None

    head = parts[0].lower()
    rest = parts[1:]

    if head in ("realm", "world"):
        if not rest:
            return ParsedCommand("realm.help", {})
        verb = rest[0].lower()
        tail = rest[1:]
        if verb == "enter" and tail:
            return ParsedCommand("realm.enter", {"realm": " ".join(tail).strip()})
        if verb == "state":
            realm = " ".join(tail).strip() if tail else None
            return ParsedCommand("realm.state", {"realm": realm} if realm else {})
        if verb == "events":
            args: Dict[str, Any] = {}
            if tail:
                # events <limit> [realm]
                try:
                    args["limit"] = int(tail[0])
                    if len(tail) > 1:
                        args["realm"] = " ".join(tail[1:]).strip()
                except Exception:
                    args["realm"] = " ".join(tail).strip()
            return ParsedCommand("realm.events", args)
        return ParsedCommand("realm.help", {"unknown": verb})

    if head == "tick":
        delta = 1
        if rest:
            try:
                delta = int(rest[0])
            except Exception:
                delta = 1
        return ParsedCommand("time.tick", {"delta": delta})

    if head == "scene" and len(rest) >= 2 and rest[0].lower() == "set":
        return ParsedCommand("scene.set", {"scene": " ".join(rest[1:]).strip()})

    if head == "flag" and len(rest) >= 3 and rest[0].lower() == "set":
        key = rest[1]
        value = " ".join(rest[2:]).strip()
        return ParsedCommand("flag.set", {"key": key, "value": value})

    if head == "entity" and len(rest) >= 3 and rest[0].lower() == "set":
        entity_id = rest[1]
        data: Dict[str, Any] = {}
        for tok in rest[2:]:
            k, v = _parse_kv(tok)
            data[k] = v
        return ParsedCommand("entity.upsert", {"entity_id": entity_id, "data": data})

    if head == "entity" and len(rest) >= 2 and rest[0].lower() == "show":
        entity_id = rest[1]
        return ParsedCommand("entity.show", {"entity_id": entity_id})

    if head == "npc" and rest and rest[0].lower() == "list":
        return ParsedCommand("npc.list", {})

    if head == "location" and len(rest) >= 3 and rest[0].lower() == "set":
        location_id = rest[1]
        data = {}
        for tok in rest[2:]:
            k, v = _parse_kv(tok)
            data[k] = v
        return ParsedCommand("location.upsert", {"location_id": location_id, "data": data})

    if head == "scroll" and len(rest) >= 2 and rest[0].lower() == "trigger":
        name = " ".join(rest[1:]).strip().strip('"').strip("'")
        return ParsedCommand("scroll.trigger", {"name": name, "reason": "storyrealms.ux"})

    return None

