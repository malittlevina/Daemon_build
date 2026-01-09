from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Tuple


@dataclass(frozen=True)
class ScoreBreakdown:
    score: float
    weighted: Dict[str, float]
    inputs: Dict[str, float]
    weights: Dict[str, float]

    @property
    def rationale(self) -> str:
        parts = [f"{k}={self.weighted[k]:.3f}" for k in sorted(self.weighted)]
        return " + ".join(parts) + f" => {self.score:.3f}"


class DecisionMatrix:
    """
    Weighted multi-signal scorer.

    Backward compatible with the earlier `evaluate(inputs)` and `choose(options)`
    but now supports a rationale breakdown for agent debugging.
    """

    def __init__(self, weights: Mapping[str, float] | None = None):
        self.weights: Dict[str, float] = dict(
            weights
            or {
                "logic": 0.4,
                "emotion": 0.2,
                "memory": 0.3,
                "intuition": 0.1,
            }
        )

    def evaluate(self, inputs: Mapping[str, float]) -> float:
        return self.evaluate_breakdown(inputs).score

    def evaluate_breakdown(self, inputs: Mapping[str, float]) -> ScoreBreakdown:
        weighted: Dict[str, float] = {}
        total = 0.0
        for key, value in inputs.items():
            w = float(self.weights.get(key, 0.0))
            v = float(value)
            weighted[key] = w * v
            total += weighted[key]
        return ScoreBreakdown(
            score=total,
            weighted=weighted,
            inputs=dict(inputs),
            weights=dict(self.weights),
        )

    def choose(self, options: Mapping[str, Mapping[str, float]]) -> str:
        best, _ = self.choose_with_rationale(options)
        return best

    def choose_with_rationale(
        self, options: Mapping[str, Mapping[str, float]]
    ) -> Tuple[str, Dict[str, Dict[str, object]]]:
        """
        Returns:
        - best option key
        - scored dict: option -> {score, rationale, breakdown}
        """
        scored: Dict[str, Dict[str, object]] = {}
        best_key = None
        best_score = float("-inf")
        for k, v in options.items():
            breakdown = self.evaluate_breakdown(v)
            scored[k] = {
                "score": breakdown.score,
                "rationale": breakdown.rationale,
                "breakdown": {
                    "weighted": breakdown.weighted,
                    "inputs": breakdown.inputs,
                    "weights": breakdown.weights,
                },
            }
            if breakdown.score > best_score:
                best_score = breakdown.score
                best_key = k
        # If options is empty, fail loudly and early: it's a caller bug.
        if best_key is None:
            raise ValueError("DecisionMatrix.choose_with_rationale() requires non-empty options")
        return best_key, scored
