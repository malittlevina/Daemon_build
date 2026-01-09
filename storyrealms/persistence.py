from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterator, List, Optional

from storyrealms.events import RealmEvent
from storyrealms.state import RealmState


def _atomic_write_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


class _FileLock:
    """
    Best-effort advisory file lock (Linux: fcntl.flock).
    Falls back to no-op if unavailable.
    """

    def __init__(self, lock_path: str):
        self.lock_path = lock_path
        self._fh = None

    def __enter__(self):
        try:
            import fcntl  # linux/unix only

            os.makedirs(os.path.dirname(self.lock_path), exist_ok=True)
            self._fh = open(self.lock_path, "a+", encoding="utf-8")
            fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX)
        except Exception:
            self._fh = None
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if self._fh is not None:
                import fcntl

                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
                self._fh.close()
        except Exception:
            pass
        self._fh = None


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

    def lock_path(self, realm: str) -> str:
        return os.path.join(self._realm_dir(realm), ".lock")

    def event_log_path(self, realm: str) -> str:
        return os.path.join(self._realm_dir(realm), "events.jsonl")

    def snapshot_path(self, realm: str) -> str:
        return os.path.join(self._realm_dir(realm), "snapshot.json")

    def archive_dir(self, realm: str) -> str:
        return os.path.join(self._realm_dir(realm), "archive")

    def append_event(self, event: RealmEvent) -> None:
        path = self.event_log_path(event.realm)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with _FileLock(self.lock_path(event.realm)):
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

    def iter_all_events(self, realm: str) -> Iterator[RealmEvent]:
        """
        Iterate current events + archived event logs (oldest to newest).
        """
        arch = self.archive_dir(realm)
        if os.path.isdir(arch):
            files = [f for f in os.listdir(arch) if f.startswith("events_") and f.endswith(".jsonl")]
            for fn in sorted(files):
                path = os.path.join(arch, fn)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                yield RealmEvent.from_dict(json.loads(line))
                            except Exception:
                                continue
                except Exception:
                    continue
        yield from self.iter_events(realm)

    def save_snapshot(self, state: RealmState, *, archive_events: bool = False, truncate_events: bool = False) -> None:
        """
        Persist snapshot. Optionally archive/truncate the current event log for performance.

        - archive_events: move current events.jsonl to archive/events_<utc>.jsonl (best-effort)
        - truncate_events: clear current events.jsonl after snapshot (best-effort)
        """
        realm = state.realm
        with _FileLock(self.lock_path(realm)):
            _atomic_write_json(self.snapshot_path(realm), state.to_dict())

            if not (archive_events or truncate_events):
                return

            log_path = self.event_log_path(realm)
            if not os.path.exists(log_path):
                return

            if archive_events:
                ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                os.makedirs(self.archive_dir(realm), exist_ok=True)
                archived = os.path.join(self.archive_dir(realm), f"events_{ts}.jsonl")
                try:
                    os.replace(log_path, archived)
                except Exception:
                    # If we can't move it, we can still attempt truncation.
                    pass

            if truncate_events:
                try:
                    with open(log_path, "w", encoding="utf-8") as f:
                        f.write("")
                except Exception:
                    return

    def load_snapshot(self, realm: str) -> Optional[RealmState]:
        path = self.snapshot_path(realm)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return RealmState.from_dict(json.load(f))
        except Exception:
            return None

