# language/vocabulary.py
"""
Vocabulary System
=================
Manages the daemon's word knowledge including:
- Definitions and meanings
- Word relationships (synonyms, antonyms, hypernyms)
- Part of speech classification
- Word frequency and importance
- Domain-specific vocabularies
"""

import os
import json
import time
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Any, Tuple


class PartOfSpeech(Enum):
    """Parts of speech classification."""
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PRONOUN = "pronoun"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    DETERMINER = "determiner"
    AUXILIARY = "auxiliary"
    UNKNOWN = "unknown"


class WordRelation(Enum):
    """Types of word relationships."""
    SYNONYM = "synonym"          # Similar meaning
    ANTONYM = "antonym"          # Opposite meaning
    HYPERNYM = "hypernym"        # More general (dog -> animal)
    HYPONYM = "hyponym"          # More specific (animal -> dog)
    MERONYM = "meronym"          # Part of (wheel -> car)
    HOLONYM = "holonym"          # Whole of (car -> wheel)
    RELATED = "related"          # Generally related
    DERIVED = "derived"          # Derived from (run -> running)


@dataclass
class WordSense:
    """A specific meaning/sense of a word."""
    sense_id: str
    definition: str
    pos: PartOfSpeech
    examples: List[str] = field(default_factory=list)
    domain: Optional[str] = None  # e.g., "technology", "medicine"
    register: str = "neutral"     # formal, informal, neutral, slang
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['pos'] = self.pos.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WordSense':
        data['pos'] = PartOfSpeech(data['pos'])
        return cls(**data)


