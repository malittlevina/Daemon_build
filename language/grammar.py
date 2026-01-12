# language/grammar.py
"""
Grammar System
==============
Handles grammatical analysis and sentence structure:
- Sentence parsing and structure analysis
- Grammar rule application
- Phrase detection (noun phrases, verb phrases, etc.)
- Grammatical correctness checking
"""

import re
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

from .vocabulary import Vocabulary, PartOfSpeech, Word


class PhraseType(Enum):
    """Types of grammatical phrases."""
    NOUN_PHRASE = "NP"           # The big dog
    VERB_PHRASE = "VP"           # runs quickly
    ADJECTIVE_PHRASE = "ADJP"    # very happy
    ADVERB_PHRASE = "ADVP"       # quite slowly
    PREPOSITIONAL_PHRASE = "PP"  # in the house
    CLAUSE = "CL"                # when it rains
    SENTENCE = "S"               # Complete sentence


class SentenceType(Enum):
    """Types of sentences."""
    DECLARATIVE = "declarative"   # Statements
    INTERROGATIVE = "interrogative"  # Questions
    IMPERATIVE = "imperative"     # Commands
    EXCLAMATORY = "exclamatory"   # Exclamations


@dataclass
class Token:
    """A token (word) with grammatical annotation."""
    text: str
    pos: PartOfSpeech
    lemma: Optional[str] = None  # Base form
    index: int = 0
    
    def __str__(self):
        return f"{self.text}/{self.pos.value}"


@dataclass
class Phrase:
    """A grammatical phrase."""
    phrase_type: PhraseType
    tokens: List[Token]
    head_index: int = 0  # Index of the head word
    
    @property
    def text(self) -> str:
        return " ".join(t.text for t in self.tokens)
    
    @property
    def head(self) -> Optional[Token]:
        if 0 <= self.head_index < len(self.tokens):
            return self.tokens[self.head_index]
        return None
    
    def __str__(self):
        return f"[{self.phrase_type.value} {self.text}]"


@dataclass
class ParsedSentence:
    """A parsed sentence with grammatical structure."""
    original: str
    tokens: List[Token]
    phrases: List[Phrase]
    sentence_type: SentenceType
    subject: Optional[Phrase] = None
    predicate: Optional[Phrase] = None
    objects: List[Phrase] = field(default_factory=list)
    
    def __str__(self):
        return f"Sentence({self.sentence_type.value}): {self.original}"
    
    def structure_str(self) -> str:
        """Get a string representation of the structure."""
        parts = []
        if self.subject:
            parts.append(f"Subject: {self.subject}")
        if self.predicate:
            parts.append(f"Predicate: {self.predicate}")
        for i, obj in enumerate(self.objects):
            parts.append(f"Object{i+1}: {obj}")
        return "\n".join(parts)


@dataclass
class GrammarRule:
    """A grammar rule for validation or transformation."""
    name: str
    pattern: str  # Regex or pattern
    description: str
    category: str = "general"  # syntax, punctuation, style
    severity: str = "suggestion"  # error, warning, suggestion
    
    def check(self, text: str) -> Optional[str]:
        """Check if text matches rule (returns message if violation found)."""
        if re.search(self.pattern, text, re.IGNORECASE):
            return self.description
        return None


