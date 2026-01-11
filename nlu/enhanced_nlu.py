# nlu/enhanced_nlu.py
# Enhanced Natural Language Understanding Engine

"""
Enhanced NLU Engine

This module provides advanced NLU capabilities:
1. Intent Classification - Understand user's purpose
2. Entity Extraction (NER) - Identify people, places, dates, etc.
3. Part-of-Speech Tagging - Grammatical analysis
4. Dependency Parsing - Sentence structure analysis
5. Semantic Role Labeling - Who did what to whom
6. Sentiment Analysis - Emotional tone detection
7. Coreference Resolution - Pronoun resolution
8. Context Tracking - Conversation memory
9. Vocabulary Integration - Word relationships and definitions

Vocabulary Requirements for Fluency:
- Basic conversation: ~1,000-2,000 words
- Everyday fluency: ~3,000-5,000 words (covers ~95% of text)
- Advanced fluency: ~8,000-10,000 words
- Near-native: ~15,000-20,000 words
- Educated adult: ~20,000-35,000 active words
"""

from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import re
from collections import defaultdict
import math


# =============================================================================
# ENUMERATIONS & DATA CLASSES
# =============================================================================

class Intent(Enum):
    """User intent categories."""
    GREETING = "greeting"
    FAREWELL = "farewell"
    QUESTION = "question"
    COMMAND = "command"
    STATEMENT = "statement"
    REQUEST = "request"
    CONFIRMATION = "confirmation"
    NEGATION = "negation"
    CLARIFICATION = "clarification"
    HELP = "help"
    THANKS = "thanks"
    APOLOGY = "apology"
    OPINION = "opinion"
    EMOTION = "emotion"
    SEARCH = "search"
    LEARN = "learn"
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    NAVIGATE = "navigate"
    UNKNOWN = "unknown"


class EntityType(Enum):
    """Named Entity types."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    TIME = "time"
    MONEY = "money"
    PERCENT = "percent"
    NUMBER = "number"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    DURATION = "duration"
    QUANTITY = "quantity"
    ORDINAL = "ordinal"
    LANGUAGE = "language"
    TECHNOLOGY = "technology"
    FILE = "file"
    COMMAND_ARG = "command_arg"


class POSTag(Enum):
    """Part-of-speech tags (simplified Penn Treebank)."""
    NOUN = "NN"           # Noun, singular
    NOUN_PLURAL = "NNS"   # Noun, plural
    PROPER_NOUN = "NNP"   # Proper noun
    PRONOUN = "PRP"       # Personal pronoun
    VERB = "VB"           # Verb, base form
    VERB_PAST = "VBD"     # Verb, past tense
    VERB_ING = "VBG"      # Verb, gerund
    VERB_3S = "VBZ"       # Verb, 3rd person singular
    ADJECTIVE = "JJ"      # Adjective
    ADJECTIVE_COMP = "JJR" # Adjective, comparative
    ADJECTIVE_SUP = "JJS" # Adjective, superlative
    ADVERB = "RB"         # Adverb
    PREPOSITION = "IN"    # Preposition
    CONJUNCTION = "CC"    # Coordinating conjunction
    DETERMINER = "DT"     # Determiner
    INTERJECTION = "UH"   # Interjection
    MODAL = "MD"          # Modal verb
    PARTICLE = "RP"       # Particle
    PUNCTUATION = "PUNCT" # Punctuation
    UNKNOWN = "UNK"       # Unknown


class Sentiment(Enum):
    """Sentiment categories."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


@dataclass
class Entity:
    """Extracted entity."""
    text: str
    entity_type: EntityType
    start: int
    end: int
    confidence: float = 1.0
    normalized: Optional[str] = None


@dataclass
class Token:
    """Tokenized word with annotations."""
    text: str
    lemma: str
    pos: POSTag
    start: int
    end: int
    index: int
    head: int = -1  # Index of syntactic head
    dep_rel: str = "root"  # Dependency relation


@dataclass
class IntentResult:
    """Intent classification result."""
    intent: Intent
    confidence: float
    sub_intent: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SentimentResult:
    """Sentiment analysis result."""
    sentiment: Sentiment
    score: float  # -1.0 to 1.0
    confidence: float
    emotions: Dict[str, float] = field(default_factory=dict)


@dataclass
class SemanticRole:
    """Semantic role in a sentence."""
    role: str  # agent, patient, theme, location, time, etc.
    text: str
    start: int
    end: int


@dataclass
class NLUResult:
    """Complete NLU analysis result."""
    text: str
    tokens: List[Token]
    intent: IntentResult
    entities: List[Entity]
    sentiment: SentimentResult
    semantic_roles: List[SemanticRole]
    key_phrases: List[str]
    topics: List[str]


# =============================================================================
# INTENT PATTERNS
# =============================================================================

