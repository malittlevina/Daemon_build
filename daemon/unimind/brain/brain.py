from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional

from ..context import UnimindContext, UnimindPlan
from ..decision_matrix import DecisionMatrix
from ..subsystems import EthicsSubsystem
from .acc import AnteriorCingulateCortex
from .amygdala import Amygdala
from .corpus_callosum import CorpusCallosum
from .cerebellum import Cerebellum
from .dmn import DefaultModeNetwork
from .hippocampus import Hippocampus
from .hemispheres import LeftHemisphere, RightHemisphere
from .insula import Insula
from .basal_ganglia import BasalGanglia
from .language_areas import BrocaArea, WernickeArea
from .prefrontal import PrefrontalCortex
from .scheduler import ExecutiveScheduler
from .thalamus import Thalamus
from .types import BrainTrace


class Brain:
    """
    Brain pipeline for Unimind:
    - Thalamus: attention packet
    - Hemispheres: propose actions
    - Corpus Callosum: integrate/resolve
    - Prefrontal Cortex: select plan w/ rationale (and ethics if available)
    """

    def __init__(self, decision: Optional[DecisionMatrix] = None, ethics: Optional[EthicsSubsystem] = None):
        self._decision = decision or DecisionMatrix()
        self._thalamus = Thalamus()
        self._wernicke = WernickeArea()
        self._insula = Insula()
        self._amygdala = Amygdala()
        self._hippocampus = Hippocampus()
        self._left = LeftHemisphere()
        self._right = RightHemisphere()
        self._cc = CorpusCallosum()
        self._acc = AnteriorCingulateCortex()
        self._basal_ganglia = BasalGanglia()
        self._scheduler = ExecutiveScheduler()
        self._pfc = PrefrontalCortex(self._decision, ethics=ethics)
        self._broca = BrocaArea()
        self._cerebellum = Cerebellum()
        self._dmn = DefaultModeNetwork()

        # Persistent cross-cycle memory for habits/refinement.
        self._brain_memory: Dict[str, Any] = {}

    def think(self, ctx: UnimindContext) -> tuple[UnimindPlan, BrainTrace]:
        # Per-cycle working state + persistent memory
        state: Dict[str, Any] = {"_brain_memory": self._brain_memory}
        trace = BrainTrace()

        state.update(self._thalamus.process(ctx, state))
        state.update(self._wernicke.process(ctx, state))
        state.update(self._insula.process(ctx, state))
        state.update(self._amygdala.process(ctx, state))
        state.update(self._hippocampus.process(ctx, state))

        trace = BrainTrace(
            attention=state.get("attention") or {},
            proposals=[],
            selected=None,
            notes={
                "language_frame": state.get("language_frame"),
                "interoception": state.get("interoception"),
                "salience": state.get("salience"),
                "recalled_episodes": state.get("recalled_episodes"),
            },
        )

        state.update(self._left.process(ctx, state))
        state.update(self._right.process(ctx, state))

        state.update(self._cc.process(ctx, state))
        state.update(self._acc.process(ctx, state))
        state.update(self._basal_ganglia.process(ctx, state))
        state.update(self._scheduler.process(ctx, state))

        # Apply scheduler budget to proposals
        proposals = state.get("proposals") or []
        budget = (state.get("scheduler") or {}).get("budget") or {}
        max_proposals = int(budget.get("max_proposals", 6))
        proposals = list(proposals)[:max_proposals]
        state["proposals"] = proposals

        trace = BrainTrace(
            attention=trace.attention,
            proposals=[asdict(p) for p in proposals],
            selected=None,
            notes={
                **(trace.notes or {}),
                "conflicts": state.get("conflicts") or [],
                "conflict_monitor": state.get("conflict_monitor"),
                "habit": state.get("habit"),
                "scheduler": state.get("scheduler"),
            },
        )

        # Prefrontal selection (optionally biasing scores via Basal Ganglia policy bias)
        policy_bias = state.get("policy_bias") or {}
        if policy_bias:
            biased = []
            for p in proposals:
                new_scores = dict(p.scores)
                for k, v in policy_bias.items():
                    if k in new_scores:
                        new_scores[k] = float(new_scores[k]) + float(v)
                biased.append(
                    type(p)(
                        key=p.key,
                        action=p.action,
                        scores=new_scores,
                        rationale=p.rationale,
                        tags=list(p.tags),
                        metadata=dict(p.metadata),
                    )
                )
            proposals = biased
            state["proposals"] = proposals

        state.update(self._pfc.process(ctx, state))
        state.update(self._broca.process(ctx, state))
        state.update(self._cerebellum.process(ctx, state))
        state.update(self._dmn.process(ctx, state))
        plan: UnimindPlan = state["plan"]
        trace = BrainTrace(
            attention=trace.attention,
            proposals=trace.proposals,
            selected=state.get("selected"),
            notes={
                **(trace.notes or {}),
                "scored": state.get("scored") or {},
                "utterance_plan": state.get("utterance_plan"),
                "refinement": state.get("refinement"),
                "dmn": state.get("dmn"),
            },
        )
        return plan, trace

