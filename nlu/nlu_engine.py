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
        self.kernel.log("NLUEngine", "Initialized.")
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
            # Connect to Symbolic Module
            symbolic = self.kernel.get_module("symbolic")
            if symbolic:
                # We might want to just check state, or update it.
                # If we update it here, we duplicate the event listener in SymbolicLayer.
                # So we should probably just READ it here if needed, or rely on SymbolicLayer to update via event.
                # However, NLU might want to influence state interpretation.
                # For now, let's assume SymbolicLayer handles "user_input" event for history,
                # but NLU might want to explicitly set "intent".
                pass
        except Exception as e:
            self.kernel.log("NLUEngine", f"LAM access failed: {e}", level="error")

        # Ollama Fallback
        if self.use_ollama_fallback:
            try:
                # Check if ollama is installed/running before calling subprocess
                result = subprocess.run(["ollama", "run", "prometheus", user_input], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            except FileNotFoundError:
                pass # Fall through to simple chatbot
            except Exception as e:
                self.kernel.log("NLUEngine", f"Fallback exception: {e}", level="error")

        # Simple Rule-Based Chatbot (The "Lizard" Brain)
        return self._simple_chat(user_input)

    def _simple_chat(self, text):
        text = text.lower()
        if "who are you" in text:
            return "I am Thoth, a Symbolic Operating System."
        if "status" in text:
            return "Systems operational. World Engine active."
        if "hello" in text or "hi" in text:
            return "Greetings, User."
        if "time" in text:
            return f"The current system time is {datetime.datetime.now().strftime('%H:%M')}."
        return f"I heard '{text}', but I lack the neural capacity to process it fully."

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
    # This is a standalone helper used by main.py directly, doesn't have kernel access easily
    # unless we pass it or refactor. For now, leave print or redirect to a global logger?
    # We will leave print as it's run by a background thread in main.py not via kernel modules strictly.
    result = run_self_analysis()
    print("[SelfReflector] Reflection complete.")
    return result
