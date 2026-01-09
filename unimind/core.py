from core.events import EventBus, Event

class Unimind:
    def __init__(self):
        self.modules = {
            "logic": [],
            "emotion": [],
            "memory": [],
            "ethics": [],
            "language": []
        }
        self.bus = None
        print("[Unimind] Core initialized.")

    def register(self, type, module):
        if type in self.modules:
            self.modules[type].append(module)
            print(f"[Unimind] Registered module under '{type}'")

    def register_events(self, bus: EventBus):
        self.bus = bus
        bus.subscribe("game:moved", self._on_game_move)
        bus.subscribe("game:encounter", self._on_game_encounter)
        bus.subscribe("game:battle_end", self._on_battle_end)
        print("[Unimind] Subscribed to game events.")

    def _on_game_move(self, event: Event):
        # Log or react
        # print(f"[Unimind Observation] Player moved to {event.payload.get('location')}")
        pass

    def _on_game_encounter(self, event: Event):
        print(f"[Unimind Analysis] Threat detected: {event.payload.get('entity')}. Suggest analyzing weakness.")
        # Future: Trigger automated scan if authorized

    def _on_battle_end(self, event: Event):
        winner = event.payload.get("winner")
        if winner == "player":
             print("[Unimind] Victory observed. Updating strategy matrix.")
        else:
             print("[Unimind] Defeat observed. Recommending retreat protocols.")

    def reflect(self):
        print("[Unimind] Running reflection loop...")
        for logic_module in self.modules["logic"]:
            logic_module.think()
