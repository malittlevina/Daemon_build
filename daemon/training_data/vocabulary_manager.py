import json
import os
from typing import Optional, Dict, List

class VocabularyManager:
    """
    Manages the dictionary of system-specific terms, including their
    pronunciation, IPA, and enunciation guides.
    """
    
    def __init__(self, data_path: str = None):
        if data_path is None:
            # Default to the file in the same directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, "pronunciation_dictionary.json")
            
        self.data_path = data_path
        self.dictionary: Dict[str, Dict] = {}
        self._load_data()

    def _load_data(self):
        """Loads the vocabulary data from the JSON file."""
        if not os.path.exists(self.data_path):
            print(f"Warning: Dictionary file not found at {self.data_path}")
            return

        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Index by term (lowercase for case-insensitive lookup)
                for entry in data.get("entries", []):
                    self.dictionary[entry["term"].lower()] = entry
        except Exception as e:
            print(f"Error loading dictionary data: {e}")

    def get_entry(self, term: str) -> Optional[Dict]:
        """Retrieves the full entry for a given term."""
        return self.dictionary.get(term.lower())

    def get_pronunciation(self, term: str) -> Optional[str]:
        """Returns the phonetic spelling of a term."""
        entry = self.get_entry(term)
        return entry.get("phonetic") if entry else None

    def get_ipa(self, term: str) -> Optional[str]:
        """Returns the IPA pronunciation of a term."""
        entry = self.get_entry(term)
        return entry.get("ipa") if entry else None

    def get_enunciation_guide(self, term: str) -> Optional[str]:
        """Returns the enunciation guide for a term."""
        entry = self.get_entry(term)
        return entry.get("enunciation_guide") if entry else None

    def add_entry(self, term: str, phonetic: str, ipa: str = "", category: str = "General", enunciation: str = ""):
        """Adds a new entry to the in-memory dictionary and saves to disk."""
        entry = {
            "term": term,
            "phonetic": phonetic,
            "ipa": ipa,
            "stress_pattern": "", # Optional
            "category": category,
            "enunciation_guide": enunciation,
            "usage_context": ""
        }
        self.dictionary[term.lower()] = entry
        self._save_data()

    def _save_data(self):
        """Saves the current dictionary back to the JSON file."""
        # Reconstruct the full JSON structure
        output_data = {
            "meta": {
                "version": "1.0", 
                "description": "Training dataset for daemon voice synthesis and recognition, focusing on pronunciation and enunciation of system-specific terminology."
            },
            "entries": list(self.dictionary.values())
        }
        
        try:
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
        except Exception as e:
            print(f"Error saving dictionary data: {e}")

    def list_terms(self) -> List[str]:
        """Returns a list of all terms in the dictionary."""
        return [entry["term"] for entry in self.dictionary.values()]
