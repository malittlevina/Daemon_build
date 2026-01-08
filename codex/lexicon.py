import json
import os
from typing import Dict, List, Optional

class Lexicon:
    def __init__(self, storage_path="codex/lexicon.json"):
        self.storage_path = storage_path
        # Schema: {word: {"def": "definition", "pos": "noun", "synonyms": []}}
        self.words: Dict[str, Dict] = {}
        self.load()

    def define(self, word: str, definition: str, pos: str = "unknown", synonyms: List[str] = None):
        """
        Adds or updates a definition in the lexicon.
        """
        key = word.lower().strip()
        self.words[key] = {
            "def": definition,
            "pos": pos,
            "synonyms": synonyms or []
        }
        self.save()

    def lookup(self, word: str) -> Optional[Dict]:
        """
        Retrieves the entry for a word.
        """
        key = word.lower().strip()
        return self.words.get(key)

    def search(self, query: str) -> List[str]:
        """
        Fuzzy search for words.
        """
        query = query.lower()
        return [w for w in self.words.keys() if query in w]

    def save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump(self.words, f, indent=2)

    def load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.words = json.load(f)
            except Exception as e:
                print(f"[Lexicon] Failed to load dictionary: {e}")
                self.words = {}
