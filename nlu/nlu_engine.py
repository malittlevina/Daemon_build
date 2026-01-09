import os
import datetime
# from codex.codex_engine import log_codex_entry 
# from code.code_generator import propose_improvements 
# from unimind.reasoner import symbolic_reasoning_chain 
# from lam.symbolic_state import update_state_with_input 

from storyrealms.storyrealm_bridge import enter_storyrealm, process_action
from nlu.languages.registry import LanguageRegistry

# Lazy load Unimind to avoid circular import if needed, 
# but usually it's fine if Unimind doesn't import NLU.
from core.kernel import get_kernel 

REFLECTION_LOG = "logs/self_reflection.log"
MAX_LOG_SIZE = 10000  # characters

class NLUEngine:
    def __init__(self, scrolls_engine=None):
        self.learned_phrases = {}
        self.use_ollama_fallback = True
        self.scrolls = scrolls_engine
        self.in_game_mode = False
        
        # New Multilingual System
        self.registry = LanguageRegistry()
        self.current_lang_code = "en"
        self.current_lang = self.registry.get_language("en")

    def interpret(self, user_input):
        user_input_lower = user_input.lower()
        
        # 0. Consult Unimind for Global Analysis
        # We check if Unimind is available via Kernel
        kernel = get_kernel()
        unimind_response = None
        if "unimind" in kernel.modules:
            unimind = kernel.modules["unimind"]
            # Create a context for the Unimind
            ctx = {"user_input": user_input}
            unimind_response = unimind.think(ctx)
            
            # Check if Unimind blocked the action
            if unimind_response.get("action_blocked"):
                return f"[Unimind Safety] Action Blocked: {unimind_response.get('block_reason')}"

        # 1. Language Switch Check
        new_lang_code = self.registry.detect_language_switch(user_input_lower)
        if new_lang_code:
            self.current_lang_code = new_lang_code
            self.current_lang = self.registry.get_language(new_lang_code)
            return self.current_lang.get_response("GREETING") # Acknowledge switch with greeting

        # 2. Intent Recognition via Language Pack
        intent = self.current_lang.get_intent(user_input_lower)

        # 3. Handle Game Toggle via Intent
        if intent == "GAME_ENTER":
            self.in_game_mode = True
            result = enter_storyrealm("Digital Frontier")
            # Format status response in current language
            formatted_status = self.current_lang.format_game_response("status", result)
            return self.current_lang.get_response(intent) + "\n" + formatted_status
        
        if intent == "GAME_EXIT":
            self.in_game_mode = False
            return self.current_lang.get_response(intent)

        # 4. Handle Game Mode
        if self.in_game_mode:
            return self._handle_game_input(user_input_lower)

        # 5. Handle General Conversation Intents
        if intent:
            return self.current_lang.get_response(intent)

        # 6. Fallback (Augmented by Unimind Creative Suggestion)
        if self.use_ollama_fallback:
            try:
                # If Unimind had a creative suggestion, prepend it to the context?
                # Or just append it to the output?
                creative_note = ""
                if unimind_response and "creative_suggestion" in unimind_response:
                    creative_note = f"\n[Unimind Idea]: {unimind_response['creative_suggestion']}"

                import subprocess
                result = subprocess.run(["ollama", "run", "llama3", user_input], capture_output=True, text=True)
                if result.returncode == 0:
                    output = result.stdout.strip()
                    return output + creative_note
                else:
                    return f"[NLUEngine] Ollama fallback failed (code {result.returncode}).{creative_note}"
            except FileNotFoundError:
                return f"[NLUEngine] Ollama not found.{creative_note}" if 'creative_note' in locals() else "[NLUEngine] Ollama not found."
            except Exception as e:
                return f"[NLUEngine] Fallback exception: {e}"

        return self.current_lang.get_fallback_response()

    def _handle_game_input(self, text):
        parts = text.split()
        command = parts[0]
        
        if command in ["move", "walk", "go"]:
            direction = parts[1] if len(parts) > 1 else None
            if direction:
                res = process_action("move", {"direction": direction})
                return self.current_lang.format_game_response("move", res)
            return "Direction?" 
            
        elif command == "scan":
             res = process_action("scan", {})
             return self.current_lang.format_game_response("scan", res)
             
        elif command in ["status", "look"]:
             res = process_action("status", {})
             return self.current_lang.format_game_response("status", res)
             
        elif command in ["attack", "fight"]:
             res = process_action("battle_action", {"move_idx": 0, "target_idx": 0})
             return self.current_lang.format_game_response("battle", res)
        
        return f"[StoryRealm] {self.current_lang.get_fallback_response()}"

# Placeholder for broken imports functions
def run_self_analysis():
    return "Self-analysis not implemented (missing dependencies)."

def nightly_reflection():
    print("[SelfReflector] Executing nightly reflection...")
    result = run_self_analysis()
    print("[SelfReflector] Reflection complete.")
    return result
