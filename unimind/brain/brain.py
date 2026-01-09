from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional

from unimind.context import UnimindContext, UnimindPlan
from unimind.decision_matrix import DecisionMatrix
from unimind.subsystems import EthicsSubsystem
from unimind.brain.corpus_callosum import CorpusCallosum
from unimind.brain.hemispheres import LeftHemisphere, RightHemisphere
from unimind.brain.prefrontal import PrefrontalCortex
from unimind.brain.thalamus import Thalamus
from unimind.brain.types import BrainTrace


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
        self._left = LeftHemisphere()
        self._right = RightHemisphere()
        self._cc = CorpusCallosum()
        self._pfc = PrefrontalCortex(self._decision, ethics=ethics)

    def think(self, ctx: UnimindContext) -> tuple[UnimindPlan, BrainTrace]:
        state: Dict[str, Any] = {}
        trace = BrainTrace()

        state.update(self._thalamus.process(ctx, state))
        trace = BrainTrace(attention=state.get("attention") or {}, proposals=[], selected=None, notes={})

        state.update(self._left.process(ctx, state))
        state.update(self._right.process(ctx, state))

        state.update(self._cc.process(ctx, state))
        proposals = state.get("proposals") or []
        trace = BrainTrace(
            attention=trace.attention,
            proposals=[asdict(p) for p in proposals],
            selected=None,
            notes={"conflicts": state.get("conflicts") or []},
        )

        state.update(self._pfc.process(ctx, state))
        plan: UnimindPlan = state["plan"]
        trace = BrainTrace(
            attention=trace.attention,
            proposals=trace.proposals,
            selected=state.get("selected"),
            notes={**(trace.notes or {}), "scored": state.get("scored") or {}},
        )
        return plan, trace