@dataclass
class Word:
    """A word in the vocabulary with all its properties."""
    word: str
    senses: List[WordSense] = field(default_factory=list)
    
    # Relationships to other words
    relations: Dict[str, List[str]] = field(default_factory=dict)  # relation_type -> [words]
    
    # Usage statistics
    frequency: int = 0           # How often encountered
    importance: float = 0.5      # 0-1, how important to know
    familiarity: float = 0.0     # 0-1, how well the daemon knows it
    
    # Learning
    times_used: int = 0
    times_looked_up: int = 0
    first_seen: Optional[float] = None
    last_seen: Optional[float] = None
    
    # Metadata
    etymology: Optional[str] = None
    pronunciation: Optional[str] = None
    syllables: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.first_seen is None:
            self.first_seen = time.time()
    
    @property
    def primary_pos(self) -> PartOfSpeech:
        """Get the primary part of speech."""
        if self.senses:
            return self.senses[0].pos
        return PartOfSpeech.UNKNOWN
    
    @property
    def primary_definition(self) -> str:
        """Get the primary definition."""
        if self.senses:
            return self.senses[0].definition
        return ""
    
    def add_sense(self, definition: str, pos: PartOfSpeech, examples: List[str] = None, domain: str = None):
        """Add a new sense/meaning."""
        sense_id = f"{self.word}_{len(self.senses) + 1}"
        sense = WordSense(
            sense_id=sense_id,
            definition=definition,
            pos=pos,
            examples=examples or [],
            domain=domain
        )
        self.senses.append(sense)
    
    def add_relation(self, relation: WordRelation, related_word: str):
        """Add a relationship to another word."""
        rel_key = relation.value
        if rel_key not in self.relations:
            self.relations[rel_key] = []
        if related_word not in self.relations[rel_key]:
            self.relations[rel_key].append(related_word)
    
    def get_related(self, relation: WordRelation) -> List[str]:
        """Get words with a specific relationship."""
        return self.relations.get(relation.value, [])
    
    def synonyms(self) -> List[str]:
        """Get synonyms."""
        return self.get_related(WordRelation.SYNONYM)
    
    def antonyms(self) -> List[str]:
        """Get antonyms."""
        return self.get_related(WordRelation.ANTONYM)
    
    def mark_seen(self):
        """Mark the word as encountered."""
        self.frequency += 1
        self.last_seen = time.time()
        # Familiarity increases with exposure
        self.familiarity = min(1.0, self.familiarity + 0.01)
    
    def mark_used(self):
        """Mark the word as used in output."""
        self.times_used += 1
        self.familiarity = min(1.0, self.familiarity + 0.02)
    
    def mark_looked_up(self):
        """Mark the word as looked up."""
        self.times_looked_up += 1
        self.familiarity = min(1.0, self.familiarity + 0.05)
    
    def to_dict(self) -> dict:
        return {
            'word': self.word,
            'senses': [s.to_dict() for s in self.senses],
            'relations': self.relations,
            'frequency': self.frequency,
            'importance': self.importance,
            'familiarity': self.familiarity,
            'times_used': self.times_used,
            'times_looked_up': self.times_looked_up,
            'first_seen': self.first_seen,
            'last_seen': self.last_seen,
            'etymology': self.etymology,
            'pronunciation': self.pronunciation,
            'syllables': self.syllables
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Word':
        senses = [WordSense.from_dict(s) for s in data.pop('senses', [])]
        word = cls(word=data.pop('word'), senses=senses)
        for key, value in data.items():
            if hasattr(word, key):
                setattr(word, key, value)
        return word
    
    def describe(self) -> str:
        """Get a human-readable description."""
        lines = [f"📖 {self.word}"]
        
        for i, sense in enumerate(self.senses, 1):
            lines.append(f"  {i}. ({sense.pos.value}) {sense.definition}")
            if sense.examples:
                lines.append(f"     Example: \"{sense.examples[0]}\"")
        
        if self.synonyms():
            lines.append(f"  Synonyms: {', '.join(self.synonyms()[:5])}")
        
        return "\n".join(lines)


class Vocabulary:
    """
    The daemon's vocabulary - its knowledge of words.
    Integrates with the cognition pipeline for NLU.
    """
    
    def __init__(self, vocab_path: str = "language/data/vocabulary.json"):
        self.vocab_path = vocab_path
        self.words: Dict[str, Word] = {}
        
        # Indexes for fast lookup
        self._by_pos: Dict[PartOfSpeech, Set[str]] = {pos: set() for pos in PartOfSpeech}
        self._by_domain: Dict[str, Set[str]] = {}
        
        # Statistics
        self.total_lookups = 0
        self.unknown_words: List[str] = []
        
        self._load()
        self._build_core_vocabulary()
        
        print(f"[Vocabulary] Loaded {len(self.words)} words.")
    
    def _load(self):
        """Load vocabulary from disk."""
        if os.path.exists(self.vocab_path):
            try:
                with open(self.vocab_path, 'r') as f:
                    data = json.load(f)
                    for word_data in data.get('words', []):
                        word = Word.from_dict(word_data)
                        self.words[word.word.lower()] = word
                        self._index_word(word)
            except Exception as e:
                print(f"[Vocabulary] Load error: {e}")
    
    def _save(self):
        """Save vocabulary to disk."""
        try:
            os.makedirs(os.path.dirname(self.vocab_path), exist_ok=True)
            with open(self.vocab_path, 'w') as f:
                data = {
                    'words': [w.to_dict() for w in self.words.values()],
                    'total_words': len(self.words),
                    'last_saved': time.time()
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Vocabulary] Save error: {e}")
    
    def _index_word(self, word: Word):
        """Index a word for fast lookup."""
        for sense in word.senses:
            self._by_pos[sense.pos].add(word.word)
            if sense.domain:
                if sense.domain not in self._by_domain:
                    self._by_domain[sense.domain] = set()
                self._by_domain[sense.domain].add(word.word)
    
    def _build_core_vocabulary(self):
        """Build core vocabulary if not already present."""
        if len(self.words) > 100:
            return
        
        # Core words the daemon should know
        core_words = [
            ("help", PartOfSpeech.VERB, "To assist or aid someone"),
            ("remember", PartOfSpeech.VERB, "To recall from memory"),
            ("learn", PartOfSpeech.VERB, "To acquire knowledge or skill"),
            ("think", PartOfSpeech.VERB, "To use the mind to consider"),
            ("understand", PartOfSpeech.VERB, "To comprehend the meaning"),
            ("observe", PartOfSpeech.VERB, "To watch carefully"),
            ("task", PartOfSpeech.NOUN, "A piece of work to be done"),
            ("memory", PartOfSpeech.NOUN, "The faculty of remembering"),
            ("knowledge", PartOfSpeech.NOUN, "Information and understanding"),
            ("insight", PartOfSpeech.NOUN, "A deep understanding"),
            ("important", PartOfSpeech.ADJECTIVE, "Of great significance"),
            ("curious", PartOfSpeech.ADJECTIVE, "Eager to learn or know"),
            ("helpful", PartOfSpeech.ADJECTIVE, "Giving or ready to give help"),
        ]
        
        for word_text, pos, definition in core_words:
            if word_text.lower() not in self.words:
                word = Word(word=word_text)
                word.add_sense(definition, pos)
                word.importance = 0.8
                self.add_word(word)
    
    def add_word(self, word: Word):
        """Add a word to the vocabulary."""
        self.words[word.word.lower()] = word
        self._index_word(word)
    
    def get(self, word: str) -> Optional[Word]:
        """Look up a word."""
        word_lower = word.lower()
        if word_lower in self.words:
            w = self.words[word_lower]
            w.mark_seen()
            self.total_lookups += 1
            return w
        return None
    
    def lookup(self, word: str) -> Optional[Word]:
        """Look up a word (marks as looked up)."""
        word_lower = word.lower()
        if word_lower in self.words:
            w = self.words[word_lower]
            w.mark_looked_up()
            self.total_lookups += 1
            return w
        
        # Track unknown words
        if word_lower not in self.unknown_words:
            self.unknown_words.append(word_lower)
            if len(self.unknown_words) > 100:
                self.unknown_words = self.unknown_words[-100:]
        
        return None
    
    def define(self, word: str) -> str:
        """Get a definition of a word."""
        w = self.lookup(word)
        if w:
            return w.describe()
        return f"Unknown word: {word}"
    
    def has_word(self, word: str) -> bool:
        """Check if a word is in vocabulary."""
        return word.lower() in self.words
    
    def get_synonyms(self, word: str) -> List[str]:
        """Get synonyms of a word."""
        w = self.get(word)
        return w.synonyms() if w else []
    
    def get_antonyms(self, word: str) -> List[str]:
        """Get antonyms of a word."""
        w = self.get(word)
        return w.antonyms() if w else []
    
    def get_by_pos(self, pos: PartOfSpeech) -> List[str]:
        """Get all words of a specific part of speech."""
        return list(self._by_pos.get(pos, set()))
    
    def get_by_domain(self, domain: str) -> List[str]:
        """Get all words in a specific domain."""
        return list(self._by_domain.get(domain, set()))
    
    def learn_word(
        self,
        word: str,
        definition: str,
        pos: PartOfSpeech = PartOfSpeech.UNKNOWN,
        examples: List[str] = None,
        synonyms: List[str] = None,
        antonyms: List[str] = None
    ) -> Word:
        """Learn a new word or update existing."""
        word_lower = word.lower()
        
        if word_lower in self.words:
            w = self.words[word_lower]
            # Add new sense if different
            if not any(s.definition == definition for s in w.senses):
                w.add_sense(definition, pos, examples)
        else:
            w = Word(word=word)
            w.add_sense(definition, pos, examples)
            self.add_word(w)
        
        # Add relationships
        if synonyms:
            for syn in synonyms:
                w.add_relation(WordRelation.SYNONYM, syn)
        
        if antonyms:
            for ant in antonyms:
                w.add_relation(WordRelation.ANTONYM, ant)
        
        self._save()
        print(f"[Vocabulary] Learned: {word}")
        return w
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text for vocabulary insights."""
        words = text.lower().split()
        
        known = []
        unknown = []
        pos_counts = {pos: 0 for pos in PartOfSpeech}
        
        for word in words:
            # Clean word
            clean_word = ''.join(c for c in word if c.isalnum())
            if not clean_word:
                continue
            
            w = self.get(clean_word)
            if w:
                known.append(clean_word)
                pos_counts[w.primary_pos] += 1
            else:
                unknown.append(clean_word)
        
        return {
            'total_words': len(words),
            'known_words': len(known),
            'unknown_words': len(unknown),
            'unknown_list': list(set(unknown)),
            'vocabulary_coverage': len(known) / len(words) if words else 0,
            'pos_distribution': {k.value: v for k, v in pos_counts.items() if v > 0}
        }
    
    def suggest_words_to_learn(self, limit: int = 10) -> List[str]:
        """Suggest unknown words that should be learned."""
        # Sort by frequency of encounters
        from collections import Counter
        counts = Counter(self.unknown_words)
        return [word for word, _ in counts.most_common(limit)]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vocabulary statistics."""
        return {
            'total_words': len(self.words),
            'by_pos': {pos.value: len(words) for pos, words in self._by_pos.items() if words},
            'by_domain': {dom: len(words) for dom, words in self._by_domain.items()},
            'total_lookups': self.total_lookups,
            'unknown_words_count': len(self.unknown_words)
        }
    
    def save(self):
        """Save vocabulary."""
        self._save()
