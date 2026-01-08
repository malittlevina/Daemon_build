# dictionary/lexicon_loader.py
"""
Lexicon Loader for Daemon Dictionary Training System

Provides integration between the dictionary training data and the voice/NLU 
subsystems. Supports pronunciation lookup, fuzzy matching, and speech 
synthesis hints.
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

# Path constants relative to this module
DICTIONARY_DIR = os.path.dirname(os.path.abspath(__file__))
LEXICON_PATH = os.path.join(DICTIONARY_DIR, "daemon_lexicon.json")
RULES_PATH = os.path.join(DICTIONARY_DIR, "pronunciation_rules.json")
TRAINING_PATH = os.path.join(DICTIONARY_DIR, "training_phrases.json")


class LexiconLoader:
    """
    Loads and provides access to the daemon dictionary for pronunciation,
    enunciation, and speech recognition training.
    """
    
    def __init__(self):
        self.lexicon = {}
        self.rules = {}
        self.training = {}
        self.word_index = {}  # Flat index for quick lookup
        self._load_all()
        self._build_index()
        print("[LexiconLoader] Dictionary loaded successfully.")

    def _load_all(self):
        """Load all dictionary JSON files."""
        try:
            if os.path.exists(LEXICON_PATH):
                with open(LEXICON_PATH, "r", encoding="utf-8") as f:
                    self.lexicon = json.load(f)
            else:
                print(f"[LexiconLoader] Warning: Lexicon not found at {LEXICON_PATH}")
                
            if os.path.exists(RULES_PATH):
                with open(RULES_PATH, "r", encoding="utf-8") as f:
                    self.rules = json.load(f)
            else:
                print(f"[LexiconLoader] Warning: Rules not found at {RULES_PATH}")
                
            if os.path.exists(TRAINING_PATH):
                with open(TRAINING_PATH, "r", encoding="utf-8") as f:
                    self.training = json.load(f)
            else:
                print(f"[LexiconLoader] Warning: Training phrases not found at {TRAINING_PATH}")
                
        except json.JSONDecodeError as e:
            print(f"[LexiconLoader] Error parsing dictionary files: {e}")

    def _build_index(self):
        """Build a flat word index for fast lookup."""
        if not self.lexicon.get("entries"):
            return
            
        for category, words in self.lexicon["entries"].items():
            for word, data in words.items():
                self.word_index[word.lower()] = {
                    "category": category,
                    **data
                }
                # Also index aliases
                for alias in data.get("aliases", []):
                    self.word_index[alias.lower()] = {
                        "category": category,
                        "alias_of": word,
                        **data
                    }

    def lookup(self, word: str) -> Optional[Dict]:
        """
        Look up a word in the lexicon.
        
        Args:
            word: The word to look up (case-insensitive)
            
        Returns:
            Dictionary with pronunciation data or None if not found
        """
        return self.word_index.get(word.lower())

    def get_ipa(self, word: str) -> Optional[str]:
        """Get IPA pronunciation for a word."""
        entry = self.lookup(word)
        return entry.get("ipa") if entry else None

    def get_phonetic_spelling(self, word: str) -> Optional[str]:
        """Get human-readable phonetic spelling."""
        entry = self.lookup(word)
        return entry.get("phonetic_spelling") if entry else None

    def get_syllables(self, word: str) -> Optional[List[str]]:
        """Get syllable breakdown for a word."""
        entry = self.lookup(word)
        return entry.get("syllables") if entry else None

    def get_stress_pattern(self, word: str) -> Optional[List[int]]:
        """
        Get stress pattern (1=stressed, 0=unstressed).
        
        Returns list matching syllables, e.g., [1, 0] for "daemon" (DAE-mon)
        """
        entry = self.lookup(word)
        return entry.get("stress") if entry else None

    def get_ssml_phoneme(self, word: str) -> Optional[str]:
        """
        Get SSML phoneme tag for speech synthesis.
        
        Returns string like: <phoneme alphabet='ipa' ph='...'>word</phoneme>
        """
        ipa = self.get_ipa(word)
        if ipa:
            return f"<phoneme alphabet='ipa' ph='{ipa}'>{word}</phoneme>"
        return None

    def fuzzy_match(self, input_text: str, threshold: float = 0.75) -> List[Tuple[str, float]]:
        """
        Find words in lexicon that fuzzy-match the input.
        
        Args:
            input_text: Text to match
            threshold: Minimum similarity ratio (0.0 to 1.0)
            
        Returns:
            List of (word, confidence) tuples sorted by confidence
        """
        matches = []
        input_lower = input_text.lower()
        
        for word in self.word_index.keys():
            ratio = SequenceMatcher(None, input_lower, word).ratio()
            if ratio >= threshold:
                matches.append((word, ratio))
                
        return sorted(matches, key=lambda x: x[1], reverse=True)

    def match_ritual(self, spoken_text: str) -> Optional[Tuple[str, float]]:
        """
        Match spoken text to a known ritual phrase.
        
        Args:
            spoken_text: The transcribed speech
            
        Returns:
            Tuple of (ritual_name, confidence) or None
        """
        if not self.training.get("ritual_training"):
            return None
            
        spoken_lower = spoken_text.lower().strip()
        best_match = None
        best_confidence = 0.0
        
        for ritual_name, ritual_data in self.training["ritual_training"].items():
            # Check exact canonical match
            if spoken_lower == ritual_data["canonical"]:
                return (ritual_name, 1.0)
                
            # Check variations
            for variation in ritual_data.get("variations", []):
                if spoken_lower == variation["text"].lower():
                    if variation["confidence"] > best_confidence:
                        best_match = ritual_name
                        best_confidence = variation["confidence"]
                        
            # Check if spoken text contains the canonical phrase
            if ritual_data["canonical"] in spoken_lower:
                confidence = 0.85
                if confidence > best_confidence:
                    best_match = ritual_name
                    best_confidence = confidence
                    
        if best_match:
            return (best_match, best_confidence)
        return None

    def match_scroll(self, spoken_text: str) -> Optional[Tuple[str, float, Optional[str]]]:
        """
        Match spoken text to a known scroll command.
        
        Args:
            spoken_text: The transcribed speech
            
        Returns:
            Tuple of (scroll_name, confidence, extracted_argument) or None
        """
        if not self.training.get("scroll_training"):
            return None
            
        spoken_lower = spoken_text.lower().strip()
        best_match = None
        best_confidence = 0.0
        extracted_arg = None
        
        for scroll_name, scroll_data in self.training["scroll_training"].items():
            canonical = scroll_data["canonical"]
            
            # Check if speech starts with any variation
            for variation in scroll_data.get("variations", []):
                var_text = variation["text"].lower()
                if spoken_lower.startswith(var_text):
                    confidence = variation["confidence"]
                    if confidence > best_confidence:
                        best_match = scroll_name
                        best_confidence = confidence
                        # Extract argument (text after the command)
                        remainder = spoken_lower[len(var_text):].strip()
                        extracted_arg = remainder if remainder else None
                        
            # Also try canonical
            if spoken_lower.startswith(canonical):
                if 0.95 > best_confidence:
                    best_match = scroll_name
                    best_confidence = 0.95
                    remainder = spoken_lower[len(canonical):].strip()
                    extracted_arg = remainder if remainder else None
                    
        if best_match:
            return (best_match, best_confidence, extracted_arg)
        return None

    def get_acceptable_variations(self, word: str) -> List[str]:
        """
        Get acceptable pronunciation variations for speech recognition.
        
        Args:
            word: The canonical word
            
        Returns:
            List of acceptable variations
        """
        variations = self.rules.get("rules", {}).get("recognition_tolerance", {}).get("acceptable_variations", {})
        return variations.get(word.lower(), [word])

    def get_pronunciation_drill(self, drill_type: str = "consonant_clusters") -> List[Dict]:
        """
        Get pronunciation practice drills.
        
        Args:
            drill_type: One of 'consonant_clusters', 'vowel_precision', 'rhythm_exercises'
            
        Returns:
            List of drill dictionaries
        """
        drills = self.training.get("pronunciation_drills", {})
        return drills.get(drill_type, [])

    def get_all_rituals(self) -> List[str]:
        """Get list of all registered ritual phrases."""
        if not self.training.get("ritual_training"):
            return []
        return list(self.training["ritual_training"].keys())

    def get_all_scrolls(self) -> List[str]:
        """Get list of all registered scroll commands."""
        if not self.training.get("scroll_training"):
            return []
        return list(self.training["scroll_training"].keys())

    def get_hotword(self) -> Optional[str]:
        """Get the primary hotword for activation."""
        hotword_data = self.training.get("hotword_training", {})
        return hotword_data.get("primary_hotword")

    def validate_hotword(self, spoken_text: str) -> Tuple[bool, float]:
        """
        Check if spoken text matches the hotword.
        
        Args:
            spoken_text: Transcribed speech
            
        Returns:
            Tuple of (is_match, confidence)
        """
        hotword_data = self.training.get("hotword_training", {})
        if not hotword_data:
            return (False, 0.0)
            
        spoken_lower = spoken_text.lower().strip()
        
        for sample in hotword_data.get("training_samples", []):
            # Check against variations
            for variation in sample.get("variations", []):
                if variation["text"].lower() in spoken_lower:
                    return (True, variation["confidence"])
                    
            # Check context phrases
            for context in sample.get("context_phrases", []):
                if context.lower() in spoken_lower:
                    return (True, 0.9)
                    
        return (False, 0.0)

    def format_for_tts(self, text: str) -> str:
        """
        Format text with SSML hints for text-to-speech.
        
        Args:
            text: Plain text to format
            
        Returns:
            Text with SSML phoneme tags for known words
        """
        words = text.split()
        formatted_words = []
        
        for word in words:
            # Strip punctuation for lookup
            clean_word = re.sub(r'[^\w]', '', word.lower())
            entry = self.lookup(clean_word)
            
            if entry and entry.get("ipa"):
                # Preserve original punctuation
                prefix = ""
                suffix = ""
                if word and not word[0].isalnum():
                    prefix = word[0]
                if word and not word[-1].isalnum():
                    suffix = word[-1]
                    
                ssml = f"<phoneme alphabet='ipa' ph='{entry['ipa']}'>{clean_word}</phoneme>"
                formatted_words.append(f"{prefix}{ssml}{suffix}")
            else:
                formatted_words.append(word)
                
        return " ".join(formatted_words)


# Singleton instance for module-level access
_loader_instance = None

def get_lexicon() -> LexiconLoader:
    """Get the singleton lexicon loader instance."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = LexiconLoader()
    return _loader_instance


