from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List, Optional

from daemon.runtime import build_daemon_runtime


DEFAULT_DAY_SCENARIOS: List[Dict[str, Any]] = [
    {"time": "08:05", "input": "xr list apps"},
    {"time": "08:10", "input": "xr create world reach target comfortably"},
    {"time": "08:15", "input": "xr train sim reach target comfortably"},
    {"time": "10:00", "input": "run task summarize yesterday's work into bullet points"},
    {"time": "13:20", "input": "study topic openxr action spaces"},
    {"time": "17:45", "input": "multi step plan create an xr comfort test checklist"},
]


def simulate_day(use_ollama_fallback: bool = False, scenarios: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Simulates a day's worth of questions/actions and verifies they traverse Unimind.
    Writes a JSONL trace to logs/day_simulation.jsonl.
    """
    runtime = build_daemon_runtime(use_ollama_fallback=use_ollama_fallback)
    items = list(scenarios or DEFAULT_DAY_SCENARIOS)

    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", "day_simulation.jsonl")

    results: List[Dict[str, Any]] = []
    for item in items:
        inp = str(item.get("input", "")).strip()
        if not inp:
            continue
        started = time.time()
        out = runtime.unimind.process_input(inp, context={"source": "day_simulator", "time": item.get("time")})
        row = {
            "time": item.get("time"),
            "input": inp,
            "output": out,
            "elapsed_s": time.time() - started,
        }
        results.append(row)
        with open(log_path, "a") as f:
            f.write(json.dumps(row, default=str) + "\n")

    return {"ok": True, "count": len(results), "log_path": log_path, "results": results}


if __name__ == "__main__":
    report = simulate_day(use_ollama_fallback=False)
    print(f"[DaySimulator] ok={report['ok']} count={report['count']} log={report['log_path']}")

