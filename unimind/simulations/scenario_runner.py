from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Expectation:
    """
    Simple expectation language for regression scenarios.
    """

    output_type: Optional[str] = None  # "str", "dict", etc.
    contains: Optional[str] = None  # substring expected in str(output) or json(output)
    dict_has_keys: List[str] = field(default_factory=list)  # keys expected in dict output


@dataclass
class Scenario:
    name: str
    input: str
    meta: Dict[str, Any] = field(default_factory=dict)
    expect: Expectation = field(default_factory=Expectation)


def _stringify_output(output: Any) -> str:
    try:
        return json.dumps(output, default=str, sort_keys=True)
    except Exception:
        return str(output)


def run_scenarios(unimind, scenarios: List[Scenario], log_path: str = "logs/day_simulation.jsonl") -> Dict[str, Any]:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    results: List[Dict[str, Any]] = []
    passed = 0

    for sc in scenarios:
        started = time.time()
        out = unimind.process_input(sc.input, context={"source": "scenario_runner", **(sc.meta or {})})
        elapsed = time.time() - started

        ok = True
        reasons: List[str] = []

        if sc.expect.output_type:
            if type(out).__name__ != sc.expect.output_type:
                ok = False
                reasons.append(f"output_type expected {sc.expect.output_type} got {type(out).__name__}")

        if sc.expect.dict_has_keys:
            if not isinstance(out, dict):
                ok = False
                reasons.append("expected dict output")
            else:
                for k in sc.expect.dict_has_keys:
                    if k not in out:
                        ok = False
                        reasons.append(f"missing key: {k}")

        if sc.expect.contains:
            blob = _stringify_output(out)
            if sc.expect.contains not in blob:
                ok = False
                reasons.append(f"missing substring: {sc.expect.contains}")

        row = {
            "name": sc.name,
            "input": sc.input,
            "output": out,
            "ok": ok,
            "reasons": reasons,
            "elapsed_s": elapsed,
        }
        results.append(row)
        if ok:
            passed += 1

        with open(log_path, "a") as f:
            f.write(json.dumps({**row, "output": _stringify_output(out)}, default=str) + "\n")

    report = {"ok": passed == len(scenarios), "passed": passed, "failed": len(scenarios) - passed, "results": results}
    with open("logs/day_simulation_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    return report