INTENT_PATTERNS = {
    Intent.GREETING: [
        r"^(hi|hello|hey|howdy|greetings|good\s*(morning|afternoon|evening|day)|what'?s?\s*up)",
        r"^yo\b", r"^hiya", r"^sup\b"
    ],
    Intent.FAREWELL: [
        r"(bye|goodbye|see\s*you|farewell|later|take\s*care|good\s*night|cya)",
        r"(have\s*a\s*(good|nice)\s*(day|night|one))", r"^peace\b"
    ],
    Intent.QUESTION: [
        r"^(what|who|where|when|why|how|which|whose|whom|is|are|was|were|do|does|did|can|could|would|will|should|shall|has|have|had)\b",
        r"\?\s*$", r"^tell\s*me\b", r"^explain\b"
    ],
    Intent.COMMAND: [
        r"^(open|close|run|execute|start|stop|create|delete|show|hide|save|load|set|get|enable|disable|turn\s*(on|off))\b",
        r"^(please\s*)?(do|make|let|give|send|find|search|play|pause|next|previous|go)\b"
    ],
    Intent.REQUEST: [
        r"(can|could|would|will)\s*you\s*(please)?",
        r"^(please|kindly|I\s*(want|need|would\s*like))\b",
        r"^(help\s*me|assist\s*me|I\s*need)\b"
    ],
    Intent.CONFIRMATION: [
        r"^(yes|yeah|yep|yup|sure|okay|ok|alright|right|correct|exactly|indeed|absolutely|definitely|of\s*course)\b",
        r"^(that'?s?\s*(right|correct|true))\b"
    ],
    Intent.NEGATION: [
        r"^(no|nope|nah|not|never|don'?t|doesn'?t|didn'?t|won'?t|wouldn'?t|can'?t|cannot|shouldn'?t)\b",
        r"^(that'?s?\s*(wrong|incorrect|false|not\s*right))\b"
    ],
    Intent.HELP: [
        r"^(help|assist|support)\b", r"(need\s*help|having\s*(trouble|issues|problems))",
        r"^(how\s*(do\s*I|can\s*I|to))\b", r"^(what\s*can\s*you\s*do)\b"
    ],
    Intent.THANKS: [
        r"^(thank|thanks|thx|ty|appreciate|grateful)\b",
        r"(thank\s*you|thanks\s*(a\s*lot|so\s*much|very\s*much))"
    ],
    Intent.APOLOGY: [
        r"^(sorry|apolog|my\s*bad|excuse\s*me|pardon)\b",
        r"(I'?m\s*sorry|forgive\s*me)"
    ],
    Intent.SEARCH: [
        r"^(search|find|look\s*(up|for)|google|query)\b",
        r"(search\s*for|looking\s*for|find\s*me)\b"
    ],
    Intent.LEARN: [
        r"^(learn|study|teach|explain|understand)\b",
        r"(how\s*to\s*learn|teach\s*me|explain\s*(to\s*me)?)\b",
        r"(want\s*to\s*(learn|understand|know))\b"
    ],
    Intent.CREATE: [
        r"^(create|make|build|generate|new|add)\b",
        r"(create\s*(a|an|new)|make\s*(a|an|new))\b"
    ],
    Intent.DELETE: [
        r"^(delete|remove|erase|destroy|clear)\b"
    ],
    Intent.UPDATE: [
        r"^(update|modify|change|edit|fix|correct)\b"
    ],
}


# =============================================================================
# ENTITY PATTERNS
# =============================================================================

ENTITY_PATTERNS = {
    EntityType.EMAIL: r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
    EntityType.URL: r'https?://[^\s<>"{}|\\^`\[\]]+',
    EntityType.PHONE: r'\b(\+?1?\s*)?(\([0-9]{3}\)|[0-9]{3})[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
    EntityType.MONEY: r'\$\s*[0-9,]+(\.[0-9]{2})?\b|\b[0-9,]+\s*(dollars?|cents?|USD|EUR|GBP)\b',
    EntityType.PERCENT: r'\b[0-9]+(\.[0-9]+)?%|\b[0-9]+(\.[0-9]+)?\s*percent\b',
    EntityType.DATE: r'\b(jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|jun(e)?|jul(y)?|aug(ust)?|sep(t)?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?)\s+[0-9]{1,2}(,?\s*[0-9]{4})?\b|\b[0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}\b|\b(today|tomorrow|yesterday)\b',
    EntityType.TIME: r'\b[0-9]{1,2}:[0-9]{2}(:[0-9]{2})?\s*(am|pm|AM|PM)?\b|\b(noon|midnight|morning|afternoon|evening|night)\b',
    EntityType.NUMBER: r'\b[0-9,]+(\.[0-9]+)?\b',
    EntityType.ORDINAL: r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|[0-9]+(st|nd|rd|th))\b',
    EntityType.DURATION: r'\b[0-9]+\s*(seconds?|minutes?|hours?|days?|weeks?|months?|years?)\b',
    EntityType.FILE: r'\b[\w\-\.]+\.(py|js|ts|html|css|json|yaml|yml|md|txt|pdf|doc|docx|xls|xlsx|png|jpg|jpeg|gif|mp3|mp4)\b',
    EntityType.TECHNOLOGY: r'\b(python|javascript|java|c\+\+|rust|go|ruby|php|swift|kotlin|react|angular|vue|node|django|flask|tensorflow|pytorch)\b',
    EntityType.LANGUAGE: r'\b(english|spanish|french|german|chinese|japanese|korean|arabic|hindi|portuguese|russian|italian)\b',
}


