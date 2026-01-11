# unimind/models/native/vocabulary.py
# Comprehensive English Vocabulary System for NLU Enhancement

"""
English Vocabulary System

Fluency levels by vocabulary size:
- A1 (Beginner): 500-1,000 words
- A2 (Elementary): 1,000-2,000 words  
- B1 (Intermediate): 2,000-4,000 words
- B2 (Upper Intermediate): 4,000-8,000 words
- C1 (Advanced): 8,000-16,000 words
- C2 (Mastery): 16,000+ words

This module provides:
- Core vocabulary with definitions
- Word relationships (synonyms, antonyms)
- Part-of-speech tagging
- Word frequency rankings
- Semantic categories
"""

from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import re


class PartOfSpeech(Enum):
    """Parts of speech."""
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


class WordFrequency(Enum):
    """Word frequency tiers."""
    CORE_100 = 1      # Most common 100 words
    CORE_500 = 2      # Top 500
    CORE_1000 = 3     # Top 1000
    COMMON = 4        # Top 3000
    INTERMEDIATE = 5  # Top 8000
    ADVANCED = 6      # Top 20000
    RARE = 7          # Beyond 20000


@dataclass
class WordEntry:
    """Entry for a vocabulary word."""
    word: str
    pos: List[PartOfSpeech]
    definitions: List[str]
    frequency: WordFrequency
    synonyms: List[str] = field(default_factory=list)
    antonyms: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    category: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "word": self.word,
            "pos": [p.value for p in self.pos],
            "definitions": self.definitions,
            "frequency": self.frequency.value,
            "synonyms": self.synonyms,
            "antonyms": self.antonyms
        }


# =============================================================================
# CORE 100 WORDS (Most frequent English words)
# =============================================================================

