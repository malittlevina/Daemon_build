from typing import Any
from .base import LanguagePack

class EnglishPack(LanguagePack):
    def __init__(self):
        super().__init__("en", "English")
        
        # --- Intents ---
        self.add_intent("GREETING", [r"\bhello\b", r"\bhi\b", r"\bgreetings\b", r"\bhey\b"])
        self.add_intent("FAREWELL", [r"\bbye\b", r"\bgoodbye\b", r"\bexit\b", r"\bquit\b"])
        self.add_intent("IDENTITY", [r"who are you", r"what are you", r"identify yourself"])
        self.add_intent("STATUS", [r"how are you", r"status report", r"system status", r"diagnostic"])
        self.add_intent("CAPABILITIES", [r"what can you do", r"help", r"capabilities"])
        self.add_intent("GAME_ENTER", [r"enter realm", r"play game", r"start simulation", r"enter storyrealm"])
        self.add_intent("GAME_EXIT", [r"exit realm", r"stop game", r"end simulation"])
        
        # --- Responses ---
        self.add_response("GREETING", [
            "Greetings, user. The system is online and listening.",
            "Hello. I am Prometheus, your digital daemon. How may I assist?",
            "System synchronization complete. Greetings.",
            "I am here. What is your command?",
            "Salutations. The digital winds are favorable today."
        ])
        
        self.add_response("FAREWELL", [
            "Powering down interaction modules. Goodbye.",
            "Until next time. Stay safe in the physical realm.",
            " terminating session. Farewell.",
            "Rest mode engaged. Goodbye."
        ])
        
        self.add_response("IDENTITY", [
            "I am a symbolic operating daemon, designed to assist and evolve.",
            "I am Prometheus, an AI agent running within the Cursor environment.",
            "I am your code-native companion, bridging logic and creativity."
        ])
        
        self.add_response("STATUS", [
            "All systems nominal. CPU load is within acceptable parameters.",
            "I am functioning at optimal capacity.",
            "Internal diagnostics show green across the board.",
            "Memory integrity is 100%. I am ready."
        ])
        
        self.add_response("CAPABILITIES", [
            "I can analyze code, manage your tasks, and accompany you into the Story Realm.",
            "My functions include system introspection, code generation, and running the Story Realm simulation.",
            "Ask me to 'enter realm' to begin our adventure, or 'status' for a system check."
        ])
        
        self.add_response("GAME_ENTER", [
            "Initializing Story Realm connection... Stand by.",
            "Connecting to the Digital Frontier...",
            "Loading simulation matrix. Prepare for transfer."
        ])
        
        self.add_response("GAME_EXIT", [
            "Disconnecting from Story Realm. Welcome back to the terminal.",
            "Simulation suspended. Saving state.",
            "Closing the bridge. Reality restored."
        ])

    def get_fallback_response(self) -> str:
        options = [
            "I did not register that command in my database.",
            "Could you rephrase that? My linguistic parsers are uncertain.",
            "Input unclear. Please specify your intent.",
            "I am listening, but I do not understand."
        ]
        import random
        return random.choice(options)
    
    def format_game_response(self, topic: str, data: Any) -> str:
        if topic == "move":
            if data['success']:
                msg = f"Traversal successful. We have arrived at {data['location']['name']}."
                if data.get('encounter', {}).get('occurred'):
                    msg += f"\n[ALERT] Hostile entity detected! A {data['encounter']['entity']['name']} blocks our path!"
                return msg
            else:
                return f"Movement failed: {data['message']}"
        elif topic == "scan":
            return f"[SCAN COMPLETE]\nTarget: {data.get('analysis', 'Unknown')}\nEntities: {', '.join(data.get('entities', []))}\nItems: {', '.join(data.get('items', []))}"
        elif topic == "status":
            loc = data['location']['name']
            hp = data['team'][0]['stats']['hp']
            return f"Current Location: {loc} | Leader HP: {hp} | Systems: Online"
            
        return str(data)