# Convenience functions for direct access
def lookup(word: str) -> Optional[Dict]:
    """Look up a word in the lexicon."""
    return get_lexicon().lookup(word)

def get_ipa(word: str) -> Optional[str]:
    """Get IPA pronunciation for a word."""
    return get_lexicon().get_ipa(word)

def get_phonetic(word: str) -> Optional[str]:
    """Get phonetic spelling for a word."""
    return get_lexicon().get_phonetic_spelling(word)

def match_command(spoken_text: str) -> Optional[Tuple[str, str, float]]:
    """
    Match spoken text to a ritual or scroll command.
    
    Returns:
        Tuple of (command_type, command_name, confidence) or None
    """
    lexicon = get_lexicon()
    
    # Try ritual first
    ritual_match = lexicon.match_ritual(spoken_text)
    if ritual_match and ritual_match[1] >= 0.75:
        return ("ritual", ritual_match[0], ritual_match[1])
        
    # Try scroll
    scroll_match = lexicon.match_scroll(spoken_text)
    if scroll_match and scroll_match[1] >= 0.75:
        return ("scroll", scroll_match[0], scroll_match[1])
        
    return None


if __name__ == "__main__":
    # Test the lexicon loader
    print("\n=== Daemon Dictionary Lexicon Loader Test ===\n")
    
    loader = get_lexicon()
    
    # Test word lookup
    print("Testing word lookup:")
    test_words = ["prometheus", "daemon", "codex", "ritual", "invoke"]
    for word in test_words:
        entry = loader.lookup(word)
        if entry:
            print(f"  {word}: {entry.get('phonetic_spelling')} ({entry.get('ipa')})")
        else:
            print(f"  {word}: Not found")
    
    # Test ritual matching
    print("\nTesting ritual matching:")
    test_phrases = ["optimize self", "optimise yourself", "summon knowledge", "call knowledge"]
    for phrase in test_phrases:
        result = loader.match_ritual(phrase)
        if result:
            print(f"  '{phrase}' -> {result[0]} (confidence: {result[1]:.2f})")
        else:
            print(f"  '{phrase}' -> No match")
    
    # Test scroll matching
    print("\nTesting scroll matching:")
    test_scrolls = ["study topic python", "run task backup", "create plan for website"]
    for scroll in test_scrolls:
        result = loader.match_scroll(scroll)
        if result:
            print(f"  '{scroll}' -> {result[0]} (confidence: {result[1]:.2f}, arg: {result[2]})")
        else:
            print(f"  '{scroll}' -> No match")
    
    # Test hotword validation
    print("\nTesting hotword validation:")
    test_hotwords = ["prometheus", "hey prometheus", "pro metheus", "hello world"]
    for hw in test_hotwords:
        is_match, confidence = loader.validate_hotword(hw)
        print(f"  '{hw}' -> Match: {is_match}, Confidence: {confidence:.2f}")
    
    # Test TTS formatting
    print("\nTesting TTS formatting:")
    sample_text = "The daemon invokes the codex ritual"
    formatted = loader.format_for_tts(sample_text)
    print(f"  Original: {sample_text}")
    print(f"  Formatted: {formatted[:100]}...")
    
    print("\n=== Test Complete ===")