CORE_100_WORDS = {
    # Pronouns
    "i": WordEntry("i", [PartOfSpeech.PRONOUN], ["First person singular pronoun"], WordFrequency.CORE_100),
    "you": WordEntry("you", [PartOfSpeech.PRONOUN], ["Second person pronoun"], WordFrequency.CORE_100),
    "he": WordEntry("he", [PartOfSpeech.PRONOUN], ["Third person masculine pronoun"], WordFrequency.CORE_100),
    "she": WordEntry("she", [PartOfSpeech.PRONOUN], ["Third person feminine pronoun"], WordFrequency.CORE_100),
    "it": WordEntry("it", [PartOfSpeech.PRONOUN], ["Third person neuter pronoun"], WordFrequency.CORE_100),
    "we": WordEntry("we", [PartOfSpeech.PRONOUN], ["First person plural pronoun"], WordFrequency.CORE_100),
    "they": WordEntry("they", [PartOfSpeech.PRONOUN], ["Third person plural pronoun"], WordFrequency.CORE_100),
    "this": WordEntry("this", [PartOfSpeech.PRONOUN, PartOfSpeech.DETERMINER], ["Indicating something near"], WordFrequency.CORE_100),
    "that": WordEntry("that", [PartOfSpeech.PRONOUN, PartOfSpeech.DETERMINER, PartOfSpeech.CONJUNCTION], ["Indicating something far"], WordFrequency.CORE_100),
    "what": WordEntry("what", [PartOfSpeech.PRONOUN], ["Asking about something"], WordFrequency.CORE_100),
    
    # Verbs
    "be": WordEntry("be", [PartOfSpeech.VERB], ["To exist, to have identity"], WordFrequency.CORE_100, synonyms=["exist"]),
    "have": WordEntry("have", [PartOfSpeech.VERB], ["To possess, to own"], WordFrequency.CORE_100, synonyms=["possess", "own"]),
    "do": WordEntry("do", [PartOfSpeech.VERB], ["To perform, to execute"], WordFrequency.CORE_100, synonyms=["perform", "execute"]),
    "say": WordEntry("say", [PartOfSpeech.VERB], ["To speak, to express"], WordFrequency.CORE_100, synonyms=["speak", "tell", "express"]),
    "get": WordEntry("get", [PartOfSpeech.VERB], ["To obtain, to receive"], WordFrequency.CORE_100, synonyms=["obtain", "receive", "acquire"]),
    "make": WordEntry("make", [PartOfSpeech.VERB], ["To create, to produce"], WordFrequency.CORE_100, synonyms=["create", "produce", "build"]),
    "go": WordEntry("go", [PartOfSpeech.VERB], ["To move, to travel"], WordFrequency.CORE_100, synonyms=["move", "travel", "proceed"], antonyms=["stop", "stay"]),
    "know": WordEntry("know", [PartOfSpeech.VERB], ["To understand, to be aware"], WordFrequency.CORE_100, synonyms=["understand", "comprehend"]),
    "take": WordEntry("take", [PartOfSpeech.VERB], ["To grab, to accept"], WordFrequency.CORE_100, synonyms=["grab", "accept", "receive"], antonyms=["give"]),
    "see": WordEntry("see", [PartOfSpeech.VERB], ["To perceive with eyes"], WordFrequency.CORE_100, synonyms=["observe", "view", "watch"]),
    "come": WordEntry("come", [PartOfSpeech.VERB], ["To move toward"], WordFrequency.CORE_100, synonyms=["arrive", "approach"], antonyms=["go", "leave"]),
    "think": WordEntry("think", [PartOfSpeech.VERB], ["To use mind, to believe"], WordFrequency.CORE_100, synonyms=["believe", "consider", "ponder"]),
    "look": WordEntry("look", [PartOfSpeech.VERB], ["To direct eyes at"], WordFrequency.CORE_100, synonyms=["see", "watch", "observe"]),
    "want": WordEntry("want", [PartOfSpeech.VERB], ["To desire, to wish for"], WordFrequency.CORE_100, synonyms=["desire", "wish", "need"]),
    "give": WordEntry("give", [PartOfSpeech.VERB], ["To transfer, to provide"], WordFrequency.CORE_100, synonyms=["provide", "offer"], antonyms=["take", "receive"]),
    "use": WordEntry("use", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["To employ, to utilize"], WordFrequency.CORE_100, synonyms=["employ", "utilize", "apply"]),
    "find": WordEntry("find", [PartOfSpeech.VERB], ["To discover, to locate"], WordFrequency.CORE_100, synonyms=["discover", "locate"], antonyms=["lose"]),
    "tell": WordEntry("tell", [PartOfSpeech.VERB], ["To communicate, to inform"], WordFrequency.CORE_100, synonyms=["inform", "notify", "say"]),
    "ask": WordEntry("ask", [PartOfSpeech.VERB], ["To inquire, to request"], WordFrequency.CORE_100, synonyms=["inquire", "question", "request"], antonyms=["answer"]),
    "work": WordEntry("work", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["To labor, to function"], WordFrequency.CORE_100, synonyms=["labor", "function", "operate"]),
    "seem": WordEntry("seem", [PartOfSpeech.VERB], ["To appear, to look like"], WordFrequency.CORE_100, synonyms=["appear", "look"]),
    "feel": WordEntry("feel", [PartOfSpeech.VERB], ["To sense, to experience emotion"], WordFrequency.CORE_100, synonyms=["sense", "experience"]),
    "try": WordEntry("try", [PartOfSpeech.VERB], ["To attempt, to endeavor"], WordFrequency.CORE_100, synonyms=["attempt", "endeavor"]),
    "leave": WordEntry("leave", [PartOfSpeech.VERB], ["To depart, to go away"], WordFrequency.CORE_100, synonyms=["depart", "exit"], antonyms=["arrive", "stay"]),
    "call": WordEntry("call", [PartOfSpeech.VERB, PartOfSpeech.NOUN], ["To summon, to name"], WordFrequency.CORE_100, synonyms=["summon", "name", "phone"]),
    
    # Common nouns
    "time": WordEntry("time", [PartOfSpeech.NOUN], ["Duration, period, moment"], WordFrequency.CORE_100, category="abstract"),
    "year": WordEntry("year", [PartOfSpeech.NOUN], ["Period of 365 days"], WordFrequency.CORE_100, category="time"),
    "people": WordEntry("people", [PartOfSpeech.NOUN], ["Humans, persons"], WordFrequency.CORE_100, synonyms=["persons", "humans"], category="people"),
    "way": WordEntry("way", [PartOfSpeech.NOUN], ["Method, path, manner"], WordFrequency.CORE_100, synonyms=["method", "path", "manner"]),
    "day": WordEntry("day", [PartOfSpeech.NOUN], ["24-hour period"], WordFrequency.CORE_100, category="time"),
    "man": WordEntry("man", [PartOfSpeech.NOUN], ["Adult male human"], WordFrequency.CORE_100, category="people"),
    "thing": WordEntry("thing", [PartOfSpeech.NOUN], ["Object, item"], WordFrequency.CORE_100, synonyms=["object", "item"]),
    "woman": WordEntry("woman", [PartOfSpeech.NOUN], ["Adult female human"], WordFrequency.CORE_100, category="people"),
    "life": WordEntry("life", [PartOfSpeech.NOUN], ["Existence, living"], WordFrequency.CORE_100, synonyms=["existence"], antonyms=["death"], category="abstract"),
    "child": WordEntry("child", [PartOfSpeech.NOUN], ["Young human"], WordFrequency.CORE_100, synonyms=["kid", "youth"], category="people"),
    "world": WordEntry("world", [PartOfSpeech.NOUN], ["Earth, globe, society"], WordFrequency.CORE_100, synonyms=["earth", "globe"], category="place"),
    "hand": WordEntry("hand", [PartOfSpeech.NOUN], ["Body part for grasping"], WordFrequency.CORE_100, category="body"),
    "part": WordEntry("part", [PartOfSpeech.NOUN], ["Piece, portion"], WordFrequency.CORE_100, synonyms=["piece", "portion", "section"]),
    "place": WordEntry("place", [PartOfSpeech.NOUN], ["Location, area"], WordFrequency.CORE_100, synonyms=["location", "area", "spot"], category="place"),
    "case": WordEntry("case", [PartOfSpeech.NOUN], ["Instance, situation"], WordFrequency.CORE_100, synonyms=["instance", "situation"]),
    "week": WordEntry("week", [PartOfSpeech.NOUN], ["Seven-day period"], WordFrequency.CORE_100, category="time"),
    "company": WordEntry("company", [PartOfSpeech.NOUN], ["Business, firm"], WordFrequency.CORE_100, synonyms=["business", "firm"], category="business"),
    "system": WordEntry("system", [PartOfSpeech.NOUN], ["Organized structure"], WordFrequency.CORE_100, synonyms=["structure", "framework"]),
    "program": WordEntry("program", [PartOfSpeech.NOUN], ["Plan, software"], WordFrequency.CORE_100, synonyms=["plan", "software"]),
    "question": WordEntry("question", [PartOfSpeech.NOUN, PartOfSpeech.VERB], ["Inquiry, query"], WordFrequency.CORE_100, synonyms=["inquiry", "query"], antonyms=["answer"]),
    
    # Adjectives
    "good": WordEntry("good", [PartOfSpeech.ADJECTIVE], ["Positive quality"], WordFrequency.CORE_100, synonyms=["great", "excellent", "fine"], antonyms=["bad"]),
    "new": WordEntry("new", [PartOfSpeech.ADJECTIVE], ["Recently made/discovered"], WordFrequency.CORE_100, synonyms=["fresh", "recent"], antonyms=["old"]),
    "first": WordEntry("first", [PartOfSpeech.ADJECTIVE, PartOfSpeech.ADVERB], ["Before all others"], WordFrequency.CORE_100, antonyms=["last"]),
    "last": WordEntry("last", [PartOfSpeech.ADJECTIVE, PartOfSpeech.ADVERB], ["Final, most recent"], WordFrequency.CORE_100, antonyms=["first"]),
    "long": WordEntry("long", [PartOfSpeech.ADJECTIVE], ["Extended in length/time"], WordFrequency.CORE_100, antonyms=["short"]),
    "great": WordEntry("great", [PartOfSpeech.ADJECTIVE], ["Large, excellent"], WordFrequency.CORE_100, synonyms=["excellent", "wonderful"], antonyms=["terrible"]),
    "little": WordEntry("little", [PartOfSpeech.ADJECTIVE], ["Small in size"], WordFrequency.CORE_100, synonyms=["small", "tiny"], antonyms=["big", "large"]),
    "own": WordEntry("own", [PartOfSpeech.ADJECTIVE, PartOfSpeech.VERB], ["Belonging to oneself"], WordFrequency.CORE_100, synonyms=["possess"]),
    "other": WordEntry("other", [PartOfSpeech.ADJECTIVE], ["Different, additional"], WordFrequency.CORE_100, synonyms=["different", "another"]),
    "old": WordEntry("old", [PartOfSpeech.ADJECTIVE], ["Existing for long time"], WordFrequency.CORE_100, synonyms=["aged", "ancient"], antonyms=["new", "young"]),
    "right": WordEntry("right", [PartOfSpeech.ADJECTIVE, PartOfSpeech.NOUN], ["Correct, opposite of left"], WordFrequency.CORE_100, synonyms=["correct"], antonyms=["wrong", "left"]),
    "big": WordEntry("big", [PartOfSpeech.ADJECTIVE], ["Large in size"], WordFrequency.CORE_100, synonyms=["large", "huge"], antonyms=["small", "little"]),
    "high": WordEntry("high", [PartOfSpeech.ADJECTIVE], ["Tall, elevated"], WordFrequency.CORE_100, synonyms=["tall", "elevated"], antonyms=["low"]),
    "different": WordEntry("different", [PartOfSpeech.ADJECTIVE], ["Not the same"], WordFrequency.CORE_100, synonyms=["distinct", "various"], antonyms=["same"]),
    "small": WordEntry("small", [PartOfSpeech.ADJECTIVE], ["Little in size"], WordFrequency.CORE_100, synonyms=["little", "tiny"], antonyms=["big", "large"]),
    "large": WordEntry("large", [PartOfSpeech.ADJECTIVE], ["Big in size"], WordFrequency.CORE_100, synonyms=["big", "huge"], antonyms=["small"]),
    "important": WordEntry("important", [PartOfSpeech.ADJECTIVE], ["Significant, valuable"], WordFrequency.CORE_100, synonyms=["significant", "crucial"], antonyms=["unimportant"]),
    
    # Prepositions/Conjunctions
    "in": WordEntry("in", [PartOfSpeech.PREPOSITION], ["Inside, within"], WordFrequency.CORE_100, antonyms=["out"]),
    "to": WordEntry("to", [PartOfSpeech.PREPOSITION], ["Direction toward"], WordFrequency.CORE_100, antonyms=["from"]),
    "for": WordEntry("for", [PartOfSpeech.PREPOSITION], ["In favor of, duration"], WordFrequency.CORE_100),
    "on": WordEntry("on", [PartOfSpeech.PREPOSITION], ["On surface of"], WordFrequency.CORE_100, antonyms=["off"]),
    "with": WordEntry("with", [PartOfSpeech.PREPOSITION], ["Accompanied by"], WordFrequency.CORE_100, antonyms=["without"]),
    "at": WordEntry("at", [PartOfSpeech.PREPOSITION], ["Location, time point"], WordFrequency.CORE_100),
    "by": WordEntry("by", [PartOfSpeech.PREPOSITION], ["Near, through means of"], WordFrequency.CORE_100),
    "from": WordEntry("from", [PartOfSpeech.PREPOSITION], ["Origin point"], WordFrequency.CORE_100, antonyms=["to"]),
    "or": WordEntry("or", [PartOfSpeech.CONJUNCTION], ["Alternative"], WordFrequency.CORE_100, antonyms=["and"]),
    "and": WordEntry("and", [PartOfSpeech.CONJUNCTION], ["Addition, connection"], WordFrequency.CORE_100),
    "but": WordEntry("but", [PartOfSpeech.CONJUNCTION], ["Contrast, exception"], WordFrequency.CORE_100, synonyms=["however"]),
    "if": WordEntry("if", [PartOfSpeech.CONJUNCTION], ["Condition"], WordFrequency.CORE_100),
    "about": WordEntry("about", [PartOfSpeech.PREPOSITION], ["Concerning, approximately"], WordFrequency.CORE_100, synonyms=["regarding", "concerning"]),
    
    # Adverbs
    "not": WordEntry("not", [PartOfSpeech.ADVERB], ["Negation"], WordFrequency.CORE_100),
    "just": WordEntry("just", [PartOfSpeech.ADVERB], ["Only, exactly, recently"], WordFrequency.CORE_100, synonyms=["only", "merely"]),
    "now": WordEntry("now", [PartOfSpeech.ADVERB], ["At present time"], WordFrequency.CORE_100, synonyms=["currently", "presently"], antonyms=["then"]),
    "also": WordEntry("also", [PartOfSpeech.ADVERB], ["In addition"], WordFrequency.CORE_100, synonyms=["too", "additionally"]),
    "only": WordEntry("only", [PartOfSpeech.ADVERB], ["Solely, exclusively"], WordFrequency.CORE_100, synonyms=["just", "merely"]),
    "then": WordEntry("then", [PartOfSpeech.ADVERB], ["At that time, next"], WordFrequency.CORE_100, antonyms=["now"]),
    "more": WordEntry("more", [PartOfSpeech.ADVERB, PartOfSpeech.ADJECTIVE], ["Greater amount"], WordFrequency.CORE_100, antonyms=["less"]),
    "very": WordEntry("very", [PartOfSpeech.ADVERB], ["Extremely, highly"], WordFrequency.CORE_100, synonyms=["extremely", "highly"]),
    "well": WordEntry("well", [PartOfSpeech.ADVERB], ["In good manner"], WordFrequency.CORE_100, synonyms=["properly"], antonyms=["badly"]),
    "here": WordEntry("here", [PartOfSpeech.ADVERB], ["In this place"], WordFrequency.CORE_100, antonyms=["there"]),
    "there": WordEntry("there", [PartOfSpeech.ADVERB], ["In that place"], WordFrequency.CORE_100, antonyms=["here"]),
    "when": WordEntry("when", [PartOfSpeech.ADVERB, PartOfSpeech.CONJUNCTION], ["At what time"], WordFrequency.CORE_100),
    "how": WordEntry("how", [PartOfSpeech.ADVERB], ["In what manner"], WordFrequency.CORE_100),
    "why": WordEntry("why", [PartOfSpeech.ADVERB], ["For what reason"], WordFrequency.CORE_100),
    "where": WordEntry("where", [PartOfSpeech.ADVERB], ["At what place"], WordFrequency.CORE_100),
}


