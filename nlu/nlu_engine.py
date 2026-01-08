from core.module import Module
import os
import datetime
import subprocess

# Stubs for missing modules or future implementation
def log_codex_entry(tag, summary):
    # TODO: Connect to actual Codex module via Kernel
    print(f"[Codex Stub] {tag}: {summary}")

def symbolic_reasoning_chain(query):
    return f"Reasoning about {query}..."

def propose_improvements(context):
    return "Optimize everything."

def update_state_with_input(input_text, source="user"):
    # TODO: Connect to LAM
    return None

REFLECTION_LOG = "logs/self_reflection.log"
MAX_LOG_SIZE = 10000  # characters

class NLUEngine(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.learned_phrases = {}
        self.use_ollama_fallback = True
        self.scroll_engine = None # Will be resolved from kernel

    def initialize(self):
        print("[NLUEngine] Initialized.")
        self.scroll_engine = self.kernel.get_module("scrolls")

    def start(self):
        pass

    def stop(self):
        pass

    def interpret(self, user_input):
        if user_input in self.learned_phrases:
            return self.learned_phrases[user_input]

        # Pattern match for known phrases
        if "learn python" in user_input.lower():
            response = "Let's dive into Python basics!"
            self.learned_phrases[user_input] = response
            return response

        # Try LAM state update (stubbed)
        try:
            result = update_state_with_input(user_input, source="nlu")
            if result:
                return result
        except Exception as e:
            print(f"[NLUEngine] LAM update failed: {e}")

        # Ollama Fallback
        if self.use_ollama_fallback:
            try:
                # Check if ollama is installed/running before calling subprocess
                # For now, we assume it might fail if not present
                result = subprocess.run(["ollama", "run", "prometheus", user_input], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    return "[NLUEngine] Ollama fallback failed or model not found."
            except FileNotFoundError:
                return "[NLUEngine] Ollama not installed."
            except Exception as e:
                return f"[NLUEngine] Fallback exception: {e}"

        return "[NLUEngine] No known intent"

# Kept as standalone functions or move to a separate util module if needed
def run_self_analysis():
    reflection = {}
    reflection["timestamp"] = str(datetime.datetime.now())
    reflection["status"] = "Running self-analysis"
    reflection["reasoning_trace"] = symbolic_reasoning_chain("analyze internal state for weaknesses")
    reflection["proposed_improvements"] = propose_improvements("Nightly self-analysis of daemon")
    
    codex_summary = (
        f"Self-reflection at {reflection['timestamp']}\n"
        f"Status: {reflection['status']}\n"
        f"Symbolic Reasoning: {reflection['reasoning_trace']}\n"
        f"Proposed Fixes: {reflection['proposed_improvements']}"
    )
    log_codex_entry("reflection", codex_summary)
    
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
