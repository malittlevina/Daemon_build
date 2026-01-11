import datetime
from lam.symbolic_state import update_state_with_input

REFLECTION_LOG = "logs/self_reflection.log"
MAX_LOG_SIZE = 10000  # characters

class NLUEngine:
    def __init__(self, scroll_engine=None):
        self.learned_phrases = {}
        self.use_ollama_fallback = True
        # Optional: retained for backward compatibility with main.py
        self.scroll_engine = scroll_engine

    def interpret(self, user_input):
        if user_input in self.learned_phrases:
            return self.learned_phrases[user_input]

        # Pattern match for known phrases
        if "learn python" in user_input.lower():
            response = "Let's dive into Python basics!"
            self.learned_phrases[user_input] = response
            return response

        # Prefer symbolic-state routing (where robotics control is integrated).
        try:
            result = update_state_with_input(user_input, source="nlu")
        except TypeError:
            result = update_state_with_input(user_input)

        if result:
            return result

        if self.use_ollama_fallback:
            try:
                import subprocess
                result = subprocess.run(["ollama", "run", "prometheus", user_input], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    return "[NLUEngine] Ollama fallback failed."
            except Exception as e:
                return f"[NLUEngine] Fallback exception: {e}"

        return "[NLUEngine] No known intent"

def run_self_analysis():
    reflection = {}

    # Symbolic diagnostic prompt
    reflection["timestamp"] = str(datetime.datetime.now())
    reflection["status"] = "Running self-analysis"
    # Optional hooks (these modules may not exist yet in this build)
    try:
        from unimind.reasoner import symbolic_reasoning_chain  # type: ignore
        reflection["reasoning_trace"] = symbolic_reasoning_chain("analyze internal state for weaknesses")
    except Exception as e:
        reflection["reasoning_trace"] = f"[SelfAnalysis] Reasoner unavailable: {e}"

    # Improvement suggestions
    try:
        from code_tools.code_generator import propose_improvements  # type: ignore
        reflection["proposed_improvements"] = propose_improvements("Nightly self-analysis of daemon")
    except Exception as e:
        reflection["proposed_improvements"] = f"[SelfAnalysis] Code generator unavailable: {e}"

    # Log reflection to Codex
    codex_summary = (
        f"Self-reflection at {reflection['timestamp']}\n"
        f"Status: {reflection['status']}\n"
        f"Symbolic Reasoning: {reflection['reasoning_trace']}\n"
        f"Proposed Fixes: {reflection['proposed_improvements']}"
    )
    try:
        from codex.ingestion import ingest_observation  # type: ignore
        ingest_observation(codex_summary)
    except Exception:
        # Keep reflection runnable even if codex ingestion isn't available.
        pass

    # Append to local log
    with open(REFLECTION_LOG, "a") as log_file:
        log_file.write(codex_summary + "\n\n")

    truncate_log_if_needed()

    return codex_summary

def truncate_log_if_needed():
    import os
    if not os.path.exists(REFLECTION_LOG):
        return
    with open(REFLECTION_LOG, "r") as f:
        content = f.read()
    if len(content) > MAX_LOG_SIZE:
        with open(REFLECTION_LOG, "w") as f:
            f.write(content[-MAX_LOG_SIZE:])

def nightly_reflection():
    print("[SelfReflector] Executing nightly reflection...")
    result = run_self_analysis()
    print("[SelfReflector] Reflection complete.")
    return result