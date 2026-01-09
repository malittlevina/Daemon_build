from .english import EnglishPack
from .mandarin import MandarinPack
from .hindi import HindiPack
from .spanish import SpanishPack
from .french import FrenchPack

class LanguageRegistry:
    def __init__(self):
        self.languages = {
            "en": EnglishPack(),
            "zh": MandarinPack(),
            "hi": HindiPack(),
            "es": SpanishPack(),
            "fr": FrenchPack()
        }
        self.default = self.languages["en"]

    def get_language(self, code: str):
        return self.languages.get(code, self.default)

    def detect_language_switch(self, text: str):
        text = text.lower()
        if "speak english" in text or "switch to english" in text:
            return "en"
        if "speak mandarin" in text or "chinese" in text: # simple heuristic
            return "zh"
        if "speak hindi" in text:
            return "hi"
        if "speak spanish" in text:
            return "es"
        if "speak french" in text:
            return "fr"
        return None
