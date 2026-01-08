import os
import datetime
# from codex.codex_engine import log_codex_entry
def log_codex_entry(tag, content):
    print(f"[Codex] Logged {tag}")

from code_tools.code_generator import propose_improvements
# from unimind.reasoner import symbolic_reasoning_chain
def symbolic_reasoning_chain(prompt):
    return f"Symbolic reasoning for: {prompt}"

from lam.symbolic_state import update_state_with_input

REFLECTION_LOG = "logs/self_reflection.log"
MAX_LOG_SIZE = 10000  # characters

class NLUEngine:
    def __init__(self, scroll_engine=None): # Added scroll_engine arg to match main.py usage
        self.learned_phrases = {}
        self.use_ollama_fallback = True
        self.scroll_engine = scroll_engine

    def interpret(self, user_input):
        if user_input in self.learned_phrases:
            return self.learned_phrases[user_input]

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
                # Check if ollama is actually available before running
                # For now just catch exception
                result = subprocess.run(["ollama", "run", "prometheus", user_input], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    return "[NLUEngine] Ollama fallback failed."
            except FileNotFoundError:
                 return "[NLUEngine] Ollama not installed."
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