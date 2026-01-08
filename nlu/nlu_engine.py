from __future__ import annotations

import datetime
import os
import subprocess
from typing import Any, Optional

from lam.symbolic_state import update_state_with_input

REFLECTION_LOG = "logs/self_reflection.log"
MAX_LOG_SIZE = 10_000  # characters


class NLUEngine:
    """
    Lightweight NLU router for the daemon build.

    This module is intentionally dependency-light: it should not import optional
    Codex/Reasoner components at import-time. The kernel can provide richer
    reasoning later via subsystem registration + event bus.
    """

    def __init__(self, scrolls: Optional[Any] = None) -> None:
        self.scrolls = scrolls
        self.learned_phrases: dict[str, str] = {}
        self.use_ollama_fallback = False

    def interpret(self, user_input: str) -> str:
        text = (user_input or "").strip()
        if not text:
            return "[NLUEngine] No known intent."

        if text in self.learned_phrases:
            return self.learned_phrases[text]

        lower = text.lower()

        # Minimal, high-signal intent routing into ScrollEngine.
        if self.scrolls is not None and hasattr(self.scrolls, "invoke"):
            if lower in {"optimize self", "optimize"}:
                return str(self.scrolls.invoke("optimize self"))
            if lower.startswith("study "):
                topic = text[6:].strip()
                return str(self.scrolls.invoke("study topic", topic))
            if lower.startswith("run task "):
                task = text[len("run task ") :].strip()
                return str(self.scrolls.invoke("run task", task))
            if lower.startswith("multi step plan "):
                goal = text[len("multi step plan ") :].strip()
                return str(self.scrolls.invoke("multi step plan", goal))

        # Update symbolic state as a baseline kernel service.
        try:
            update_state_with_input(text)
        except Exception:
            pass

        if self.use_ollama_fallback:
            try:
                result = subprocess.run(
                    ["ollama", "run", "prometheus", text],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
                return "[NLUEngine] Ollama fallback failed."
            except Exception as e:
                return f"[NLUEngine] Fallback exception: {e}"

        return "[NLUEngine] No known intent."


def run_self_analysis() -> str:
    """
    Nightly self-analysis hook.

    In this repo, the durable side effect is logging an "improvement proposal"
    using `code_tools.code_generator`.
    """

    reflection = {
        "timestamp": str(datetime.datetime.now()),
        "status": "Running self-analysis",
    }

    try:
        from code_tools.code_generator import propose_improvements

        reflection["proposed_improvements"] = propose_improvements("Nightly self-analysis of daemon")
    except Exception as e:
        reflection["proposed_improvements"] = f"[SelfReflector] Improvement logging failed: {e}"

    summary = (
        f"Self-reflection at {reflection['timestamp']}\n"
        f"Status: {reflection['status']}\n"
        f"Proposed Fixes: {reflection['proposed_improvements']}"
    )

    os.makedirs(os.path.dirname(REFLECTION_LOG) or ".", exist_ok=True)
    with open(REFLECTION_LOG, "a") as log_file:
        log_file.write(summary + "\n\n")

    truncate_log_if_needed()
    return summary


def truncate_log_if_needed() -> None:
    if not os.path.exists(REFLECTION_LOG):
        return
    with open(REFLECTION_LOG, "r") as f:
        content = f.read()
    if len(content) <= MAX_LOG_SIZE:
        return
    with open(REFLECTION_LOG, "w") as f:
        f.write(content[-MAX_LOG_SIZE:])


def nightly_reflection() -> str:
    print("[SelfReflector] Executing nightly reflection...")
    result = run_self_analysis()
    print("[SelfReflector] Reflection complete.")
    return result