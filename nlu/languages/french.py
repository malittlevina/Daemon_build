from typing import Any
from .base import LanguagePack

class FrenchPack(LanguagePack):
    def __init__(self):
        super().__init__("fr", "French")
        
        # --- Intents ---
        self.add_intent("GAME_ENTER", [r"jouer", r"lancer le jeu", r"entrer"])
        self.add_intent("GAME_EXIT", [r"arr.ter le jeu", r"quitter le jeu", r"stop"])
        self.add_intent("GREETING", [r"\bbonjour\b", r"\bsalut\b", r"\bcoucou\b"])
        self.add_intent("FAREWELL", [r"\bau revoir\b", r"\badieu\b", r"\bquitter\b"])
        self.add_intent("IDENTITY", [r"qui es-tu", r"identit.", r"t'es qui"])
        self.add_intent("STATUS", [r"comment .a va", r"statut", r".tat"])
        self.add_intent("CAPABILITIES", [r"que peux-tu faire", r"aide", r"capacit.s"])
        
        # --- Responses ---
        self.add_response("GREETING", [
            "Bonjour. Système en ligne.",
            "Salutations. Je suis Prometheus.",
            "Prêt à servir."
        ])
        
        self.add_response("FAREWELL", [
            "Arrêt des modules. Au revoir.",
            "À la prochaine.",
            "Session terminée."
        ])
        
        self.add_response("IDENTITY", [
            "Je suis un démon numérique symbolique.",
            "Je suis Prometheus, votre assistant."
        ])
        
        self.add_response("STATUS", [
            "Systèmes nominaux.",
            "Fonctionnement optimal.",
            "Tout est vert."
        ])
        
        self.add_response("CAPABILITIES", [
            "Je peux analyser le code et lancer des simulations.",
            "Mes fonctions incluent l'introspection et le jeu."
        ])
        
        self.add_response("GAME_ENTER", [
            "Connexion au royaume...",
            "Entrée dans la Frontière Numérique...",
            "Chargement..."
        ])
        
        self.add_response("GAME_EXIT", [
            "Déconnexion du royaume.",
            "Simulation suspendue.",
            "Retour au terminal."
        ])

    def get_fallback_response(self) -> str:
        return "Je n'ai pas compris."

    def format_game_response(self, topic: str, data: Any) -> str:
        if topic == "move":
            if data['success']:
                msg = f"Déplacement réussi. Nous sommes à {data['location']['name']}."
                if data.get('encounter', {}).get('occurred'):
                    msg += f"\n[ALERTE] Entité hostile ! Un {data['encounter']['entity']['name']} est apparu !"
                return msg
            else:
                return f"Échec du déplacement : {data['message']}"
        elif topic == "scan":
            return f"[SCAN COMPLET]\nCible: {data.get('analysis', 'Inconnu')}\nEntités: {', '.join(data.get('entities', []))}\nObjets: {', '.join(data.get('items', []))}"
        elif topic == "status":
            loc = data['location']['name']
            hp = data['team'][0]['stats']['hp']
            return f"Lieu: {loc} | PV: {hp} | Systèmes: En ligne"
        elif topic == "battle":
            log = "\n".join(data.get("log", []))
            return f"[COMBAT]\n{log}"
            
        return str(data)
