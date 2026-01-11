from __future__ import annotations

from typing import Any, Dict, List, Optional

from daemon.runtime import build_daemon_runtime
from unimind.simulations.scenario_runner import Expectation, Scenario, run_scenarios


DEFAULT_DAY_SCENARIOS: List[Dict[str, Any]] = [
    {"time": "08:05", "input": "xr list apps", "expect": {"output_type": "dict", "dict_has_keys": ["ok", "apps"]}},
    {"time": "08:10", "input": "xr create world reach target comfortably", "expect": {"output_type": "dict", "dict_has_keys": ["ok", "world"]}},
    {"time": "08:15", "input": "xr train sim reach target comfortably", "expect": {"output_type": "dict", "dict_has_keys": ["ok", "knowledge_paths", "deleted_raw_run"]}},
    {"time": "10:00", "input": "run task summarize yesterday's work into bullet points", "expect": {"output_type": "str", "contains": "Task completed:"}},
    {"time": "13:20", "input": "study topic openxr action spaces", "expect": {"output_type": "str", "contains": "Scroll triggered self-study"}},
    {"time": "17:45", "input": "multi step plan create an xr comfort test checklist", "expect": {"output_type": "str", "contains": "[Planner]"}},
]


def simulate_day(use_ollama_fallback: bool = False, scenarios: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Simulates a day's worth of questions/actions and regression-checks expected outputs.
    Writes a JSONL trace to logs/day_simulation.jsonl and a summary report to logs/day_simulation_report.json.
    """
    runtime = build_daemon_runtime(use_ollama_fallback=use_ollama_fallback)
    items = list(scenarios or DEFAULT_DAY_SCENARIOS)

    scs: List[Scenario] = []
    for idx, item in enumerate(items):
        inp = str(item.get("input", "")).strip()
        if not inp:
            continue
        exp_raw = item.get("expect", {}) or {}
        scs.append(
            Scenario(
                name=f"{idx:02d}-{item.get('time','??:??')}",
                input=inp,
                meta={"time": item.get("time"), "source": "day_simulator"},
                expect=Expectation(
                    output_type=exp_raw.get("output_type"),
                    contains=exp_raw.get("contains"),
                    dict_has_keys=list(exp_raw.get("dict_has_keys") or []),
                ),
            )
        )

    report = run_scenarios(runtime.unimind, scs, log_path="logs/day_simulation.jsonl")
    report["log_path"] = "logs/day_simulation.jsonl"
    report["count"] = len(scs)
    return report


if __name__ == "__main__":
    report = simulate_day(use_ollama_fallback=False)
    print(f"[DaySimulator] ok={report['ok']} passed={report['passed']} failed={report['failed']} log={report['log_path']}")