# =============================================================================
# SENTIMENT LEXICON
# =============================================================================

POSITIVE_WORDS = {
    # Strong positive (score: 0.8-1.0)
    "amazing": 0.9, "awesome": 0.9, "excellent": 0.9, "fantastic": 0.9, "wonderful": 0.9,
    "brilliant": 0.85, "outstanding": 0.85, "perfect": 0.95, "superb": 0.85, "incredible": 0.85,
    "love": 0.9, "adore": 0.85, "thrilled": 0.85, "ecstatic": 0.9,
    
    # Moderate positive (score: 0.5-0.79)
    "good": 0.6, "great": 0.7, "nice": 0.55, "lovely": 0.65, "pleasant": 0.55,
    "happy": 0.7, "glad": 0.6, "pleased": 0.65, "satisfied": 0.6, "delighted": 0.75,
    "enjoy": 0.65, "like": 0.5, "appreciate": 0.6, "grateful": 0.7, "thankful": 0.65,
    "helpful": 0.6, "useful": 0.55, "valuable": 0.6, "beneficial": 0.55,
    "beautiful": 0.7, "pretty": 0.55, "elegant": 0.6,
    "excited": 0.7, "eager": 0.6, "enthusiastic": 0.7, "optimistic": 0.65,
    "confident": 0.6, "proud": 0.65, "successful": 0.7,
    
    # Mild positive (score: 0.2-0.49)
    "okay": 0.3, "fine": 0.35, "alright": 0.3, "decent": 0.4, "acceptable": 0.35,
    "interesting": 0.45, "cool": 0.4, "neat": 0.4,
}

NEGATIVE_WORDS = {
    # Strong negative (score: -0.8 to -1.0)
    "terrible": -0.9, "horrible": -0.9, "awful": -0.85, "dreadful": -0.85, "disgusting": -0.9,
    "hate": -0.9, "despise": -0.85, "loathe": -0.85, "detest": -0.85,
    "furious": -0.85, "enraged": -0.9, "outraged": -0.85,
    "devastating": -0.85, "catastrophic": -0.9, "disastrous": -0.85,
    
    # Moderate negative (score: -0.5 to -0.79)
    "bad": -0.6, "poor": -0.55, "wrong": -0.5, "ugly": -0.6, "nasty": -0.65,
    "sad": -0.6, "unhappy": -0.6, "upset": -0.55, "disappointed": -0.6, "frustrated": -0.65,
    "angry": -0.7, "annoyed": -0.55, "irritated": -0.55,
    "afraid": -0.6, "scared": -0.6, "worried": -0.55, "anxious": -0.55, "nervous": -0.5,
    "useless": -0.6, "worthless": -0.7, "boring": -0.5, "stupid": -0.65, "dumb": -0.6,
    "confusing": -0.5, "difficult": -0.4, "hard": -0.3, "problem": -0.5,
    "fail": -0.6, "failed": -0.6, "failure": -0.65, "mistake": -0.5, "error": -0.5,
    
    # Mild negative (score: -0.2 to -0.49)
    "meh": -0.3, "mediocre": -0.4, "lacking": -0.35,
    "tired": -0.35, "bored": -0.4, "unsure": -0.25,
}

NEGATION_WORDS = {"not", "no", "never", "none", "neither", "nobody", "nothing", "nowhere",
                  "don't", "doesn't", "didn't", "won't", "wouldn't", "can't", "cannot",
                  "couldn't", "shouldn't", "isn't", "aren't", "wasn't", "weren't", "haven't",
                  "hasn't", "hadn't"}

INTENSIFIERS = {"very": 1.3, "extremely": 1.5, "really": 1.25, "absolutely": 1.4,
                "totally": 1.3, "completely": 1.4, "incredibly": 1.4, "highly": 1.3,
                "so": 1.2, "super": 1.3, "too": 1.15, "quite": 1.1, "rather": 1.1}

DIMINISHERS = {"somewhat": 0.7, "slightly": 0.6, "barely": 0.5, "hardly": 0.5,
               "a little": 0.7, "a bit": 0.7, "kind of": 0.7, "sort of": 0.7}


# =============================================================================
# POS TAGGING PATTERNS
# =============================================================================

# Common word lists for POS tagging
DETERMINERS = {"the", "a", "an", "this", "that", "these", "those", "my", "your", "his",
               "her", "its", "our", "their", "some", "any", "no", "every", "each", "all",
               "both", "few", "many", "much", "most", "several", "other", "another"}

PRONOUNS = {"i", "me", "my", "mine", "myself", "you", "your", "yours", "yourself",
            "he", "him", "his", "himself", "she", "her", "hers", "herself",
            "it", "its", "itself", "we", "us", "our", "ours", "ourselves",
            "they", "them", "their", "theirs", "themselves",
            "who", "whom", "whose", "which", "what", "that"}

PREPOSITIONS = {"in", "on", "at", "by", "for", "with", "about", "against", "between",
                "into", "through", "during", "before", "after", "above", "below",
                "to", "from", "up", "down", "out", "off", "over", "under", "again",
                "further", "then", "once", "of", "as", "until", "while", "toward",
                "towards", "upon", "across", "along", "around", "behind", "beside",
                "besides", "beyond", "within", "without", "throughout", "despite"}

