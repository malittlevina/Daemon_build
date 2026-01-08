from typing import Dict, List, Any

class Unimind:
    def __init__(self):
        self.modules = {
            "logic": [],        # Reasoning, Planning (e.g., LAM)
            "emotion": [],      # Emotional State
            "memory": [],       # Codex, Short-term memory
            "ethics": [],       # Guardian
            "language": [],     # NLU
            "perception": [],   # Sensors (Vision, Audio)
            "motivation": [],   # Drives, Curiosity
            "world": []         # WorldEngine, StoryRealm
        }
        print("[Unimind] Core initialized.")

    def register(self, module_type: str, module: Any):
        if module_type in self.modules:
            self.modules[module_type].append(module)
            print(f"[Unimind] Registered module '{module.__class__.__name__}' under '{module_type}'")
        else:
            print(f"[Unimind] Warning: Unknown module type '{module_type}'. Creating new category.")
            self.modules[module_type] = [module]

    def reflect(self):
        """
        Aggregates state from all connected subsystems to form a 'Stream of Consciousness'.
        """
        print("\n[Unimind] --- System Reflection ---")
        
        # 1. Check Motivation (Why am I doing this?)
        for mod in self.modules["motivation"]:
            if hasattr(mod, "get_most_urgent_drive"):
                drive = mod.get_most_urgent_drive()
                print(f"[Unimind] dominant_drive: {drive.name} ({drive.value:.2f})")
            elif hasattr(mod, "status"):
                print(f"[Unimind] motivation_status: {mod.status()}")

        # 2. Check Perception (What do I sense?)
        for mod in self.modules["perception"]:
            # Check for generic status or last observation
            if hasattr(mod, "last_observation"):
                print(f"[Unimind] sensory_input: {mod.last_observation}")
            
        # 3. Check World State (Where am I?)
        for mod in self.modules["world"]:
            if hasattr(mod, "get_world_summary"):
                summary = mod.get_world_summary()
                print(f"[Unimind] world_context: {summary['location_count']} locations, Time: {summary['time']}")

        # 4. Run Logic/Thinking
        for mod in self.modules["logic"]:
            if hasattr(mod, "think"):
                mod.think()

        print("[Unimind] --- Reflection Complete ---\n")
