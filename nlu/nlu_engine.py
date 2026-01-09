import os
import datetime
# from codex.codex_engine import log_codex_entry 
# from code.code_generator import propose_improvements 
# from unimind.reasoner import symbolic_reasoning_chain 
# from lam.symbolic_state import update_state_with_input 

from storyrealms.storyrealm_bridge import enter_storyrealm, process_action
from nlu.languages.registry import LanguageRegistry

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

        # 6. Fallback
        if self.use_ollama_fallback:
            try:
                import subprocess
                # Pass a system prompt to Ollama to respond in the target language if possible, 
                # but standard Ollama might just reply in English. 
                # We'll just append a "respond in [Language]" instruction if needed, 
                # but for now keep it simple.
                result = subprocess.run(["ollama", "run", "llama3", user_input], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    return f"[NLUEngine] Ollama fallback failed (code {result.returncode})."
            except FileNotFoundError:
                return "[NLUEngine] Ollama not found."
            except Exception as e:
                return f"[NLUEngine] Fallback exception: {e}"

        return self.current_lang.get_fallback_response()

    def _handle_game_input(self, text):
        # Basic Multilingual Support for Game Commands via Regex/Keywords could be added here
        # For now, we rely on English keywords OR we could add GAME_MOVE to the packs.
        # Let's support at least the keywords in the packs if we added them? 
        # I didn't add explicit MOVE/ATTACK intents to packs yet, just ENTER/EXIT.
        # I'll stick to English command parsing for mechanics, but localized output.
        
        parts = text.split()
        command = parts[0]
        
        # Simple aliasing for other languages could be done here if I had a dictionary.
        # For now, English commands.
        
        if command in ["move", "walk", "go"]:
            direction = parts[1] if len(parts) > 1 else None
            if direction:
                res = process_action("move", {"direction": direction})
                return self.current_lang.format_game_response("move", res)
            return "Direction?" # Should localize
            
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
