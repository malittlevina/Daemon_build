import os
import datetime
# from codex.codex_engine import log_codex_entry
# from code.code_generator import propose_improvements
# from unimind.reasoner import symbolic_reasoning_chain
from lam.symbolic_state import update_state_with_input

REFLECTION_LOG = "logs/self_reflection.log"
MAX_LOG_SIZE = 10000  # characters

class NLUEngine:
    def __init__(self, scrolls=None, world_engine=None):
        self.scrolls = scrolls
        self.world_engine = world_engine
        self.learned_phrases = {}
        self.use_ollama_fallback = True

    def interpret(self, user_input):
        if user_input in self.learned_phrases:
            return self.learned_phrases[user_input]
        
        # Check world context
        if self.world_engine:
            context = self.world_engine.get_current_context()
            # In a real implementation, we would use this context to bias the NLU
            # For now, we just print it to show awareness
            # print(f"[NLU Context] {context}")

        # Basic command handling via scrolls
        if self.scrolls:
            # Simple keyword matching for scrolls
            if "change realm" in user_input.lower():
                parts = user_input.split("to")
                if len(parts) > 1:
                    realm_name = parts[1].strip()
                    return self.scrolls.invoke("change realm", realm_name)

        # Pattern match for known phrases
        if "learn python" in user_input.lower():
            response = "Let's dive into Python basics!"
            self.learned_phrases[user_input] = response
            return response

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
    reflection["reasoning_trace"] = symbolic_reasoning_chain("analyze internal state for weaknesses")

    # Improvement suggestions
    reflection["proposed_improvements"] = propose_improvements("Nightly self-analysis of daemon")

    # Log reflection to Codex
    codex_summary = (
        f"Self-reflection at {reflection['timestamp']}\n"
        f"Status: {reflection['status']}\n"
        f"Symbolic Reasoning: {reflection['reasoning_trace']}\n"
        f"Proposed Fixes: {reflection['proposed_improvements']}"
    )
    log_codex_entry("reflection", codex_summary)

    # Append to local log
    with open(REFLECTION_LOG, "a") as log_file:
        log_file.write(codex_summary + "\n\n")

    truncate_log_if_needed()

    return codex_summary

def truncate_log_if_needed():
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