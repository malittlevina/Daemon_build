from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Iterator, List, Optional

from storyrealms.events import RealmEvent
from storyrealms.state import RealmState


def _atomic_write_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


@dataclass(slots=True)
class StoryrealmsStore:
    """
    Persistence adapter (event log + latest snapshot).

    - event log: JSONL for append-only durability and replay
    - snapshot: JSON for quick startup
    """

    base_dir: str = os.environ.get("STORYREALMS_DATA_DIR", "storyrealms/data")

    def _realm_dir(self, realm: str) -> str:
        safe = realm.replace("/", "_").replace("\\", "_").strip() or "default"
        return os.path.join(self.base_dir, safe)

    def event_log_path(self, realm: str) -> str:
        return os.path.join(self._realm_dir(realm), "events.jsonl")

    def snapshot_path(self, realm: str) -> str:
        return os.path.join(self._realm_dir(realm), "snapshot.json")

    def append_event(self, event: RealmEvent) -> None:
        path = self.event_log_path(event.realm)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")

    def iter_events(self, realm: str) -> Iterator[RealmEvent]:
        path = self.event_log_path(realm)
        if not os.path.exists(path):
            def _empty() -> Iterator[RealmEvent]:
                if False:
                    yield  # pragma: no cover
                return
            return _empty()
        def _iter() -> Iterator[RealmEvent]:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield RealmEvent.from_dict(json.loads(line))
                    except Exception:
                        continue
        return _iter()

    def read_events(self, realm: str, limit: Optional[int] = None) -> List[RealmEvent]:
        """
        Convenience: load events into memory (optionally last N).
        """
        events = list(self.iter_events(realm))
        if limit is None:
            return events
        try:
            n = int(limit)
        except Exception:
            return events
        if n <= 0:
            return []
        return events[-n:]

    def save_snapshot(self, state: RealmState) -> None:
        _atomic_write_json(self.snapshot_path(state.realm), state.to_dict())

    def load_snapshot(self, realm: str) -> Optional[RealmState]:
        path = self.snapshot_path(realm)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return RealmState.from_dict(json.load(f))
        except Exception:
            return None