CONJUNCTIONS = {"and", "but", "or", "nor", "for", "yet", "so", "because", "although",
                "though", "while", "if", "unless", "until", "when", "where", "whereas",
                "whether", "after", "before", "since", "as", "that", "than"}

MODAL_VERBS = {"can", "could", "may", "might", "must", "shall", "should", "will",
               "would", "ought"}

AUXILIARY_VERBS = {"be", "am", "is", "are", "was", "were", "been", "being",
                   "have", "has", "had", "having", "do", "does", "did", "doing"}

INTERJECTIONS = {"oh", "ah", "wow", "oops", "ouch", "ugh", "hmm", "huh", "um", "uh",
                 "hey", "hi", "hello", "bye", "goodbye", "yes", "no", "yeah", "nope",
                 "please", "thanks", "sorry", "well", "okay", "ok"}


# =============================================================================
# ENHANCED NLU ENGINE
# =============================================================================

class EnhancedNLUEngine:
    """
    Enhanced Natural Language Understanding Engine.
    
    Provides comprehensive NLU capabilities including:
    - Intent classification
    - Entity extraction
    - POS tagging
    - Sentiment analysis
    - Semantic role labeling
    - Key phrase extraction
    """
    
    def __init__(self):
        self.context: List[NLUResult] = []
        self.max_context = 10
        self.vocabulary = None
        self._load_vocabulary()
        
        # Compiled regex patterns for efficiency
        self.intent_patterns_compiled = {
            intent: [re.compile(p, re.IGNORECASE) for p in patterns]
            for intent, patterns in INTENT_PATTERNS.items()
        }
        self.entity_patterns_compiled = {
            etype: re.compile(pattern, re.IGNORECASE)
            for etype, pattern in ENTITY_PATTERNS.items()
        }
        
    def _load_vocabulary(self):
        """Load vocabulary if available."""
        try:
            from unimind.models.native.vocabulary import get_vocabulary
            from unimind.models.native.vocabulary_extended import load_extended_vocabulary
            self.vocabulary = get_vocabulary()
            load_extended_vocabulary(self.vocabulary)
        except ImportError:
            self.vocabulary = None
            
    def analyze(self, text: str, use_context: bool = True) -> NLUResult:
        """
        Perform complete NLU analysis on input text.
        
        Args:
            text: Input text to analyze
            use_context: Whether to use conversation context
            
        Returns:
            NLUResult with all analysis
        """
        # Tokenize
        tokens = self.tokenize(text)
        
        # Intent classification
        intent = self.classify_intent(text, tokens)
        
        # Entity extraction
        entities = self.extract_entities(text)
        
        # Sentiment analysis
        sentiment = self.analyze_sentiment(text, tokens)
        
        # Semantic role labeling
        semantic_roles = self.extract_semantic_roles(text, tokens, entities)
        
        # Key phrase extraction
        key_phrases = self.extract_key_phrases(tokens)
        
        # Topic extraction
        topics = self.extract_topics(tokens, entities)
        
        result = NLUResult(
            text=text,
            tokens=tokens,
            intent=intent,
            entities=entities,
            sentiment=sentiment,
            semantic_roles=semantic_roles,
            key_phrases=key_phrases,
            topics=topics
        )
        
        # Update context
        if use_context:
            self.context.append(result)
            if len(self.context) > self.max_context:
                self.context.pop(0)
                
        return result
        
    def tokenize(self, text: str) -> List[Token]:
        """
        Tokenize text and add POS tags.
        
        Args:
            text: Input text
            
        Returns:
            List of Token objects with POS tags
        """
        tokens = []
        
        # Simple tokenization pattern
        pattern = r"(\w+(?:'\w+)?|[^\w\s])"
        
        for idx, match in enumerate(re.finditer(pattern, text)):
            word = match.group()
            start = match.start()
            end = match.end()
            
            # Get POS tag
            pos = self._get_pos_tag(word, idx, text)
            
            # Get lemma
            lemma = self._get_lemma(word, pos)
            
            token = Token(
                text=word,
                lemma=lemma,
                pos=pos,
                start=start,
                end=end,
                index=idx
            )
            tokens.append(token)
            
        # Add dependency relations (simplified)
        self._add_dependencies(tokens)
        
        return tokens
        
    def _get_pos_tag(self, word: str, position: int, context: str) -> POSTag:
        """Determine part-of-speech tag for a word."""
        word_lower = word.lower()
        
        # Punctuation
        if re.match(r'^[^\w\s]$', word):
            return POSTag.PUNCTUATION
            
        # Determiners
        if word_lower in DETERMINERS:
            return POSTag.DETERMINER
            
        # Pronouns
        if word_lower in PRONOUNS:
            return POSTag.PRONOUN
            
        # Prepositions
        if word_lower in PREPOSITIONS:
            return POSTag.PREPOSITION
            
        # Conjunctions
        if word_lower in CONJUNCTIONS:
            return POSTag.CONJUNCTION
            
        # Modal verbs
        if word_lower in MODAL_VERBS:
            return POSTag.MODAL
            
        # Interjections
        if word_lower in INTERJECTIONS and position == 0:
            return POSTag.INTERJECTION
            
        # Auxiliary verbs
        if word_lower in AUXILIARY_VERBS:
            return POSTag.VERB
            
        # Check vocabulary for POS
        if self.vocabulary:
            entry = self.vocabulary.lookup(word_lower)
            if entry:
                from unimind.models.native.vocabulary import PartOfSpeech as VocabPOS
                pos_map = {
                    VocabPOS.NOUN: POSTag.NOUN,
                    VocabPOS.VERB: POSTag.VERB,
                    VocabPOS.ADJECTIVE: POSTag.ADJECTIVE,
                    VocabPOS.ADVERB: POSTag.ADVERB,
                    VocabPOS.PRONOUN: POSTag.PRONOUN,
                    VocabPOS.PREPOSITION: POSTag.PREPOSITION,
                    VocabPOS.CONJUNCTION: POSTag.CONJUNCTION,
                    VocabPOS.INTERJECTION: POSTag.INTERJECTION,
                }
                if entry.pos:
                    return pos_map.get(entry.pos[0], POSTag.UNKNOWN)
                    
        # Heuristic rules
        if word.endswith('ly') and len(word) > 3:
            return POSTag.ADVERB
        if word.endswith(('ing', 'ed', 'es', 's')) and len(word) > 3:
            return POSTag.VERB
        if word.endswith(('ness', 'ment', 'tion', 'sion', 'ity')):
            return POSTag.NOUN
        if word.endswith(('ful', 'less', 'ous', 'ive', 'able', 'ible')):
            return POSTag.ADJECTIVE
        if word[0].isupper() and position > 0:
            return POSTag.PROPER_NOUN
            
        # Default to noun
        return POSTag.NOUN
        
    def _get_lemma(self, word: str, pos: POSTag) -> str:
        """Get lemma (base form) of word."""
        word_lower = word.lower()
        
        # Common irregular verbs
        irregular_verbs = {
            "am": "be", "is": "be", "are": "be", "was": "be", "were": "be",
            "been": "be", "being": "be",
            "have": "have", "has": "have", "had": "have", "having": "have",
            "do": "do", "does": "do", "did": "do", "doing": "do",
            "go": "go", "goes": "go", "went": "go", "gone": "go", "going": "go",
            "say": "say", "says": "say", "said": "say", "saying": "say",
            "get": "get", "gets": "get", "got": "get", "gotten": "get",
            "make": "make", "makes": "make", "made": "make", "making": "make",
            "know": "know", "knows": "know", "knew": "know", "known": "know",
            "think": "think", "thinks": "think", "thought": "think",
            "take": "take", "takes": "take", "took": "take", "taken": "take",
            "see": "see", "sees": "see", "saw": "see", "seen": "see",
            "come": "come", "comes": "come", "came": "come", "coming": "come",
            "want": "want", "wants": "want", "wanted": "want",
            "use": "use", "uses": "use", "used": "use", "using": "use",
            "find": "find", "finds": "find", "found": "find",
            "give": "give", "gives": "give", "gave": "give", "given": "give",
            "tell": "tell", "tells": "tell", "told": "tell",
            "can": "can", "could": "can",
            "will": "will", "would": "will",
            "may": "may", "might": "may",
            "must": "must",
            "should": "shall",
        }
        
        if word_lower in irregular_verbs:
            return irregular_verbs[word_lower]
            
        # Regular verb suffixes
        if pos in (POSTag.VERB, POSTag.VERB_PAST, POSTag.VERB_ING, POSTag.VERB_3S):
            if word_lower.endswith('ied'):
                return word_lower[:-3] + 'y'
            if word_lower.endswith('ed'):
                if word_lower.endswith('eed'):
                    return word_lower[:-2]
                return word_lower[:-2] if len(word_lower) > 4 else word_lower[:-1]
            if word_lower.endswith('ing'):
                base = word_lower[:-3]
                if base.endswith('i'):
                    return base[:-1] + 'y'
                return base
            if word_lower.endswith('ies'):
                return word_lower[:-3] + 'y'
            if word_lower.endswith('es'):
                return word_lower[:-2]
            if word_lower.endswith('s') and not word_lower.endswith('ss'):
                return word_lower[:-1]
                
        # Noun plurals
        if pos in (POSTag.NOUN, POSTag.NOUN_PLURAL):
            if word_lower.endswith('ies'):
                return word_lower[:-3] + 'y'
            if word_lower.endswith('es'):
                return word_lower[:-2]
            if word_lower.endswith('s') and not word_lower.endswith('ss'):
                return word_lower[:-1]
                
        return word_lower
        
    def _add_dependencies(self, tokens: List[Token]):
        """Add simplified dependency relations."""
        if not tokens:
            return
            
        # Find main verb as root
        root_idx = -1
        for i, token in enumerate(tokens):
            if token.pos in (POSTag.VERB, POSTag.VERB_PAST, POSTag.VERB_3S):
                root_idx = i
                break
                
        if root_idx == -1 and tokens:
            root_idx = 0
            
        # Set dependencies
        for i, token in enumerate(tokens):
            if i == root_idx:
                token.head = -1
                token.dep_rel = "root"
            elif token.pos == POSTag.DETERMINER:
                # Link to next noun
                for j in range(i + 1, len(tokens)):
                    if tokens[j].pos in (POSTag.NOUN, POSTag.NOUN_PLURAL, POSTag.PROPER_NOUN):
                        token.head = j
                        token.dep_rel = "det"
                        break
            elif token.pos == POSTag.ADJECTIVE:
                # Link to next noun
                for j in range(i + 1, len(tokens)):
                    if tokens[j].pos in (POSTag.NOUN, POSTag.NOUN_PLURAL, POSTag.PROPER_NOUN):
                        token.head = j
                        token.dep_rel = "amod"
                        break
            elif token.pos == POSTag.ADVERB:
                # Link to verb
                token.head = root_idx
                token.dep_rel = "advmod"
            elif token.pos == POSTag.PREPOSITION:
                token.head = root_idx
                token.dep_rel = "prep"
            else:
                token.head = root_idx
                token.dep_rel = "dep"
                
    def classify_intent(self, text: str, tokens: List[Token] = None) -> IntentResult:
        """
        Classify the intent of the input text.
        
        Args:
            text: Input text
            tokens: Optional pre-computed tokens
            
        Returns:
            IntentResult with classification
        """
        text_lower = text.lower().strip()
        
        # Check patterns for each intent
        scores = {}
        for intent, patterns in self.intent_patterns_compiled.items():
            score = 0.0
            for pattern in patterns:
                if pattern.search(text_lower):
                    score = max(score, 0.8)  # Pattern match gives high confidence
            scores[intent] = score
            
        # Additional heuristics
        if text.endswith('?'):
            scores[Intent.QUESTION] = max(scores.get(Intent.QUESTION, 0), 0.7)
        if text.endswith('!'):
            if any(word in text_lower for word in ['please', 'help', 'need']):
                scores[Intent.REQUEST] = max(scores.get(Intent.REQUEST, 0), 0.6)
            else:
                scores[Intent.COMMAND] = max(scores.get(Intent.COMMAND, 0), 0.5)
                
        # Find best intent
        best_intent = Intent.UNKNOWN
        best_score = 0.0
        for intent, score in scores.items():
            if score > best_score:
                best_score = score
                best_intent = intent
                
        # If no strong match, use statement
        if best_score < 0.3:
            best_intent = Intent.STATEMENT
            best_score = 0.5
            
        # Extract sub-intent parameters
        params = self._extract_intent_params(text, best_intent, tokens)
        
        return IntentResult(
            intent=best_intent,
            confidence=best_score,
            parameters=params
        )
        
    def _extract_intent_params(self, text: str, intent: Intent, tokens: List[Token]) -> Dict:
        """Extract parameters relevant to the intent."""
        params = {}
        
        if intent == Intent.QUESTION:
            # Identify question type
            text_lower = text.lower()
            if text_lower.startswith('what'):
                params['question_type'] = 'what'
            elif text_lower.startswith('who'):
                params['question_type'] = 'who'
            elif text_lower.startswith('where'):
                params['question_type'] = 'where'
            elif text_lower.startswith('when'):
                params['question_type'] = 'when'
            elif text_lower.startswith('why'):
                params['question_type'] = 'why'
            elif text_lower.startswith('how'):
                params['question_type'] = 'how'
            else:
                params['question_type'] = 'yes_no'
                
        elif intent == Intent.COMMAND:
            # Extract command verb
            if tokens:
                for token in tokens:
                    if token.pos in (POSTag.VERB, POSTag.VERB_3S):
                        params['action'] = token.lemma
                        break
                        
        return params
        
    def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract named entities from text.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted entities
        """
        entities = []
        
        # Pattern-based extraction
        for entity_type, pattern in self.entity_patterns_compiled.items():
            for match in pattern.finditer(text):
                entity = Entity(
                    text=match.group(),
                    entity_type=entity_type,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9
                )
                entities.append(entity)
                
        # Capitalize proper nouns as potential PERSON/ORGANIZATION
        words = text.split()
        for i, word in enumerate(words):
            # Skip first word and already matched entities
            if i == 0:
                continue
            if word[0].isupper() and word.isalpha():
                # Check if not already captured
                word_start = text.find(word)
                already_captured = any(
                    e.start <= word_start < e.end for e in entities
                )
                if not already_captured:
                    entities.append(Entity(
                        text=word,
                        entity_type=EntityType.PERSON,  # Default to person
                        start=word_start,
                        end=word_start + len(word),
                        confidence=0.5
                    ))
                    
        # Sort by position
        entities.sort(key=lambda e: e.start)
        
        return entities
        
    def analyze_sentiment(self, text: str, tokens: List[Token] = None) -> SentimentResult:
        """
        Analyze sentiment of text.
        
        Args:
            text: Input text
            tokens: Optional pre-computed tokens
            
        Returns:
            SentimentResult with sentiment analysis
        """
        words = text.lower().split()
        
        total_score = 0.0
        word_count = 0
        emotions = defaultdict(float)
        
        i = 0
        while i < len(words):
            word = words[i].strip('.,!?')
            
            # Check for negation
            negated = False
            if i > 0 and words[i-1] in NEGATION_WORDS:
                negated = True
                
            # Check for intensifier
            intensifier = 1.0
            if i > 0:
                prev = words[i-1]
                if prev in INTENSIFIERS:
                    intensifier = INTENSIFIERS[prev]
                elif prev in DIMINISHERS:
                    intensifier = DIMINISHERS[prev]
                    
            # Score word
            score = 0.0
            if word in POSITIVE_WORDS:
                score = POSITIVE_WORDS[word]
                emotions['joy'] += abs(score)
            elif word in NEGATIVE_WORDS:
                score = NEGATIVE_WORDS[word]
                if score < -0.5:
                    emotions['sadness'] += abs(score)
                else:
                    emotions['frustration'] += abs(score)
                    
            if score != 0:
                if negated:
                    score = -score * 0.8  # Negation flips and slightly diminishes
                score *= intensifier
                total_score += score
                word_count += 1
                
            i += 1
            
        # Calculate final score
        if word_count > 0:
            avg_score = total_score / word_count
        else:
            avg_score = 0.0
            
        # Normalize to -1 to 1
        final_score = max(-1.0, min(1.0, avg_score))
        
        # Determine sentiment category
        if final_score >= 0.6:
            sentiment = Sentiment.VERY_POSITIVE
        elif final_score >= 0.2:
            sentiment = Sentiment.POSITIVE
        elif final_score <= -0.6:
            sentiment = Sentiment.VERY_NEGATIVE
        elif final_score <= -0.2:
            sentiment = Sentiment.NEGATIVE
        else:
            sentiment = Sentiment.NEUTRAL
            
        # Normalize emotions
        if emotions:
            total_emotion = sum(emotions.values())
            if total_emotion > 0:
                emotions = {k: v / total_emotion for k, v in emotions.items()}
                
        return SentimentResult(
            sentiment=sentiment,
            score=final_score,
            confidence=0.6 + (0.4 * min(word_count / 5, 1.0)),
            emotions=dict(emotions)
        )
        
    def extract_semantic_roles(self, text: str, tokens: List[Token], 
                               entities: List[Entity]) -> List[SemanticRole]:
        """
        Extract semantic roles (who did what to whom).
        
        Args:
            text: Input text
            tokens: Tokenized text
            entities: Extracted entities
            
        Returns:
            List of semantic roles
        """
        roles = []
        
        # Find subject (agent)
        for i, token in enumerate(tokens):
            if token.pos in (POSTag.PRONOUN, POSTag.PROPER_NOUN, POSTag.NOUN):
                # Check if before main verb
                is_subject = True
                for j in range(i + 1, len(tokens)):
                    if tokens[j].pos in (POSTag.VERB, POSTag.VERB_3S):
                        roles.append(SemanticRole(
                            role="agent",
                            text=token.text,
                            start=token.start,
                            end=token.end
                        ))
                        break
                break
                
        # Find action (predicate)
        for token in tokens:
            if token.pos in (POSTag.VERB, POSTag.VERB_PAST, POSTag.VERB_3S):
                if token.text.lower() not in AUXILIARY_VERBS:
                    roles.append(SemanticRole(
                        role="action",
                        text=token.text,
                        start=token.start,
                        end=token.end
                    ))
                    break
                    
        # Find object (patient/theme)
        # Look for nouns after the verb
        found_verb = False
        for token in tokens:
            if token.pos in (POSTag.VERB, POSTag.VERB_3S):
                found_verb = True
                continue
            if found_verb and token.pos in (POSTag.NOUN, POSTag.NOUN_PLURAL, POSTag.PROPER_NOUN):
                roles.append(SemanticRole(
                    role="patient",
                    text=token.text,
                    start=token.start,
                    end=token.end
                ))
                break
                
        # Add location and time from entities
        for entity in entities:
            if entity.entity_type == EntityType.LOCATION:
                roles.append(SemanticRole(
                    role="location",
                    text=entity.text,
                    start=entity.start,
                    end=entity.end
                ))
            elif entity.entity_type in (EntityType.DATE, EntityType.TIME):
                roles.append(SemanticRole(
                    role="time",
                    text=entity.text,
                    start=entity.start,
                    end=entity.end
                ))
                
        return roles
        
    def extract_key_phrases(self, tokens: List[Token]) -> List[str]:
        """
        Extract key phrases from tokens.
        
        Args:
            tokens: Tokenized text
            
        Returns:
            List of key phrases
        """
        phrases = []
        
        # Look for noun phrases (Det? Adj* Noun+)
        i = 0
        while i < len(tokens):
            phrase_tokens = []
            
            # Optional determiner
            if tokens[i].pos == POSTag.DETERMINER:
                phrase_tokens.append(tokens[i])
                i += 1
                if i >= len(tokens):
                    break
                    
            # Adjectives
            while i < len(tokens) and tokens[i].pos == POSTag.ADJECTIVE:
                phrase_tokens.append(tokens[i])
                i += 1
                
            # Nouns
            while i < len(tokens) and tokens[i].pos in (POSTag.NOUN, POSTag.NOUN_PLURAL, POSTag.PROPER_NOUN):
                phrase_tokens.append(tokens[i])
                i += 1
                
            # If we have a noun phrase
            if phrase_tokens and any(t.pos in (POSTag.NOUN, POSTag.NOUN_PLURAL, POSTag.PROPER_NOUN) 
                                     for t in phrase_tokens):
                # Skip determiners in output
                content_tokens = [t for t in phrase_tokens if t.pos != POSTag.DETERMINER]
                if content_tokens:
                    phrase = ' '.join(t.text for t in content_tokens)
                    phrases.append(phrase)
            else:
                i += 1
                
        return phrases
        
    def extract_topics(self, tokens: List[Token], entities: List[Entity]) -> List[str]:
        """
        Extract main topics from text.
        
        Args:
            tokens: Tokenized text
            entities: Extracted entities
            
        Returns:
            List of topic strings
        """
        topics = []
        
        # Add entity texts as topics
        for entity in entities:
            if entity.entity_type in (EntityType.PERSON, EntityType.ORGANIZATION, 
                                       EntityType.LOCATION, EntityType.TECHNOLOGY):
                topics.append(entity.text)
                
        # Add noun lemmas as topics
        for token in tokens:
            if token.pos in (POSTag.NOUN, POSTag.NOUN_PLURAL, POSTag.PROPER_NOUN):
                if token.lemma not in topics and len(token.lemma) > 2:
                    topics.append(token.lemma)
                    
        return topics[:5]  # Limit to top 5 topics
        
    def resolve_coreferences(self, text: str) -> Dict[str, List[str]]:
        """
        Resolve coreferences (pronouns to their referents).
        
        Args:
            text: Input text
            
        Returns:
            Dict mapping pronouns to their likely referents
        """
        coreferences = {}
        
        # Use context for resolution
        if self.context:
            last_result = self.context[-1]
            
            # Find pronouns in current text
            tokens = self.tokenize(text)
            for token in tokens:
                if token.pos == POSTag.PRONOUN:
                    pronoun = token.text.lower()
                    
                    # Look for antecedent in previous context
                    for prev in reversed(self.context):
                        for entity in prev.entities:
                            if entity.entity_type == EntityType.PERSON:
                                if pronoun in ('he', 'him', 'his'):
                                    coreferences[pronoun] = coreferences.get(pronoun, [])
                                    coreferences[pronoun].append(entity.text)
                                elif pronoun in ('she', 'her', 'hers'):
                                    coreferences[pronoun] = coreferences.get(pronoun, [])
                                    coreferences[pronoun].append(entity.text)
                                    
        return coreferences
        
    def get_word_info(self, word: str) -> Optional[Dict]:
        """
        Get information about a word from vocabulary.
        
        Args:
            word: Word to look up
            
        Returns:
            Dict with word information or None
        """
        if self.vocabulary:
            entry = self.vocabulary.lookup(word)
            if entry:
                return {
                    "word": entry.word,
                    "definitions": entry.definitions,
                    "pos": [p.value for p in entry.pos],
                    "synonyms": entry.synonyms,
                    "antonyms": entry.antonyms,
                    "frequency": entry.frequency.name,
                    "related": self.vocabulary.find_related(word)
                }
        return None
        
    def get_synonyms(self, word: str) -> List[str]:
        """Get synonyms for a word."""
        if self.vocabulary:
            return self.vocabulary.get_synonyms(word)
        return []
        
    def get_antonyms(self, word: str) -> List[str]:
        """Get antonyms for a word."""
        if self.vocabulary:
            return self.vocabulary.get_antonyms(word)
        return []
        
    def clear_context(self):
        """Clear conversation context."""
        self.context = []
        
    def get_stats(self) -> Dict:
        """Get NLU engine statistics."""
        return {
            "context_size": len(self.context),
            "max_context": self.max_context,
            "vocabulary_loaded": self.vocabulary is not None,
            "vocabulary_size": self.vocabulary.vocabulary_size() if self.vocabulary else 0,
            "intent_patterns": len(INTENT_PATTERNS),
            "entity_patterns": len(ENTITY_PATTERNS),
            "sentiment_words": len(POSITIVE_WORDS) + len(NEGATIVE_WORDS)
        }


# =============================================================================
# SINGLETON & HELPER FUNCTIONS
# =============================================================================

_nlu_engine: Optional[EnhancedNLUEngine] = None


def get_nlu_engine() -> EnhancedNLUEngine:
    """Get the global NLU engine instance."""
    global _nlu_engine
    if _nlu_engine is None:
        _nlu_engine = EnhancedNLUEngine()
    return _nlu_engine


def analyze(text: str) -> NLUResult:
    """Quick analyze function."""
    return get_nlu_engine().analyze(text)


def classify_intent(text: str) -> IntentResult:
    """Quick intent classification."""
    return get_nlu_engine().classify_intent(text)


def extract_entities(text: str) -> List[Entity]:
    """Quick entity extraction."""
    return get_nlu_engine().extract_entities(text)


def analyze_sentiment(text: str) -> SentimentResult:
    """Quick sentiment analysis."""
    return get_nlu_engine().analyze_sentiment(text, None)