class SentenceParser:
    """
    Parses sentences into grammatical components.
    Uses simple rule-based parsing with vocabulary integration.
    """
    
    def __init__(self, vocabulary: Optional[Vocabulary] = None):
        self.vocabulary = vocabulary or Vocabulary()
        
        # Common patterns
        self.question_starters = ['what', 'who', 'where', 'when', 'why', 'how', 'can', 'could', 'would', 'should', 'is', 'are', 'do', 'does', 'did', 'will']
        self.command_starters = ['please', 'do', 'don\'t', 'let', 'make', 'help', 'show', 'tell', 'give', 'take', 'run', 'stop', 'start', 'open', 'close']
        
        # Determiners, prepositions, etc.
        self.determiners = ['the', 'a', 'an', 'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'some', 'any', 'no', 'every', 'all']
        self.prepositions = ['in', 'on', 'at', 'to', 'for', 'with', 'by', 'from', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'over']
        self.conjunctions = ['and', 'but', 'or', 'nor', 'yet', 'so', 'because', 'although', 'while', 'if', 'when', 'unless', 'until']
        self.auxiliaries = ['is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can']
        self.pronouns = ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'themselves']
    
    def tokenize(self, text: str) -> List[Token]:
        """Tokenize text into annotated tokens."""
        # Simple tokenization
        words = re.findall(r'\b\w+\b', text.lower())
        tokens = []
        
        for i, word in enumerate(words):
            pos = self._get_pos(word)
            lemma = self._get_lemma(word)
            tokens.append(Token(text=word, pos=pos, lemma=lemma, index=i))
        
        return tokens
    
    def _get_pos(self, word: str) -> PartOfSpeech:
        """Get part of speech for a word."""
        word_lower = word.lower()
        
        # Check vocabulary first
        vocab_word = self.vocabulary.get(word_lower)
        if vocab_word:
            return vocab_word.primary_pos
        
        # Rule-based fallback
        if word_lower in self.determiners:
            return PartOfSpeech.DETERMINER
        if word_lower in self.prepositions:
            return PartOfSpeech.PREPOSITION
        if word_lower in self.conjunctions:
            return PartOfSpeech.CONJUNCTION
        if word_lower in self.auxiliaries:
            return PartOfSpeech.AUXILIARY
        if word_lower in self.pronouns:
            return PartOfSpeech.PRONOUN
        
        # Suffix-based guessing
        if word.endswith('ly'):
            return PartOfSpeech.ADVERB
        if word.endswith(('ing', 'ed', 's', 'es')) and len(word) > 3:
            return PartOfSpeech.VERB
        if word.endswith(('tion', 'ness', 'ment', 'ity')):
            return PartOfSpeech.NOUN
        if word.endswith(('ful', 'less', 'ous', 'ive', 'able', 'ible')):
            return PartOfSpeech.ADJECTIVE
        
        return PartOfSpeech.UNKNOWN
    
    def _get_lemma(self, word: str) -> str:
        """Get base form (lemma) of a word."""
        # Simple lemmatization rules
        if word.endswith('ing') and len(word) > 4:
            if word[-4] == word[-5]:  # running -> run
                return word[:-4]
            return word[:-3]
        if word.endswith('ed') and len(word) > 3:
            return word[:-2]
        if word.endswith('s') and not word.endswith('ss') and len(word) > 2:
            return word[:-1]
        if word.endswith('es') and len(word) > 3:
            return word[:-2]
        return word
    
    def parse(self, text: str) -> ParsedSentence:
        """Parse a sentence into grammatical structure."""
        tokens = self.tokenize(text)
        
        # Determine sentence type
        sentence_type = self._determine_sentence_type(text, tokens)
        
        # Find phrases
        phrases = self._find_phrases(tokens)
        
        # Identify subject and predicate
        subject, predicate, objects = self._find_spo(tokens, phrases)
        
        return ParsedSentence(
            original=text,
            tokens=tokens,
            phrases=phrases,
            sentence_type=sentence_type,
            subject=subject,
            predicate=predicate,
            objects=objects
        )
    
    def _determine_sentence_type(self, text: str, tokens: List[Token]) -> SentenceType:
        """Determine the type of sentence."""
        text_stripped = text.strip()
        
        if text_stripped.endswith('?'):
            return SentenceType.INTERROGATIVE
        
        if text_stripped.endswith('!'):
            return SentenceType.EXCLAMATORY
        
        if tokens:
            first_word = tokens[0].text.lower()
            if first_word in self.question_starters:
                return SentenceType.INTERROGATIVE
            if first_word in self.command_starters or tokens[0].pos == PartOfSpeech.VERB:
                return SentenceType.IMPERATIVE
        
        return SentenceType.DECLARATIVE
    
    def _find_phrases(self, tokens: List[Token]) -> List[Phrase]:
        """Find grammatical phrases in the token sequence."""
        phrases = []
        i = 0
        
        while i < len(tokens):
            # Try to find noun phrase
            np, end = self._find_noun_phrase(tokens, i)
            if np:
                phrases.append(np)
                i = end
                continue
            
            # Try to find verb phrase
            vp, end = self._find_verb_phrase(tokens, i)
            if vp:
                phrases.append(vp)
                i = end
                continue
            
            # Try to find prepositional phrase
            pp, end = self._find_prep_phrase(tokens, i)
            if pp:
                phrases.append(pp)
                i = end
                continue
            
            i += 1
        
        return phrases
    
    def _find_noun_phrase(self, tokens: List[Token], start: int) -> Tuple[Optional[Phrase], int]:
        """Find a noun phrase starting at position."""
        if start >= len(tokens):
            return None, start
        
        phrase_tokens = []
        head_index = 0
        i = start
        
        # Determiner
        if i < len(tokens) and tokens[i].pos == PartOfSpeech.DETERMINER:
            phrase_tokens.append(tokens[i])
            i += 1
        
        # Adjectives
        while i < len(tokens) and tokens[i].pos == PartOfSpeech.ADJECTIVE:
            phrase_tokens.append(tokens[i])
            i += 1
        
        # Noun (head)
        if i < len(tokens) and tokens[i].pos in [PartOfSpeech.NOUN, PartOfSpeech.PRONOUN, PartOfSpeech.UNKNOWN]:
            head_index = len(phrase_tokens)
            phrase_tokens.append(tokens[i])
            i += 1
            
            if phrase_tokens:
                return Phrase(
                    phrase_type=PhraseType.NOUN_PHRASE,
                    tokens=phrase_tokens,
                    head_index=head_index
                ), i
        
        return None, start
    
    def _find_verb_phrase(self, tokens: List[Token], start: int) -> Tuple[Optional[Phrase], int]:
        """Find a verb phrase starting at position."""
        if start >= len(tokens):
            return None, start
        
        phrase_tokens = []
        head_index = 0
        i = start
        
        # Auxiliaries
        while i < len(tokens) and tokens[i].pos == PartOfSpeech.AUXILIARY:
            phrase_tokens.append(tokens[i])
            i += 1
        
        # Main verb
        if i < len(tokens) and tokens[i].pos == PartOfSpeech.VERB:
            head_index = len(phrase_tokens)
            phrase_tokens.append(tokens[i])
            i += 1
            
            # Adverbs
            while i < len(tokens) and tokens[i].pos == PartOfSpeech.ADVERB:
                phrase_tokens.append(tokens[i])
                i += 1
            
            if phrase_tokens:
                return Phrase(
                    phrase_type=PhraseType.VERB_PHRASE,
                    tokens=phrase_tokens,
                    head_index=head_index
                ), i
        
        return None, start
    
    def _find_prep_phrase(self, tokens: List[Token], start: int) -> Tuple[Optional[Phrase], int]:
        """Find a prepositional phrase."""
        if start >= len(tokens):
            return None, start
        
        if tokens[start].pos != PartOfSpeech.PREPOSITION:
            return None, start
        
        phrase_tokens = [tokens[start]]
        i = start + 1
        
        # Find the noun phrase that follows
        np, end = self._find_noun_phrase(tokens, i)
        if np:
            phrase_tokens.extend(np.tokens)
            return Phrase(
                phrase_type=PhraseType.PREPOSITIONAL_PHRASE,
                tokens=phrase_tokens,
                head_index=0
            ), end
        
        return None, start
    
    def _find_spo(self, tokens: List[Token], phrases: List[Phrase]) -> Tuple[Optional[Phrase], Optional[Phrase], List[Phrase]]:
        """Find subject, predicate, and objects."""
        subject = None
        predicate = None
        objects = []
        
        found_verb = False
        
        for phrase in phrases:
            if phrase.phrase_type == PhraseType.NOUN_PHRASE:
                if not found_verb and subject is None:
                    subject = phrase
                elif found_verb:
                    objects.append(phrase)
            elif phrase.phrase_type == PhraseType.VERB_PHRASE:
                predicate = phrase
                found_verb = True
        
        return subject, predicate, objects


