from typing import Any
from .base import LanguagePack

class HindiPack(LanguagePack):
    def __init__(self):
        super().__init__("hi", "Hindi")
        
        # --- Intents ---
        self.add_intent("GAME_ENTER", [r"game shuru karo", r"play game", r"enter realm"])
        self.add_intent("GAME_EXIT", [r"game band karo", r"stop game", r"exit realm"])
        self.add_intent("GREETING", [r"नमस्ते", r"hello", r"pranam", r"namaskar"])
        self.add_intent("FAREWELL", [r"alvida", r"bye", r"phir milenge"])
        self.add_intent("IDENTITY", [r"tum kaun ho", r"aap kaun hain", r"parichay"])
        self.add_intent("STATUS", [r"kaise ho", r"kya haal hai", r"status"])
        self.add_intent("CAPABILITIES", [r"kya kar sakte ho", r"madad", r"help"])
        
        # --- Responses ---
        self.add_response("GREETING", [
            "Namaste. System online hai.",
            "Namaste user, main Prometheus hoon.",
            "Main taiyaar hoon."
        ])
        
        self.add_response("FAREWELL", [
            "Alvida. Phir milenge.",
            "System band ho raha hai.",
            "Shubhraatri."
        ])
        
        self.add_response("IDENTITY", [
            "Main ek digital daemon hoon.",
            "Main Prometheus hoon, aapka saathi."
        ])
        
        self.add_response("STATUS", [
            "Sab kuch theek hai.",
            "System poori tarah se kaam kar raha hai.",
            "Sab systems operational hain."
        ])
        
        self.add_response("CAPABILITIES", [
            "Main code likh sakta hoon aur game chala sakta hoon.",
            "Meri capabilities mein code analysis aur simulation shamil hain."
        ])
        
        self.add_response("GAME_ENTER", [
            "Game shuru ho raha hai...",
            "Digital duniya mein pravesh kar rahe hain...",
            "Loading..."
        ])
        
        self.add_response("GAME_EXIT", [
            "Game se bahar aa rahe hain.",
            "Simulation band kiya ja raha hai."
        ])

    def get_fallback_response(self) -> str:
        return "Maaf kijiye, main samjha nahi."

    def format_game_response(self, topic: str, data: Any) -> str:
        if topic == "move":
            if data['success']:
                msg = f"Hum {data['location']['name']} pahunch gaye hain."
                if data.get('encounter', {}).get('occurred'):
                    msg += f"\n[ALERT] Dushman samne hai! {data['encounter']['entity']['name']}!"
                return msg
            else:
                return f"Nahi ja sakte: {data['message']}"
        elif topic == "scan":
            return f"[SCAN COMPLETE]\nTarget: {data.get('analysis', 'Unknown')}\nEntities: {', '.join(data.get('entities', []))}\nItems: {', '.join(data.get('items', []))}"
        elif topic == "status":
            loc = data['location']['name']
            hp = data['team'][0]['stats']['hp']
            return f"Sthan: {loc} | HP: {hp} | System: Online"
        elif topic == "battle":
            log = "\n".join(data.get("log", []))
            return f"[YUDDH]\n{log}"
            
        return str(data)
