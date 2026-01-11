from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


def _today_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _safe_date(date_str: str) -> str:
    d = (date_str or "").strip()
    if len(d) == 10 and d[4] == "-" and d[7] == "-":
        return d
    return _today_utc()


def _load_json(path: str) -> Any:
    with open(path, "r") as f:
        return json.load(f)


def _load_jsonl(path: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                out.append({"raw": line})
            if limit and len(out) >= limit:
                break
    return out


def _iso_date(ts: str) -> Optional[str]:
    if not ts:
        return None
    # Accept: 2026-01-11T02:32:31.399515 or 2026-01-11T02:32:31Z
    return ts[:10] if len(ts) >= 10 else None


def _iso_hour(ts: str) -> str:
    if not ts or len(ts) < 13:
        return "??"
    return ts[11:13]


@dataclass
class DayDigest:
    day: str
    counts: Dict[str, int]
    timeline: Dict[str, List[Dict[str, Any]]]
    highlights: List[str]
    output_path: str


def _summarize_entry(entry: Dict[str, Any]) -> str:
    t = str(entry.get("type", "")).strip()
    content = entry.get("content")
    if isinstance(content, dict):
        # common interaction log shape
        if "input" in content and "output" in content:
            return f"{t or 'interaction'}: {content.get('input')} -> {str(content.get('output'))[:120]}"
        return f"{t or 'event'}: {json.dumps(content, default=str)[:160]}"
    return f"{t or 'event'}: {str(content)[:160]}"


def sort_day(
    day: Optional[str] = None,
    memory_log_path: str = "memory_tree/logs/memory_log.json",
    inbox_dir: str = "memory_tree/inbox",
    clips_dir: str = "memory_tree/clips",
    out_dir: str = "memory_tree/daily",
) -> DayDigest:
    """
    Build an end-of-day digest from:
    - Memory logger JSON (`memory_tree/logs/memory_log.json`)
    - Telemetry inbox JSONL (`memory_tree/inbox/YYYY-MM-DD.jsonl`)
    - Clip metadata JSONL (`memory_tree/clips/YYYY-MM-DD.jsonl`)
    """
    d = _safe_date(day or "")
    os.makedirs(out_dir, exist_ok=True)

    entries: List[Dict[str, Any]] = []

    # Memory log (structured)
    if os.path.exists(memory_log_path):
        try:
            data = _load_json(memory_log_path) or []
            for e in data:
                ts = str(e.get("timestamp", "") or "")
                if _iso_date(ts) == d:
                    entries.append({"source": "memory_log", **e})
        except Exception:
            pass

    # Telemetry inbox (events)
    inbox_path = os.path.join(inbox_dir, f"{d}.jsonl")
    if os.path.exists(inbox_path):
        for e in _load_jsonl(inbox_path):
            ts = str(e.get("ts", "") or "")
            entries.append(
                {
                    "timestamp": ts or f"{d}T00:00:00Z",
                    "type": e.get("type", "telemetry"),
                    "content": e,
                    "source": "telemetry",
                }
            )

    # Clips metadata
    clips_path = os.path.join(clips_dir, f"{d}.jsonl")
    if os.path.exists(clips_path):
        for e in _load_jsonl(clips_path):
            entries.append(
                {"timestamp": str(e.get("ts", f"{d}T00:00:00Z")), "type": "clip", "content": e, "source": "clips"}
            )

    # Organize
    timeline: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    counts: Dict[str, int] = defaultdict(int)
    highlights: List[str] = []

    for e in entries:
        ts = str(e.get("timestamp", "") or "")
        hour = _iso_hour(ts)
        typ = str(e.get("type", "event"))
        counts[typ] += 1
        timeline[hour].append(e)

    # simple highlights
    for e in entries:
        typ = str(e.get("type", ""))
        if typ in {"interaction"}:
            content = e.get("content") or {}
            if isinstance(content, dict) and "input" in content:
                inp = str(content.get("input"))
                if inp.startswith("xr ") or "train" in inp:
                    highlights.append(_summarize_entry(e))
        if typ in {"ar_xr.training_started", "ar_xr.sim_distilled"}:
            highlights.append(_summarize_entry(e))
        if typ == "clip":
            c = e.get("content") or {}
            if isinstance(c, dict):
                highlights.append(f"clip: {c.get('device_id','?')} {c.get('clip_name','(unnamed)')}")

    # write digest markdown
    out_path = os.path.join(out_dir, f"{d}.md")
    lines: List[str] = []
    lines.append(f"# Day Digest: {d}")
    lines.append("")
    lines.append("## Counts")
    for k in sorted(counts.keys()):
        lines.append(f"- **{k}**: {counts[k]}")
    lines.append("")
    lines.append("## Highlights")
    if highlights:
        for h in highlights[:50]:
            lines.append(f"- {h}")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Timeline")
    for hour in sorted(timeline.keys()):
        lines.append(f"### {hour}:00")
        for e in timeline[hour][:100]:
            lines.append(f"- {_summarize_entry(e)}")
        lines.append("")

    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    return DayDigest(day=d, counts=dict(counts), timeline=dict(timeline), highlights=highlights, output_path=out_path)

