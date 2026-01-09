from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .context import ConceptGraph, UnimindContext, UnimindPlan, UnimindSignals
from .decision_matrix import DecisionMatrix
from .brain import Brain
from .subsystems import EthicsSubsystem, SubsystemReport, UnimindSubsystem
from .knowledge_store import KnowledgeStore
from .mind_palace import MindPalace
from .consolidator import MemoryConsolidator


class Unimind:
    """
    Unimind: a modular daemon cognition orchestrator.

    The old implementation was a bare module registry with a `reflect()` loop.
    This version keeps backward compatibility (still supports `.register(type, module)`),
    but upgrades Unimind into an orchestrator that:
    - builds a shared `UnimindContext`
    - collects observations from subsystems
    - performs concept expansion (symbolic graph)
    - scores candidate plans with a decision matrix + ethical review
    - logs artifacts for later reflection
    """

    def __init__(self, log_dir: str = "logs", *, enable_learning: bool = True):
        self._by_type: Dict[str, List[Any]] = {
            "logic": [],
            "emotion": [],
            "memory": [],
            "ethics": [],
            "language": [],
        }
        self._subsystems: List[UnimindSubsystem] = []
        self._ethics: Optional[EthicsSubsystem] = None
        self._decision = DecisionMatrix()
        self._brain = Brain(decision=self._decision, ethics=self._ethics)
        self._log_dir = log_dir
        os.makedirs(self._log_dir, exist_ok=True)

        # Learning substrate (daemon-local, durable)
        self.knowledge = KnowledgeStore(root="daemon/unimind/knowledge")
        self.mind_palace = MindPalace()
        self._consolidator = MemoryConsolidator(
            self.knowledge,
            on_upsert=lambda aid, tags: self.mind_palace.place(aid, tags=tags),
        )
        self._learning_enabled = enable_learning
        if self._learning_enabled:
            self._consolidator.start()

        print("[Unimind] Core initialized.")

    # ---- Backward-compatible registry ----
    def register(self, type: str, module: Any):
        if type in self._by_type:
            self._by_type[type].append(module)
            print(f"[Unimind] Registered module under '{type}'")

    # ---- New agent-native registry ----
    def attach(self, subsystem: UnimindSubsystem):
        self._subsystems.append(subsystem)
        if getattr(subsystem, "name", None) == "ethics" and isinstance(subsystem, EthicsSubsystem):
            self._ethics = subsystem
            # Keep brain wired to ethics if/when ethics is attached later.
            self._brain = Brain(decision=self._decision, ethics=self._ethics)
        print(f"[Unimind] Attached subsystem: {getattr(subsystem, 'name', 'unknown')}")

    def build_context(self, input_text: Optional[str] = None, intent: Any = None) -> UnimindContext:
        """
        Construct a shared context snapshot from attached subsystems.
        """
        symbolic_state: Dict[str, Any] = {}
        signals = UnimindSignals()

        reports: List[SubsystemReport] = []
        for s in list(self._subsystems):
            try:
                obs = s.observe(
                    UnimindContext(input_text=input_text, intent=intent)  # minimal bootstrap ctx
                )
            except Exception as e:
                obs = {"error": str(e)}

            thought = None
            try:
                # Provide a richer ctx for think() once we have observations.
                pass
            except Exception:
                thought = None

            reports.append(SubsystemReport(name=getattr(s, "name", "unknown"), observation=obs, thought=thought))

            if getattr(s, "name", None) == "logic":
                symbolic_state = obs.get("symbolic_state", {}) or {}
            elif getattr(s, "name", None) == "emotion":
                signals = UnimindSignals(
                    emotion=obs,
                    memory=signals.memory,
                    ethics=signals.ethics,
                    language=signals.language,
                    logic=signals.logic,
                )
            elif getattr(s, "name", None) == "memory":
                signals = UnimindSignals(
                    emotion=signals.emotion,
                    memory=obs,
                    ethics=signals.ethics,
                    language=signals.language,
                    logic=signals.logic,
                )
            elif getattr(s, "name", None) == "ethics":
                signals = UnimindSignals(
                    emotion=signals.emotion,
                    memory=signals.memory,
                    ethics=obs,
                    language=signals.language,
                    logic=signals.logic,
                )

        ctx = UnimindContext(
            input_text=input_text,
            intent=intent,
            symbolic_state=symbolic_state,
            signals=signals,
            notes={"subsystem_reports": [asdict(r) for r in reports]},
        )
        return ctx

    def _log_jsonl(self, filename: str, payload: Dict[str, Any]) -> None:
        path = os.path.join(self._log_dir, filename)
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception:
            # Logging should never take down the daemon.
            pass

    # ---- Core loop ----
    def cycle(self, input_text: str, intent: Any = None) -> UnimindPlan:
        """
        Run one perception->expansion->decision pass.
        """
        plan, _trace = self.cycle_with_trace(input_text=input_text, intent=intent, event=None)
        return plan

    def cycle_with_trace(self, input_text: str, intent: Any = None, event: Optional[Dict[str, Any]] = None):
        """
        Same as `cycle()` but returns (plan, brain_trace) for routing/UX layers.
        """
        ctx = self.build_context(input_text=input_text, intent=intent)
        if event:
            ctx = ctx.with_note("event", event)

        # Let subsystems update internal state based on the now-stable context.
        lam_thoughts: Dict[str, Any] = {}
        for s in list(self._subsystems):
            try:
                thought = s.think(ctx)
                if thought:
                    lam_thoughts.update(thought)
            except Exception:
                continue
        if lam_thoughts:
            ctx = ctx.with_note("subsystem_thoughts", lam_thoughts)

        graph = self.expand_concepts(ctx)
        ctx = ctx.with_note("concept_graph", asdict(graph))

        # Recall from knowledge store (small top-k only) to avoid scanning logs.
        recall = self.knowledge.search(input_text, tags=["geometry"] if "shape" in (input_text or "").lower() else [], top_k=5)
        if recall:
            ctx = ctx.with_note("knowledge_recall", recall)

        plan, brain_trace = self._brain.think(ctx)
        ctx = ctx.with_note("brain_trace", asdict(brain_trace))
        self._log_jsonl(
            "unimind_cycles.jsonl",
            {
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "input_text": input_text,
                "intent": intent,
                "plan": asdict(plan),
                "concept_graph": asdict(graph),
                "brain_trace": asdict(brain_trace),
                "signals": asdict(ctx.signals),
            },
        )
        return plan, brain_trace

    def ingest_event(self, event: Dict[str, Any], *, nlu_intent: Any = None):
        """
        Ingest a daemon event, transform it into a reasoning seed, and return (plan, trace).
        """
        etype = str(event.get("type") or "system_event")
        payload = event.get("payload") or {}
        source = event.get("source") or "unknown"

        seed = ""
        if isinstance(payload, dict):
            if isinstance(payload.get("text"), str):
                seed = payload["text"]
            elif isinstance(payload.get("scene"), str):
                seed = f"[vision] scene={payload['scene']} source={source}"
            else:
                seed = f"[event] type={etype} source={source} payload={payload}"
        else:
            seed = f"[event] type={etype} source={source} payload={payload}"

        intent = nlu_intent if nlu_intent is not None else etype
        # Enqueue for consolidation (best-effort, async)
        if self._learning_enabled:
            self._consolidator.enqueue(event)

        # Run cognition immediately
        plan, trace = self.cycle_with_trace(seed, intent=intent, event=event)

        # Place learned/known artifacts into the mind palace (coarse routing by tags)
        try:
            # If we recalled artifacts, ensure they are placed for future fast routing.
            recalled = (trace.notes or {}).get("knowledge_recall") if trace else None
            if isinstance(recalled, list):
                for a in recalled[:10]:
                    aid = a.get("id")
                    tags = a.get("tags") or []
                    if aid:
                        self.mind_palace.place(str(aid), tags=tags)
        except Exception:
            pass

        return plan, trace

    def reflect(self):
        """
        Reflection loop for nightly runs or idle moments.
        """
        print("[Unimind] Running reflection loop...")
        ctx = self.build_context(input_text=None, intent="reflection")
        graph = self.expand_concepts(ctx)
        self._log_jsonl(
            "unimind_reflections.jsonl",
            {
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "concept_graph": asdict(graph),
                "signals": asdict(ctx.signals),
            },
        )

    # ---- Expansion + decision (implemented in dedicated modules, but kept here for cohesion) ----
    def expand_concepts(self, ctx: UnimindContext) -> ConceptGraph:
        # Local import to avoid cycles; keep dependencies shallow.
        from .expansion import ConceptExpander
        from .knowledge import CodexIndex

        codex = CodexIndex(root="codex/data")
        expander = ConceptExpander(codex_index=codex)
        seed = ctx.input_text or "reflection"

        recent_events = (ctx.signals.memory or {}).get("recent_events", []) or []
        graph = expander.expand(seed=seed, recent_memory_events=recent_events)
        self._log_jsonl(
            "unimind_concepts.jsonl",
            {
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "seed": seed,
                "nodes": graph.nodes,
                "edges": graph.edges,
            },
        )
        return graph

    def decide_next(self, ctx: UnimindContext) -> UnimindPlan:
        """
        Legacy decision path. Kept for compatibility; new behavior uses `Brain`.
        """
        # Candidates are symbolic actions; execution can be handled elsewhere.
        lam_plan = (ctx.notes.get("subsystem_thoughts", {}) or {}).get("lam_plan")
        candidates: Dict[str, Dict[str, float]] = {
            "idle_reflect": {"logic": 0.2, "emotion": 0.2, "memory": 0.2, "intuition": 0.4},
            "log_and_wait": {"logic": 0.1, "emotion": 0.1, "memory": 0.6, "intuition": 0.2},
        }
        if lam_plan:
            candidates["lam_next_action"] = {"logic": 0.6, "emotion": 0.1, "memory": 0.2, "intuition": 0.1}

        best, scored = self._decision.choose_with_rationale(candidates)
        action = lam_plan if best == "lam_next_action" and lam_plan else best

        ethics_note = self._ethics.evaluate(action) if self._ethics else None
        rationale = scored.get(best, {}).get("rationale", "")
        if ethics_note:
            rationale = f"{rationale} | Ethics: {ethics_note}"

        return UnimindPlan(
            action=action,
            rationale=rationale or "Selected highest-scoring candidate.",
            score=scored.get(best, {}).get("score"),
            details={"scoring": scored, "selected_key": best},
        )