# =============================================================================
# SEMANTIC CATEGORIES - Words grouped by meaning
# =============================================================================

SEMANTIC_CATEGORIES = {
    "emotions_positive": [
        "happy", "joy", "excited", "love", "grateful", "hopeful", "proud", "confident",
        "peaceful", "content", "pleased", "delighted", "enthusiastic", "optimistic",
        "cheerful", "thrilled", "elated", "blissful", "wonderful", "amazing"
    ],
    "emotions_negative": [
        "sad", "angry", "afraid", "worried", "anxious", "frustrated", "disappointed",
        "lonely", "stressed", "upset", "confused", "nervous", "scared", "depressed",
        "annoyed", "irritated", "jealous", "guilty", "ashamed", "embarrassed"
    ],
    "thinking": [
        "think", "believe", "understand", "know", "learn", "remember", "forget",
        "analyze", "consider", "reason", "imagine", "wonder", "realize", "recognize",
        "comprehend", "perceive", "reflect", "ponder", "conclude", "deduce"
    ],
    "communication": [
        "say", "tell", "speak", "talk", "ask", "answer", "explain", "describe",
        "discuss", "argue", "suggest", "recommend", "advise", "warn", "promise",
        "agree", "disagree", "confirm", "deny", "announce"
    ],
    "movement": [
        "go", "come", "walk", "run", "move", "travel", "arrive", "leave", "enter",
        "exit", "return", "approach", "follow", "lead", "climb", "jump", "fall",
        "fly", "drive", "ride"
    ],
    "time": [
        "now", "then", "before", "after", "soon", "later", "early", "late",
        "always", "never", "sometimes", "often", "rarely", "recently", "finally",
        "immediately", "eventually", "meanwhile", "yesterday", "tomorrow"
    ],
    "quantities": [
        "all", "some", "many", "few", "more", "less", "most", "none", "enough",
        "several", "various", "numerous", "plenty", "multiple", "single", "double",
        "half", "whole", "entire", "total"
    ],
    "learning": [
        "study", "learn", "teach", "understand", "practice", "master", "improve",
        "develop", "research", "investigate", "explore", "discover", "examine",
        "analyze", "comprehend", "memorize", "review", "test", "train", "educate"
    ],
    "problem_solving": [
        "solve", "fix", "resolve", "address", "tackle", "overcome", "handle",
        "manage", "deal", "approach", "analyze", "investigate", "diagnose",
        "identify", "determine", "figure", "work out", "troubleshoot"
    ],
    "creation": [
        "create", "make", "build", "design", "develop", "produce", "generate",
        "construct", "compose", "write", "draw", "paint", "craft", "invent",
        "innovate", "establish", "form", "shape", "manufacture"
    ],
}


