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
        # In-memory counters for "repeated question" detection (best-effort).
        self._topic_counts: Dict[str, int] = {}

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

        # Track repeated question topics and upgrade recipes when threshold reached.
        self._track_and_upgrade(lowered)

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
            tags, steps, qc, fm = self._infer_k12_recipe_skeleton(lowered, goal)
            recipe = SkillRecipe(
                id=rid,
                goal=goal,
                steps=steps,
                quality_checks=qc,
                failure_modes=fm,
                tags=tags,
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

    def _infer_k12_recipe_skeleton(self, lowered_text: str, goal: str):
        """
        Best-effort domain tagging + step skeleton so recipes sort into the mind palace.
        Returns: (tags, steps, quality_checks, failure_modes)
        """
        t = lowered_text or ""

        # Math
        if any(w in t for w in ("equation", "solve for x", "linear")):
            return (
                ["k12", "math", "algebra", "recipe"],
                [
                    "Simplify both sides (combine like terms).",
                    "Move variable terms to one side and constants to the other.",
                    "Divide by the coefficient of the variable.",
                    "Check by substitution.",
                ],
                ["solution satisfies original equation"],
                ["sign errors", "not applying operations to both sides"],
            )
        if any(w in t for w in ("fraction", "common denominator")):
            return (
                ["k12", "math", "arithmetic", "recipe"],
                [
                    "Find a common denominator.",
                    "Rewrite fractions with that denominator.",
                    "Add/subtract numerators and simplify.",
                    "Check reasonableness (size and sign).",
                ],
                ["fraction simplified"],
                ["adding denominators directly", "not simplifying"],
            )
        if any(w in t for w in ("pythagorean", "right triangle", "hypotenuse")):
            return (
                ["k12", "math", "geometry", "recipe"],
                [
                    "Identify the hypotenuse (opposite the right angle).",
                    "Use a² + b² = c² with correct assignment.",
                    "Solve for the unknown (square root if needed).",
                    "Sanity check the result.",
                ],
                ["hypotenuse identified correctly"],
                ["mixing up sides", "forgetting square root"],
            )

        # Science
        if any(w in t for w in ("scientific method", "hypothesis", "experiment", "variables")):
            return (
                ["k12", "science", "earth_science", "recipe"],
                [
                    "Ask a testable question and propose a hypothesis.",
                    "Identify independent/dependent variables and controls.",
                    "Run the experiment and record data.",
                    "Analyze results and conclude (then iterate).",
                ],
                ["variables identified", "data recorded"],
                ["changing multiple variables", "biased observations"],
            )

        # English
        if any(w in t for w in ("paragraph", "topic sentence", "thesis")):
            return (
                ["k12", "english", "writing", "recipe"],
                [
                    "Write a topic sentence stating the main point.",
                    "Add supporting sentences (evidence/examples).",
                    "Use transitions for flow.",
                    "Conclude and revise for clarity.",
                ],
                ["single main idea", "support matches topic sentence"],
                ["multiple topics", "no evidence"],
            )
        if any(w in t for w in ("subject verb", "subject-verb", "agreement", "grammar")):
            return (
                ["k12", "english", "grammar", "recipe"],
                [
                    "Find the main verb and the true subject.",
                    "Ignore prepositional phrases between subject and verb.",
                    "Match singular/plural forms.",
                    "Re-read for meaning.",
                ],
                ["main subject identified"],
                ["agreeing with a nearby noun"],
            )

        # History/Civics
        if any(w in t for w in ("timeline", "historical period", "summarize history")):
            return (
                ["k12", "history", "modern", "recipe"],
                [
                    "Identify the time span and key events.",
                    "Order events chronologically.",
                    "Add brief cause/effect notes for major events.",
                    "Summarize what changed over time.",
                ],
                ["chronological order maintained"],
                ["listing facts without impact"],
            )
        if any(w in t for w in ("branches of government", "checks and balances", "legislative", "executive", "judicial")):
            return (
                ["k12", "history", "civics", "recipe"],
                [
                    "Name the three branches and their roles.",
                    "Give examples of checks and balances.",
                    "Explain why checks and balances matter.",
                ],
                ["roles correct", "at least one check/balance example"],
                ["mixing branch roles"],
            )

        # Default: keep generic but not geometry-only
        return (
            ["k12", "recipe"],
            ["Break the goal into steps.", "Work one example.", "Check the result."],
            ["result checked"],
            ["unclear goal; restate it"],
        )

    def _track_and_upgrade(self, lowered_text: str) -> None:
        """
        Detect repeated question themes and promote/upgrade procedural recipes.

        This stays intentionally lightweight: keyword routing + counters.
        """
        if not lowered_text:
            return

        # Heuristic: treat questions as stronger signals.
        is_question = "?" in lowered_text or lowered_text.startswith(("how", "what", "why", "when", "where"))

        topics: List[str] = []
        # Math
        if any(w in lowered_text for w in ("linear equation", "solve for x", "ax +", "equation")):
            topics.append("k12.recipe.solve_linear_equations")
        if any(w in lowered_text for w in ("add fractions", "subtract fractions", "common denominator", "fractions")):
            topics.append("k12.recipe.add_fractions")
        if any(w in lowered_text for w in ("pythagorean", "right triangle", "hypotenuse")):
            topics.append("k12.recipe.use_pythagorean_theorem")

        # Science
        if any(w in lowered_text for w in ("scientific method", "hypothesis", "experiment", "variables")):
            topics.append("k12.recipe.scientific_method")

        # English
        if any(w in lowered_text for w in ("topic sentence", "paragraph", "write a paragraph")):
            topics.append("k12.recipe.write_paragraph")
        if any(w in lowered_text for w in ("subject verb agreement", "subject-verb", "grammar")):
            topics.append("k12.recipe.subject_verb_agreement_check")

        # History/Civics
        if any(w in lowered_text for w in ("timeline", "summarize history", "historical period")):
            topics.append("k12.recipe.read_history_timeline")
        if any(w in lowered_text for w in ("branches of government", "checks and balances", "legislative", "executive", "judicial")):
            topics.append("k12.recipe.explain_branches_government")

        if not topics:
            return

        # Update counters and upgrade at threshold
        threshold = 3 if is_question else 5
        for tid in topics:
            self._topic_counts[tid] = int(self._topic_counts.get(tid, 0)) + 1
            if self._topic_counts[tid] == threshold:
                self._upgrade_recipe(tid)

    def _upgrade_recipe(self, recipe_id: str) -> None:
        """
        Upgrade an existing recipe with a small set of clarifying steps/checks.
        """
        base = self._store.get(recipe_id)
        # If not present, do nothing (seed pack should cover most).
        if not base or base.get("kind") != "recipe":
            return

        goal = str(base.get("goal") or "")
        steps = list(base.get("steps") or [])
        qc = list(base.get("quality_checks") or [])
        fm = list(base.get("failure_modes") or [])
        tags = list(base.get("tags") or [])

        # Generic upgrades: add an "example" and "explain why" prompt.
        if "Work through a concrete example step-by-step." not in steps:
            steps.append("Work through a concrete example step-by-step.")
        if "Explain the reasoning for each step in one sentence." not in steps:
            steps.append("Explain the reasoning for each step in one sentence.")
        if "final answer checked" not in " ".join(qc).lower():
            qc.append("final answer checked")
        if "confusing terms" not in " ".join(fm).lower():
            fm.append("confusing terms or definitions; re-derive from basics")

        upgraded = SkillRecipe(
            id=recipe_id,
            goal=goal,
            steps=steps[:30],
            quality_checks=qc[:20],
            failure_modes=fm[:20],
            tags=tags,
        )
        out = self._store.upsert_recipe(upgraded)
        if self._on_upsert:
            try:
                self._on_upsert(out.id, list(out.tags))
            except Exception:
                pass

