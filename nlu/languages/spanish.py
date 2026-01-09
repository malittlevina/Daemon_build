from typing import Any
from .base import LanguagePack

class SpanishPack(LanguagePack):
    def __init__(self):
        super().__init__("es", "Spanish")
        
        # --- Intents (Ordered by Priority) ---
        self.add_intent("GAME_ENTER", [r"entrar al juego", r"jugar", r"iniciar"])
        self.add_intent("GAME_EXIT", [r"salir del juego", r"terminar juego", r"parar juego"])
        self.add_intent("GREETING", [r"\bhola\b", r"\bbuenos d.as\b", r"\bsaludos\b"])
        self.add_intent("FAREWELL", [r"\badi.s\b", r"\bhasta luego\b", r"\bchao\b", r"\bsalir\b"])
        self.add_intent("IDENTITY", [r"qui.n eres", r"identif.cate", r"que eres"])
        self.add_intent("STATUS", [r"c.mo est.s", r"estado", r"reporte"])
        self.add_intent("CAPABILITIES", [r"qu. puedes hacer", r"ayuda", r"capacidades"])
        
        # --- Responses ---
        self.add_response("GREETING", [
            "Hola. El sistema está en línea.",
            "Saludos, usuario. Soy Prometheus.",
            "A la orden."
        ])
        
        self.add_response("FAREWELL", [
            "Apagando módulos. Adiós.",
            "Hasta la próxima.",
            "Sesión terminada."
        ])
        
        self.add_response("IDENTITY", [
            "Soy un demonio digital simbólico.",
            "Soy Prometheus, tu asistente de código."
        ])
        
        self.add_response("STATUS", [
            "Sistemas nominales.",
            "Operando a capacidad óptima.",
            "Todo correcto."
        ])
        
        self.add_response("CAPABILITIES", [
            "Puedo analizar código y ejecutar simulaciones.",
            "Mis funciones incluyen introspección y juegos."
        ])
        
        self.add_response("GAME_ENTER", [
            "Iniciando conexión al reino...",
            "Entrando a la Frontera Digital...",
            "Cargando..."
        ])
        
        self.add_response("GAME_EXIT", [
            "Desconectando del reino.",
            "Simulación suspendida.",
            "Regresando al terminal."
        ])

    def get_fallback_response(self) -> str:
        return "No entendí ese comando."

    def format_game_response(self, topic: str, data: Any) -> str:
        if topic == "move":
            if data['success']:
                msg = f"Movimiento exitoso. Estamos en {data['location']['name']}."
                if data.get('encounter', {}).get('occurred'):
                    msg += f"\n[ALERTA] ¡Enemigo detectado! ¡Un {data['encounter']['entity']['name']} apareció!"
                return msg
            else:
                return f"No se pudo mover: {data['message']}"
        elif topic == "scan":
            return f"[ESCANEO COMPLETO]\nObjetivo: {data.get('analysis', 'Desconocido')}\nEntidades: {', '.join(data.get('entities', []))}\nItems: {', '.join(data.get('items', []))}"
        elif topic == "status":
            loc = data['location']['name']
            hp = data['team'][0]['stats']['hp']
            return f"Ubicación: {loc} | HP Líder: {hp} | Sistemas: En línea"
        elif topic == "battle":
            log = "\n".join(data.get("log", []))
            return f"[BATALLA]\n{log}"
            
        return str(data)
