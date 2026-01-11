from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


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


def _iso_hour(ts: str) -> str:
    if not ts or len(ts) < 13:
        return "??"
    return ts[11:13]


def _text_blob(entry: Dict[str, Any]) -> str:
    pieces: List[str] = []
    for k in ("type", "source", "timestamp"):
        if k in entry:
            pieces.append(str(entry.get(k)))
    content = entry.get("content")
    if isinstance(content, dict):
        pieces.append(json.dumps(content, default=str))
    else:
        pieces.append(str(content))
    return " ".join(pieces).lower()


def _classify_plot(entry: Dict[str, Any]) -> str:
    """
    Heuristic plot classifier. This is intentionally simple but stable/offline.
    """
    blob = _text_blob(entry)
    if "xr" in blob or "openxr" in blob or "webxr" in blob or "ar_xr" in blob:
        return "XR Grove"
    if "clip" in blob or entry.get("type") == "clip":
        return "Memory Pond (Clips)"
    if "task" in blob or "planner" in blob or "run task" in blob:
        return "Workshop (Tasks)"
    if "meeting" in blob or "met " in blob or "call" in blob:
        return "People Arbor"
    if "health" in blob or "workout" in blob or "walk" in blob or "sleep" in blob:
        return "Health Meadow"
    if "idea" in blob or "insight" in blob or "learn" in blob or "study" in blob:
        return "Idea Greenhouse"
    return "Daily Path"


def _summarize_seed(entry: Dict[str, Any]) -> str:
    ts = str(entry.get("timestamp", "") or "")
    hour = _iso_hour(ts)
    typ = str(entry.get("type", "event"))
    content = entry.get("content")
    if isinstance(content, dict) and "input" in content:
        inp = str(content.get("input"))
        out = str(content.get("output"))[:120]
        return f"{hour}:00 {typ}: {inp} → {out}"
    if isinstance(content, dict) and "text" in content:
        return f"{hour}:00 {typ}: {str(content.get('text'))[:160]}"
    return f"{hour}:00 {typ}: {str(content)[:160]}"


@dataclass
class Seed:
    summary: str
    entry: Dict[str, Any]


@dataclass
class Plot:
    name: str
    seeds: List[Seed] = field(default_factory=list)


@dataclass
class GardenMap:
    day: str
    plots: Dict[str, Plot]
    output_md: str
    output_json: str


def build_garden_map(
    day: Optional[str] = None,
    memory_log_path: str = "memory_tree/logs/memory_log.json",
    inbox_dir: str = "memory_tree/inbox",
    clips_dir: str = "memory_tree/clips",
    out_dir: str = "memory_tree/garden",
) -> GardenMap:
    d = _safe_date(day or "")
    os.makedirs(out_dir, exist_ok=True)

    entries: List[Dict[str, Any]] = []

    # memory log (structured)
    if os.path.exists(memory_log_path):
        try:
            data = _load_json(memory_log_path) or []
            for e in data:
                ts = str(e.get("timestamp", "") or "")
                if ts[:10] == d:
                    entries.append({"source": "memory_log", **e})
        except Exception:
            pass

    # telemetry events
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

    # clips
    clips_path = os.path.join(clips_dir, f"{d}.jsonl")
    if os.path.exists(clips_path):
        for e in _load_jsonl(clips_path):
            entries.append({"timestamp": str(e.get("ts", f"{d}T00:00:00Z")), "type": "clip", "content": e, "source": "clips"})

    plots: Dict[str, Plot] = {}
    for e in entries:
        plot_name = _classify_plot(e)
        if plot_name not in plots:
            plots[plot_name] = Plot(name=plot_name)
        plots[plot_name].seeds.append(Seed(summary=_summarize_seed(e), entry=e))

    # outputs
    out_md = os.path.join(out_dir, f"{d}.md")
    out_json = os.path.join(out_dir, f"{d}.json")

    md: List[str] = []
    md.append(f"# Memory Garden: {d}")
    md.append("")
    md.append("A 'mind palace' view of your day: memories are grouped into garden plots (themes), each containing seeds (events).")
    md.append("")
    md.append("## Plots")
    for plot_name in sorted(plots.keys()):
        md.append(f"### {plot_name}")
        for seed in plots[plot_name].seeds[:200]:
            md.append(f"- {seed.summary}")
        md.append("")

    with open(out_md, "w") as f:
        f.write("\n".join(md) + "\n")

    serial = {
        "day": d,
        "plots": {
            name: {
                "name": p.name,
                "seeds": [{"summary": s.summary, "entry": s.entry} for s in p.seeds],
            }
            for name, p in plots.items()
        },
    }
    with open(out_json, "w") as f:
        json.dump(serial, f, indent=2, default=str)

    return GardenMap(day=d, plots=plots, output_md=out_md, output_json=out_json)

