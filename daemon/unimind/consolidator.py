from __future__ import annotations

import queue
import re
import threading
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from daemon.unimind.knowledge_store import ConceptCard, KnowledgeStore, PrefabTemplate, SkillRecipe


def _slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_\\-]+", "_", (s or "").strip().lower())
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:64] if s else "unknown"


GEOM_OPS = {
    "extrude": {
        "id": "shape.extrude",
        "title": "Extrude",
        "definition": "Create a solid by extending a 2D profile along a direction for a given height.",
        "parameters": [{"name": "profile", "type": "closed_polyline"}, {"name": "height", "type": "float"}],
        "constraints": ["Profile should be closed", "Height should be > 0"],
        "tags": ["geometry", "shape.op", "shape.extrude"],
        "related": ["shape.sweep", "shape.boolean_union"],
    },
    "bevel": {
        "id": "shape.bevel",
        "title": "Bevel",
        "definition": "Replace sharp edges with a chamfer/round to improve aesthetics and reduce artifacts.",
        "parameters": [{"name": "radius", "type": "float"}, {"name": "segments", "type": "int"}],
        "constraints": ["Radius must be non-negative", "Avoid beveling edges smaller than radius"],
        "tags": ["geometry", "shape.op", "shape.bevel"],
        "related": ["shape.extrude"],
    },
    "boolean": {
        "id": "shape.boolean_ops",
        "title": "Boolean Operations",
        "definition": "Combine solids using union, difference, and intersection.",
        "parameters": [{"name": "a", "type": "solid"}, {"name": "b", "type": "solid"}, {"name": "op", "type": "union|difference|intersection"}],
        "constraints": ["Inputs should be watertight solids"],
        "tags": ["geometry", "shape.op", "shape.boolean"],
        "related": ["shape.extrude"],
    },
}


@dataclass
class ConsolidationConfig:
    max_examples_per_card: int = 10
    max_queue: int = 1000


class MemoryConsolidator:
    """
    Background worker that promotes episodic events into compact semantic/procedural artifacts.

    Input: daemon event dicts (or small learning artifacts)
    Output: upserts into KnowledgeStore
    """

    def __init__(
        self,
        store: KnowledgeStore,
        config: Optional[ConsolidationConfig] = None,
        *,
        on_upsert: Optional[callable] = None,
    ):
        self._store = store
        self._cfg = config or ConsolidationConfig()
        self._q: "queue.Queue[Dict[str, Any]]" = queue.Queue(maxsize=self._cfg.max_queue)
        self._t: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._on_upsert = on_upsert

    def start(self) -> None:
        if self._t and self._t.is_alive():
            return
        self._stop.clear()
        self._t = threading.Thread(target=self._run, daemon=True)
        self._t.start()

    def stop(self) -> None:
        self._stop.set()

    def enqueue(self, event: Dict[str, Any]) -> None:
        try:
            self._q.put(event, block=False)
        except queue.Full:
            # Drop if overloaded; consolidation is best-effort.
            return

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                event = self._q.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                self._process_event(event)
            except Exception:
                continue

    def _process_event(self, event: Dict[str, Any]) -> None:
        etype = str(event.get("type") or "")
        payload = event.get("payload") or {}

        text = ""
        if isinstance(payload, dict):
            if isinstance(payload.get("text"), str):
                text = payload["text"]
            elif isinstance(payload.get("scene"), str):
                text = f"scene={payload['scene']}"
        if not text:
            return

        lowered = text.lower()

        # Geometry concept cards
        for k, spec in GEOM_OPS.items():
            if k in lowered:
                example = text.strip()[:200]
                card = ConceptCard(
                    id=spec["id"],
                    title=spec["title"],
                    definition=spec["definition"],
                    parameters=list(spec.get("parameters") or []),
                    constraints=list(spec.get("constraints") or []),
                    related=list(spec.get("related") or []),
                    tags=list(spec.get("tags") or []),
                    examples=[example],
                )
                out = self._store.upsert_concept(card)
                if self._on_upsert:
                    try:
                        self._on_upsert(out.id, list(out.tags))
                    except Exception:
                        pass

        # Procedural: detect "how do i make/build" → create a recipe skeleton
        if any(p in lowered for p in ("how do i", "how to", "recipe", "steps to")):
            goal = text.strip()[:120]
            rid = f"recipe.{_slug(goal)[:48]}"
            recipe = SkillRecipe(
                id=rid,
                goal=goal,
                steps=[
                    "Identify primitives and constraints.",
                    "Select operations (extrude/sweep/boolean/bevel) in a stable order.",
                    "Run quality checks (watertight, normals, self-intersections).",
                ],
                quality_checks=["watertight mesh", "no self-intersections", "normals consistent"],
                failure_modes=["non-manifold edges after boolean", "profile not closed for extrude"],
                tags=["geometry", "procedural", "recipe"],
            )
            out = self._store.upsert_recipe(recipe)
            if self._on_upsert:
                try:
                    self._on_upsert(out.id, list(out.tags))
                except Exception:
                    pass

        # Prefab: detect "prefab:" or "template:" to store a blueprint
        if lowered.startswith("prefab:") or lowered.startswith("template:"):
            name = text.split(":", 1)[1].strip()[:80] if ":" in text else text[:80]
            pid = f"prefab.{_slug(name)}"
            prefab = PrefabTemplate(
                id=pid,
                name=name,
                description=f"User-defined prefab template: {name}",
                parameters={},
                tags=["geometry", "prefab"],
            )
            out = self._store.upsert_prefab(prefab)
            if self._on_upsert:
                try:
                    self._on_upsert(out.id, list(out.tags))
                except Exception:
                    pass