# =============================================================================
# WORD RELATIONSHIPS
# =============================================================================

SYNONYMS = {
    "happy": ["joyful", "cheerful", "delighted", "pleased", "glad", "content"],
    "sad": ["unhappy", "sorrowful", "depressed", "melancholy", "gloomy", "down"],
    "big": ["large", "huge", "enormous", "massive", "giant", "vast"],
    "small": ["little", "tiny", "minute", "miniature", "compact", "petite"],
    "good": ["great", "excellent", "fine", "wonderful", "superb", "fantastic"],
    "bad": ["poor", "terrible", "awful", "horrible", "dreadful", "lousy"],
    "fast": ["quick", "rapid", "swift", "speedy", "hasty", "prompt"],
    "slow": ["sluggish", "leisurely", "gradual", "unhurried", "plodding"],
    "smart": ["intelligent", "clever", "brilliant", "wise", "bright", "sharp"],
    "stupid": ["foolish", "dumb", "silly", "idiotic", "dense", "dim"],
    "beautiful": ["pretty", "gorgeous", "lovely", "stunning", "attractive"],
    "ugly": ["unattractive", "hideous", "unsightly", "grotesque", "plain"],
    "easy": ["simple", "effortless", "straightforward", "uncomplicated"],
    "difficult": ["hard", "challenging", "tough", "demanding", "complex"],
    "important": ["significant", "crucial", "vital", "essential", "critical"],
    "help": ["assist", "aid", "support", "facilitate", "enable"],
    "start": ["begin", "commence", "initiate", "launch", "originate"],
    "end": ["finish", "complete", "conclude", "terminate", "cease"],
    "like": ["enjoy", "love", "appreciate", "prefer", "fancy"],
    "hate": ["detest", "loathe", "despise", "abhor", "dislike"],
}