class Grammar:
    """
    Grammar system for the daemon.
    Provides parsing, validation, and grammatical analysis.
    """
    
    def __init__(self, vocabulary: Optional[Vocabulary] = None):
        self.vocabulary = vocabulary or Vocabulary()
        self.parser = SentenceParser(self.vocabulary)
        self.rules: List[GrammarRule] = []
        
        self._load_default_rules()
        print("[Grammar] Initialized.")
    
    def _load_default_rules(self):
        """Load default grammar rules."""
        self.rules = [
            GrammarRule(
                name="double_negative",
                pattern=r"\b(don't|doesn't|didn't|won't|can't|couldn't|shouldn't|wouldn't)\s+\w+\s+(no|none|nothing|nobody|nowhere|never)\b",
                description="Avoid double negatives",
                category="syntax",
                severity="warning"
            ),
            GrammarRule(
                name="subject_verb_agreement",
                pattern=r"\b(I|we|they)\s+(is|was)\b|\b(he|she|it)\s+(are|were)\b",
                description="Subject-verb agreement error",
                category="syntax",
                severity="error"
            ),
            GrammarRule(
                name="repeated_word",
                pattern=r"\b(\w+)\s+\1\b",
                description="Word repeated consecutively",
                category="style",
                severity="suggestion"
            ),
            GrammarRule(
                name="missing_article",
                pattern=r"\b(is|was|are|were)\s+(very|quite|really)\s+(big|small|good|bad|important)\s+\w+\b",
                description="Consider adding an article",
                category="style",
                severity="suggestion"
            ),
        ]
    
    def parse(self, text: str) -> ParsedSentence:
        """Parse a sentence."""
        return self.parser.parse(text)
    
    def check(self, text: str) -> List[Dict[str, str]]:
        """Check text for grammar issues."""
        issues = []
        
        for rule in self.rules:
            message = rule.check(text)
            if message:
                issues.append({
                    'rule': rule.name,
                    'message': message,
                    'category': rule.category,
                    'severity': rule.severity
                })
        
        return issues
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Full grammatical analysis of text."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        parsed_sentences = [self.parse(s) for s in sentences]
        issues = self.check(text)
        
        # Collect statistics
        sentence_types = {}
        phrase_counts = {pt: 0 for pt in PhraseType}
        
        for ps in parsed_sentences:
            st = ps.sentence_type.value
            sentence_types[st] = sentence_types.get(st, 0) + 1
            
            for phrase in ps.phrases:
                phrase_counts[phrase.phrase_type] += 1
        
        return {
            'text': text,
            'sentence_count': len(parsed_sentences),
            'sentence_types': sentence_types,
            'phrase_counts': {k.value: v for k, v in phrase_counts.items() if v > 0},
            'issues': issues,
            'parsed_sentences': parsed_sentences
        }
    
    def get_sentence_structure(self, text: str) -> str:
        """Get a human-readable sentence structure."""
        parsed = self.parse(text)
        
        lines = [
            f"Sentence Type: {parsed.sentence_type.value}",
            parsed.structure_str(),
            "",
            "Phrases found:",
        ]
        
        for phrase in parsed.phrases:
            lines.append(f"  {phrase}")
        
        return "\n".join(lines)
