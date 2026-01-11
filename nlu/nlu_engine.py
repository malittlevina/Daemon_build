from __future__ import annotations

from typing import Any, Dict, Optional

from lam.symbolic_state import update_state_with_input

class NLUEngine:
    def __init__(self, scroll_engine=None, use_ollama_fallback: bool = False):
        self.learned_phrases = {}
        self.use_ollama_fallback = bool(use_ollama_fallback)
        self.scroll_engine = scroll_engine

    def interpret(self, user_input):
        if user_input in self.learned_phrases:
            return self.learned_phrases[user_input]

        text = (user_input or "").strip()
        text_l = text.lower()

        # XR direct commands (pass-through to ScrollEngine)
        # Examples:
        # - "xr list apps"
        # - "xr create world reach target comfortably"
        # - "xr train sim practice teleport comfort" (goal inferred from remainder)
        if self.scroll_engine and (text_l == "xr list apps" or text_l.startswith("xr ")):
            try:
                return self._route_xr(text)
            except Exception as e:
                return f"[NLUEngine] XR routing failed: {e}"

        try:
            # Keep symbolic state in sync with the input.
            update_state_with_input(text)
            result = None
        except Exception:
            result = None

        if result:
            return result

        if self.use_ollama_fallback:
            try:
                import subprocess
                proc = subprocess.run(["ollama", "run", "prometheus", text], capture_output=True, text=True)
                if proc.returncode == 0:
                    return proc.stdout.strip()
                else:
                    return "[NLUEngine] Ollama fallback failed."
            except Exception as e:
                return f"[NLUEngine] Fallback exception: {e}"

        return "[NLUEngine] No known intent"

    def plan(self, user_input: str) -> Optional[Dict[str, Any]]:
        """
        Side-effect free intent planning.

        Returns a structured intent dict, or None if no intent recognized.
        This is what Unimind should use before executing actions.
        """
        text = (user_input or "").strip()
        text_l = text.lower()

        if text_l == "xr list apps":
            return {"intent": "xr.list_apps"}
        if text_l.startswith("xr launch app "):
            return {"intent": "xr.launch_app", "app": text[len("xr launch app ") :].strip(), "dry_run": True}
        if text_l.startswith("xr create world "):
            return {"intent": "xr.create_world", "goal": text[len("xr create world ") :].strip(), "kind": "xr"}
        if text_l.startswith("xr train sim "):
            return {
                "intent": "xr.train_sim",
                "goal": text[len("xr train sim ") :].strip(),
                "kind": "xr",
                "steps": 300,
                "delete_raw_run": True,
            }
        return None

    def _route_xr(self, text: str) -> Any:
        """
        Minimal XR command router to ScrollEngine.
        """
        parts = [p for p in (text or "").strip().split(" ") if p]
        if len(parts) < 2:
            return "[NLUEngine] XR command incomplete."

        # "xr list apps"
        if parts[:3] == ["xr", "list", "apps"]:
            return self.scroll_engine.invoke("xr list apps")

        # "xr launch app <name_or_id>"
        if len(parts) >= 4 and parts[:3] == ["xr", "launch", "app"]:
            app = " ".join(parts[3:])
            return self.scroll_engine.invoke("xr launch app", app, True)

        # "xr create world <goal...>"
        if len(parts) >= 4 and parts[:3] == ["xr", "create", "world"]:
            goal = " ".join(parts[3:])
            return self.scroll_engine.invoke("xr create world", goal, "xr")

        # "xr train sim <goal...>"
        if len(parts) >= 4 and parts[:3] == ["xr", "train", "sim"]:
            goal = " ".join(parts[3:])
            return self.scroll_engine.invoke("xr train sim", goal, "xr", 300, True)

        return "[NLUEngine] XR command not recognized."