ANTONYMS = {
    "happy": "sad", "big": "small", "good": "bad", "fast": "slow",
    "smart": "stupid", "beautiful": "ugly", "easy": "difficult",
    "hot": "cold", "light": "dark", "up": "down", "in": "out",
    "old": "new", "young": "old", "rich": "poor", "strong": "weak",
    "high": "low", "long": "short", "thick": "thin", "deep": "shallow",
    "wide": "narrow", "open": "closed", "full": "empty", "wet": "dry",
    "clean": "dirty", "safe": "dangerous", "quiet": "loud", "soft": "hard",
    "sweet": "sour", "true": "false", "right": "wrong", "love": "hate",
    "start": "end", "give": "take", "buy": "sell", "win": "lose",
    "remember": "forget", "find": "lose", "increase": "decrease",
}


# =============================================================================
# VOCABULARY CLASS
# =============================================================================

class EnglishVocabulary:
    """
    Comprehensive English vocabulary for NLU enhancement.
    
    Provides:
    - Word lookup with definitions
    - Synonyms and antonyms
    - Part-of-speech information
    - Semantic category membership
    - Word frequency ranking
    """
    
    def __init__(self):
        self.words: Dict[str, WordEntry] = {}
        self.synonyms = SYNONYMS.copy()
        self.antonyms = ANTONYMS.copy()
        self.categories = SEMANTIC_CATEGORIES.copy()
        
        # Load core words
        self._load_core_vocabulary()
        
    def _load_core_vocabulary(self):
        """Load core vocabulary."""
        self.words.update(CORE_100_WORDS)
        print(f"[EnglishVocabulary] Loaded {len(self.words)} core words")
        
    def lookup(self, word: str) -> Optional[WordEntry]:
        """Look up a word."""
        return self.words.get(word.lower())
        
    def get_definition(self, word: str) -> Optional[str]:
        """Get the primary definition of a word."""
        entry = self.lookup(word)
        if entry and entry.definitions:
            return entry.definitions[0]
        return None
        
    def get_synonyms(self, word: str) -> List[str]:
        """Get synonyms for a word."""
        word_lower = word.lower()
        
        # Check direct synonyms
        if word_lower in self.synonyms:
            return self.synonyms[word_lower]
            
        # Check word entry
        entry = self.lookup(word)
        if entry:
            return entry.synonyms
            
        return []
        
    def get_antonyms(self, word: str) -> List[str]:
        """Get antonyms for a word."""
        word_lower = word.lower()
        
        if word_lower in self.antonyms:
            ant = self.antonyms[word_lower]
            return [ant] if isinstance(ant, str) else ant
            
        entry = self.lookup(word)
        if entry:
            return entry.antonyms
            
        return []
        
    def get_pos(self, word: str) -> List[PartOfSpeech]:
        """Get parts of speech for a word."""
        entry = self.lookup(word)
        if entry:
            return entry.pos
        return []
        
    def get_category(self, word: str) -> List[str]:
        """Get semantic categories a word belongs to."""
        word_lower = word.lower()
        categories = []
        
        for cat, words in self.categories.items():
            if word_lower in words:
                categories.append(cat)
                
        return categories
        
    def find_related(self, word: str) -> Dict[str, List[str]]:
        """Find all related words."""
        return {
            "synonyms": self.get_synonyms(word),
            "antonyms": self.get_antonyms(word),
            "categories": self.get_category(word)
        }
        
    def is_in_category(self, word: str, category: str) -> bool:
        """Check if word is in a semantic category."""
        return category in self.get_category(word)
        
    def get_words_in_category(self, category: str) -> List[str]:
        """Get all words in a category."""
        return self.categories.get(category, [])
        
    def add_word(self, entry: WordEntry):
        """Add a word to the vocabulary."""
        self.words[entry.word.lower()] = entry
        
    def add_synonym_pair(self, word1: str, word2: str):
        """Add a synonym relationship."""
        w1, w2 = word1.lower(), word2.lower()
        
        if w1 not in self.synonyms:
            self.synonyms[w1] = []
        if w2 not in self.synonyms[w1]:
            self.synonyms[w1].append(w2)
            
        if w2 not in self.synonyms:
            self.synonyms[w2] = []
        if w1 not in self.synonyms[w2]:
            self.synonyms[w2].append(w1)
            
    def add_antonym_pair(self, word1: str, word2: str):
        """Add an antonym relationship."""
        self.antonyms[word1.lower()] = word2.lower()
        self.antonyms[word2.lower()] = word1.lower()
        
    def vocabulary_size(self) -> int:
        """Get total vocabulary size."""
        return len(self.words)
        
    def get_stats(self) -> Dict:
        """Get vocabulary statistics."""
        return {
            "total_words": len(self.words),
            "synonym_pairs": len(self.synonyms),
            "antonym_pairs": len(self.antonyms),
            "categories": len(self.categories),
            "words_with_definitions": sum(1 for w in self.words.values() if w.definitions)
        }


# Singleton instance
_vocabulary: Optional[EnglishVocabulary] = None


def get_vocabulary() -> EnglishVocabulary:
    """Get the global vocabulary instance."""
    global _vocabulary
    if _vocabulary is None:
        _vocabulary = EnglishVocabulary()
    return _vocabulary
