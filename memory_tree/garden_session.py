from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from memory_tree.garden import GardenMap, build_garden_map


SESSION_PATH = "memory_tree/garden/session.json"


@dataclass
class GardenSessionState:
    day: str
    current_plot: Optional[str] = None
    # index offset for paging within current plot
    cursor: int = 0
    tags: Dict[str, List[str]] = field(default_factory=dict)  # key = seed_id, value = tags


def _seed_id(plot: str, idx: int) -> str:
    return f"{plot}::{idx}"


def load_session(default_day: Optional[str] = None) -> GardenSessionState:
    if os.path.exists(SESSION_PATH):
        try:
            with open(SESSION_PATH, "r") as f:
                data = json.load(f)
            return GardenSessionState(
                day=str(data.get("day")),
                current_plot=data.get("current_plot"),
                cursor=int(data.get("cursor", 0)),
                tags=dict(data.get("tags", {})),
            )
        except Exception:
            pass
    # create a new session
    day = str(default_day or "")
    if not day:
        # build_garden_map will normalize day
        gm = build_garden_map(day=None)
        day = gm.day
    return GardenSessionState(day=day)


def save_session(state: GardenSessionState) -> None:
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
    with open(SESSION_PATH, "w") as f:
        json.dump(
            {
                "day": state.day,
                "current_plot": state.current_plot,
                "cursor": state.cursor,
                "tags": state.tags,
            },
            f,
            indent=2,
        )


def open_day(day: Optional[str] = None) -> Tuple[GardenMap, GardenSessionState]:
    gm = build_garden_map(day=day)
    state = load_session(default_day=gm.day)
    state.day = gm.day
    state.cursor = 0
    # keep plot if still exists
    if state.current_plot and state.current_plot not in gm.plots:
        state.current_plot = None
    save_session(state)
    return gm, state


def list_plots(gm: GardenMap) -> List[str]:
    return sorted(gm.plots.keys())


def walk_to_plot(gm: GardenMap, state: GardenSessionState, plot_name: str) -> GardenSessionState:
    if plot_name not in gm.plots:
        raise ValueError(f"Unknown plot: {plot_name}")
    state.current_plot = plot_name
    state.cursor = 0
    save_session(state)
    return state


def show_current(state: GardenSessionState) -> Dict[str, Any]:
    return {"day": state.day, "current_plot": state.current_plot, "cursor": state.cursor}


def list_seeds(
    gm: GardenMap,
    state: GardenSessionState,
    plot_name: Optional[str] = None,
    limit: int = 10,
    offset: Optional[int] = None,
) -> Dict[str, Any]:
    plot = plot_name or state.current_plot
    if not plot:
        raise ValueError("No plot selected. Use 'garden walk <plot>'.")
    if plot not in gm.plots:
        raise ValueError(f"Unknown plot: {plot}")

    seeds = gm.plots[plot].seeds
    start = int(offset) if offset is not None else int(state.cursor)
    start = max(0, start)
    lim = max(1, int(limit))
    chunk = seeds[start : start + lim]

    # advance cursor when listing the current plot
    if plot == state.current_plot and offset is None:
        state.cursor = start + len(chunk)
        save_session(state)

    items = []
    for i, s in enumerate(chunk, start=start):
        sid = _seed_id(plot, i)
        items.append(
            {
                "index": i,
                "seed_id": sid,
                "summary": s.summary,
                "tags": state.tags.get(sid, []),
            }
        )
    return {"plot": plot, "offset": start, "count": len(items), "items": items, "next_cursor": state.cursor}


def inspect_seed(gm: GardenMap, state: GardenSessionState, plot: str, index: int) -> Dict[str, Any]:
    if plot not in gm.plots:
        raise ValueError(f"Unknown plot: {plot}")
    seeds = gm.plots[plot].seeds
    if index < 0 or index >= len(seeds):
        raise IndexError("Seed index out of range")
    sid = _seed_id(plot, index)
    s = seeds[index]
    return {"seed_id": sid, "plot": plot, "index": index, "summary": s.summary, "entry": s.entry, "tags": state.tags.get(sid, [])}


def tag_seed(state: GardenSessionState, plot: str, index: int, tag: str) -> GardenSessionState:
    t = (tag or "").strip()
    if not t:
        raise ValueError("Tag is empty")
    sid = _seed_id(plot, index)
    tags = state.tags.get(sid, [])
    if t not in tags:
        tags.append(t)
    state.tags[sid] = tags
    save_session(state)
    return state

