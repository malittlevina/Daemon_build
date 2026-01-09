import re
import random
from typing import Dict, List, Optional, Any

class LanguagePack:
    def __init__(self, language_code: str, language_name: str):
        self.code = language_code
        self.name = language_name
        self.intents: Dict[str, List[str]] = {} # regex patterns per intent
        self.responses: Dict[str, List[str]] = {} # list of response templates per intent
        self.keywords: Dict[str, Any] = {} # For simpler keyword matching

    def add_intent(self, intent_name: str, patterns: List[str]):
        self.intents[intent_name] = patterns

    def add_response(self, intent_name: str, responses: List[str]):
        self.responses[intent_name] = responses

    def get_intent(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for intent, patterns in self.intents.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        return None

    def get_response(self, intent: str, context: Dict = {}) -> str:
        if intent in self.responses:
            template = random.choice(self.responses[intent])
            return template.format(**context)
        return self.get_fallback_response()

    def get_fallback_response(self) -> str:
        return "..."

    def format_game_response(self, topic: str, data: Any) -> str:
        # Specialized formatting for game events
        return str(data)
