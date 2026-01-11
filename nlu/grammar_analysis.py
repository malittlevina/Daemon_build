# nlu/grammar_analysis.py
# Grammar Analysis Module for Enhanced NLU

"""
Grammar Analysis Module

Provides:
- Sentence structure analysis
- Phrase detection (NP, VP, PP)
- Question analysis
- Command parsing
- Clause detection
- Grammatical error detection
- Text normalization
- Morphological analysis
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import re


class PhraseType(Enum):
    """Types of phrases."""
    NOUN_PHRASE = "NP"       # The big dog
    VERB_PHRASE = "VP"       # is running quickly
    PREP_PHRASE = "PP"       # in the house
    ADJ_PHRASE = "ADJP"      # very tall
    ADV_PHRASE = "ADVP"      # quite slowly
    CLAUSE = "S"             # Full clause


class SentenceType(Enum):
    """Types of sentences."""
    DECLARATIVE = "declarative"    # Statement
    INTERROGATIVE = "interrogative"  # Question
    IMPERATIVE = "imperative"        # Command
    EXCLAMATORY = "exclamatory"      # Exclamation


class QuestionType(Enum):
    """Types of questions."""
    YES_NO = "yes_no"           # Can you help?
    WH_WHAT = "wh_what"         # What is this?
    WH_WHO = "wh_who"           # Who did it?
    WH_WHERE = "wh_where"       # Where is it?
    WH_WHEN = "wh_when"         # When does it start?
    WH_WHY = "wh_why"           # Why is it happening?
    WH_HOW = "wh_how"           # How does it work?
    WH_WHICH = "wh_which"       # Which one?
    TAG = "tag"                 # It's nice, isn't it?
    CHOICE = "choice"           # Is it A or B?


@dataclass
class Phrase:
    """Detected phrase."""
    phrase_type: PhraseType
    text: str
    start: int
    end: int
    head: Optional[str] = None  # Main word
    modifiers: List[str] = field(default_factory=list)


@dataclass
class GrammarIssue:
    """Detected grammar issue."""
    issue_type: str
    text: str
    start: int
    end: int
    suggestion: Optional[str] = None
    severity: str = "warning"  # info, warning, error


@dataclass
class SentenceAnalysis:
    """Complete sentence analysis."""
    text: str
    sentence_type: SentenceType
    phrases: List[Phrase]
    subject: Optional[str] = None
    predicate: Optional[str] = None
    objects: List[str] = field(default_factory=list)
    question_type: Optional[QuestionType] = None
    is_passive: bool = False
    tense: str = "present"
    issues: List[GrammarIssue] = field(default_factory=list)


class GrammarAnalyzer:
    """
    Grammar analysis engine.
    
    Analyzes sentence structure, detects phrases,
    identifies grammatical patterns, and finds issues.
    """
    
    def __init__(self):
        # Question word patterns
        self.question_patterns = {
            QuestionType.WH_WHAT: r'^what\b',
            QuestionType.WH_WHO: r'^who(m)?\b',
            QuestionType.WH_WHERE: r'^where\b',
            QuestionType.WH_WHEN: r'^when\b',
            QuestionType.WH_WHY: r'^why\b',
            QuestionType.WH_HOW: r'^how\b',
            QuestionType.WH_WHICH: r'^which\b',
        }
        
        # Auxiliary verbs for question detection
        self.auxiliaries = {
            "am", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "having",
            "do", "does", "did",
            "can", "could", "may", "might", "must",
            "shall", "should", "will", "would"
        }
        
        # Common grammar mistake patterns
        self.grammar_patterns = [
            # Subject-verb agreement
            (r'\b(i)\s+(is|was|has)\b', "subject_verb", "Use 'I am/was/have'"),
            (r'\b(you|we|they)\s+(is|was|has)\b', "subject_verb", "Use plural verb form"),
            (r'\b(he|she|it)\s+(are|were|have)\b', "subject_verb", "Use singular verb form"),
            
            # Double negatives
            (r"\b(don't|doesn't|didn't|can't|won't)\s+\w+\s+(no|nothing|nobody|never)\b", 
             "double_negative", "Avoid double negatives"),
            
            # Article usage
            (r'\b(a)\s+([aeiou])', "article", "Use 'an' before vowel sounds"),
            (r'\b(an)\s+([^aeiou\s])', "article", "Use 'a' before consonant sounds"),
            
            # Common confusion
            (r"\b(your)\s+(welcome|right|wrong)\b", "confusion", "Use 'you're' (you are)"),
            (r"\b(there)\s+(going|coming|doing)\b", "confusion", "Use 'they're' (they are)"),
            (r"\b(its)\s+(a|the|my|your)\b", "confusion", "Use 'it's' (it is)"),
            
            # Missing punctuation
            (r'\b(i)\b(?!\s*(\'m|\'ll|\'ve|\'d|am|will|would|have|had))', "capitalization", 
             "Capitalize 'I'"),
        ]
        
        # Tense indicators
        self.tense_patterns = {
            "past": [r'\b(was|were|had|did)\b', r'\b\w+ed\b'],
            "present": [r'\b(am|is|are|do|does|have|has)\b'],
            "future": [r'\b(will|shall|going to)\b'],
            "perfect": [r'\b(have|has|had)\s+\w+ed\b', r'\b(have|has|had)\s+been\b'],
            "progressive": [r'\b(am|is|are|was|were)\s+\w+ing\b'],
        }
        
        # Passive voice patterns
        self.passive_patterns = [
            r'\b(am|is|are|was|were|be|been|being)\s+\w+ed\b',
            r'\b(am|is|are|was|were|be|been|being)\s+\w+en\b',
        ]
        
    def analyze(self, text: str) -> SentenceAnalysis:
        """
        Perform complete grammar analysis.
        
        Args:
            text: Input sentence
            
        Returns:
            SentenceAnalysis with all findings
        """
        # Determine sentence type
        sentence_type = self._get_sentence_type(text)
        
        # Detect question type if applicable
        question_type = None
        if sentence_type == SentenceType.INTERROGATIVE:
            question_type = self._get_question_type(text)
            
        # Extract phrases
        phrases = self._extract_phrases(text)
        
        # Identify subject and predicate
        subject, predicate = self._identify_subject_predicate(text)
        
        # Extract objects
        objects = self._extract_objects(text)
        
        # Detect passive voice
        is_passive = self._is_passive_voice(text)
        
        # Determine tense
        tense = self._detect_tense(text)
        
        # Check for grammar issues
        issues = self._check_grammar(text)
        
        return SentenceAnalysis(
            text=text,
            sentence_type=sentence_type,
            phrases=phrases,
            subject=subject,
            predicate=predicate,
            objects=objects,
            question_type=question_type,
            is_passive=is_passive,
            tense=tense,
            issues=issues
        )
        
    def _get_sentence_type(self, text: str) -> SentenceType:
        """Determine the type of sentence."""
        text_stripped = text.strip()
        
        # Check punctuation first
        if text_stripped.endswith('?'):
            return SentenceType.INTERROGATIVE
        if text_stripped.endswith('!'):
            return SentenceType.EXCLAMATORY
            
        # Check for question words at start
        text_lower = text_stripped.lower()
        for pattern in self.question_patterns.values():
            if re.match(pattern, text_lower):
                return SentenceType.INTERROGATIVE
                
        # Check for auxiliary at start (yes/no questions)
        first_word = text_lower.split()[0] if text_lower.split() else ""
        if first_word in self.auxiliaries:
            return SentenceType.INTERROGATIVE
            
        # Check for imperative (starts with verb, no subject)
        imperative_verbs = {
            "open", "close", "run", "start", "stop", "go", "come", "look",
            "tell", "show", "give", "take", "make", "get", "put", "let",
            "please", "help", "find", "search", "create", "delete", "save"
        }
        if first_word in imperative_verbs:
            return SentenceType.IMPERATIVE
            
        return SentenceType.DECLARATIVE
        
    def _get_question_type(self, text: str) -> Optional[QuestionType]:
        """Determine the type of question."""
        text_lower = text.lower().strip()
        
        # Check WH-questions
        for q_type, pattern in self.question_patterns.items():
            if re.match(pattern, text_lower):
                return q_type
                
        # Check for "or" in question (choice question)
        if ' or ' in text_lower and text.strip().endswith('?'):
            return QuestionType.CHOICE
            
        # Check for tag questions
        tag_pattern = r',\s*(is|are|was|were|do|does|did|can|could|will|would|has|have)(n\'?t)?\s+(it|he|she|they|we|you|I)\s*\?'
        if re.search(tag_pattern, text_lower):
            return QuestionType.TAG
            
        # Default to yes/no
        return QuestionType.YES_NO
        
    def _extract_phrases(self, text: str) -> List[Phrase]:
        """Extract noun, verb, and prepositional phrases."""
        phrases = []
        
        # Simple phrase patterns
        # Noun phrase: (Det)? (Adj)* Noun
        np_pattern = r'\b(the|a|an|this|that|my|your|his|her|its|our|their)?\s*(\w+ly\s+)?(\w+)\b'
        
        # Prepositional phrase: Prep + NP
        pp_pattern = r'\b(in|on|at|by|for|with|to|from|about|of|into|onto|through)\s+(\w+\s+)*\w+\b'
        
        # Find prepositional phrases
        for match in re.finditer(pp_pattern, text, re.IGNORECASE):
            phrases.append(Phrase(
                phrase_type=PhraseType.PREP_PHRASE,
                text=match.group(),
                start=match.start(),
                end=match.end(),
                head=match.group(1)  # Preposition as head
            ))
            
        return phrases
        
    def _identify_subject_predicate(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Identify subject and predicate of sentence."""
        words = text.split()
        if not words:
            return None, None
            
        text_lower = text.lower()
        
        # Simple heuristic: first noun/pronoun is subject
        pronouns = {"i", "you", "he", "she", "it", "we", "they", "who", "what"}
        
        subject = None
        predicate_start = 0
        
        for i, word in enumerate(words):
            word_clean = word.lower().strip('.,!?')
            if word_clean in pronouns:
                subject = word
                predicate_start = i + 1
                break
            # Check for noun (capitalize check or after determiner)
            if i > 0 and words[i-1].lower() in {"the", "a", "an", "this", "that"}:
                subject = word
                predicate_start = i + 1
                break
                
        if subject and predicate_start < len(words):
            predicate = ' '.join(words[predicate_start:])
        else:
            predicate = None
            
        return subject, predicate
        
    def _extract_objects(self, text: str) -> List[str]:
        """Extract objects (direct and indirect) from sentence."""
        objects = []
        
        # Look for nouns after verbs
        # This is a simplified approach
        words = text.split()
        
        verb_passed = False
        for word in words:
            word_clean = word.lower().strip('.,!?')
            
            # Check if it's a verb
            if word_clean.endswith(('ing', 'ed', 's')) or word_clean in self.auxiliaries:
                verb_passed = True
                continue
                
            # After verb, collect nouns
            if verb_passed:
                # Simple noun check
                if word[0].isupper() or word_clean not in self.auxiliaries:
                    if word_clean not in {"the", "a", "an", "to", "for", "with", "in", "on", "at"}:
                        objects.append(word)
                        
        return objects[:3]  # Limit to 3
        
    def _is_passive_voice(self, text: str) -> bool:
        """Check if sentence uses passive voice."""
        text_lower = text.lower()
        for pattern in self.passive_patterns:
            if re.search(pattern, text_lower):
                return True
        return False
        
    def _detect_tense(self, text: str) -> str:
        """Detect the primary tense of the sentence."""
        text_lower = text.lower()
        
        # Check each tense pattern
        tense_scores = {}
        for tense, patterns in self.tense_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1
            tense_scores[tense] = score
            
        # Return highest scoring tense
        if tense_scores:
            best_tense = max(tense_scores, key=tense_scores.get)
            if tense_scores[best_tense] > 0:
                return best_tense
                
        return "present"  # Default
        
    def _check_grammar(self, text: str) -> List[GrammarIssue]:
        """Check for common grammar issues."""
        issues = []
        
        for pattern, issue_type, suggestion in self.grammar_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                issues.append(GrammarIssue(
                    issue_type=issue_type,
                    text=match.group(),
                    start=match.start(),
                    end=match.end(),
                    suggestion=suggestion,
                    severity="warning"
                ))
                
        return issues


class TextNormalizer:
    """
    Text normalization for NLU preprocessing.
    
    Handles:
    - Contraction expansion
    - Number normalization
    - Spelling correction hints
    - Case normalization
    - Punctuation handling
    """
    
    def __init__(self):
        self.contractions = {
            # Common contractions
            "i'm": "i am",
            "i've": "i have",
            "i'll": "i will",
            "i'd": "i would",
            "you're": "you are",
            "you've": "you have",
            "you'll": "you will",
            "you'd": "you would",
            "he's": "he is",
            "he'll": "he will",
            "he'd": "he would",
            "she's": "she is",
            "she'll": "she will",
            "she'd": "she would",
            "it's": "it is",
            "it'll": "it will",
            "it'd": "it would",
            "we're": "we are",
            "we've": "we have",
            "we'll": "we will",
            "we'd": "we would",
            "they're": "they are",
            "they've": "they have",
            "they'll": "they will",
            "they'd": "they would",
            "that's": "that is",
            "that'll": "that will",
            "that'd": "that would",
            "who's": "who is",
            "who'll": "who will",
            "who'd": "who would",
            "what's": "what is",
            "what'll": "what will",
            "what'd": "what would",
            "where's": "where is",
            "where'll": "where will",
            "where'd": "where would",
            "when's": "when is",
            "when'll": "when will",
            "when'd": "when would",
            "why's": "why is",
            "why'll": "why will",
            "why'd": "why would",
            "how's": "how is",
            "how'll": "how will",
            "how'd": "how would",
            "there's": "there is",
            "there'll": "there will",
            "there'd": "there would",
            "here's": "here is",
            "here'll": "here will",
            
            # Negative contractions
            "isn't": "is not",
            "aren't": "are not",
            "wasn't": "was not",
            "weren't": "were not",
            "haven't": "have not",
            "hasn't": "has not",
            "hadn't": "had not",
            "don't": "do not",
            "doesn't": "does not",
            "didn't": "did not",
            "won't": "will not",
            "wouldn't": "would not",
            "can't": "cannot",
            "couldn't": "could not",
            "shouldn't": "should not",
            "mightn't": "might not",
            "mustn't": "must not",
            
            # Informal
            "gonna": "going to",
            "gotta": "got to",
            "wanna": "want to",
            "lemme": "let me",
            "gimme": "give me",
            "kinda": "kind of",
            "sorta": "sort of",
            "dunno": "do not know",
            "ain't": "is not",
            "y'all": "you all",
            "c'mon": "come on",
        }
        
        # Number words
        self.number_words = {
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
            "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
            "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
            "eighteen": "18", "nineteen": "19", "twenty": "20",
            "thirty": "30", "forty": "40", "fifty": "50",
            "sixty": "60", "seventy": "70", "eighty": "80", "ninety": "90",
            "hundred": "100", "thousand": "1000", "million": "1000000",
        }
        
        # Common misspellings
        self.common_misspellings = {
            "teh": "the",
            "taht": "that",
            "recieve": "receive",
            "occured": "occurred",
            "seperate": "separate",
            "definately": "definitely",
            "occassion": "occasion",
            "untill": "until",
            "wierd": "weird",
            "thier": "their",
            "freind": "friend",
            "beleive": "believe",
            "begining": "beginning",
            "existance": "existence",
            "independant": "independent",
            "refered": "referred",
            "succesful": "successful",
            "tommorow": "tomorrow",
            "accomodate": "accommodate",
            "arguement": "argument",
        }
        
    def normalize(self, text: str, 
                  expand_contractions: bool = True,
                  normalize_numbers: bool = False,
                  fix_spelling: bool = True,
                  lowercase: bool = False) -> str:
        """
        Normalize text with various options.
        
        Args:
            text: Input text
            expand_contractions: Expand contractions
            normalize_numbers: Convert number words to digits
            fix_spelling: Fix common misspellings
            lowercase: Convert to lowercase
            
        Returns:
            Normalized text
        """
        result = text
        
        if expand_contractions:
            result = self._expand_contractions(result)
            
        if fix_spelling:
            result = self._fix_spelling(result)
            
        if normalize_numbers:
            result = self._normalize_numbers(result)
            
        if lowercase:
            result = result.lower()
            
        # Clean up extra whitespace
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result
        
    def _expand_contractions(self, text: str) -> str:
        """Expand contractions to full forms."""
        result = text
        for contraction, expansion in self.contractions.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(contraction), re.IGNORECASE)
            result = pattern.sub(expansion, result)
        return result
        
    def _fix_spelling(self, text: str) -> str:
        """Fix common misspellings."""
        result = text
        for misspelling, correct in self.common_misspellings.items():
            pattern = re.compile(r'\b' + re.escape(misspelling) + r'\b', re.IGNORECASE)
            result = pattern.sub(correct, result)
        return result
        
    def _normalize_numbers(self, text: str) -> str:
        """Convert number words to digits."""
        result = text
        for word, digit in self.number_words.items():
            pattern = re.compile(r'\b' + word + r'\b', re.IGNORECASE)
            result = pattern.sub(digit, result)
        return result


class MorphologicalAnalyzer:
    """
    Morphological analysis for word structure.
    
    Analyzes:
    - Word roots
    - Prefixes and suffixes
    - Word formation patterns
    - Inflectional forms
    """
    
    def __init__(self):
        # Common prefixes with meanings
        self.prefixes = {
            "un": "not",
            "re": "again",
            "dis": "not, opposite",
            "pre": "before",
            "mis": "wrong",
            "over": "too much",
            "under": "too little",
            "out": "beyond",
            "sub": "under",
            "super": "above",
            "anti": "against",
            "auto": "self",
            "bi": "two",
            "co": "together",
            "counter": "against",
            "de": "remove",
            "en": "make",
            "ex": "out, former",
            "extra": "beyond",
            "hyper": "excessive",
            "im": "not",
            "in": "not, in",
            "inter": "between",
            "intra": "within",
            "macro": "large",
            "micro": "small",
            "mid": "middle",
            "multi": "many",
            "non": "not",
            "poly": "many",
            "post": "after",
            "pro": "for, forward",
            "semi": "half",
            "trans": "across",
            "tri": "three",
            "ultra": "beyond",
        }
        
        # Common suffixes with meanings
        self.suffixes = {
            # Noun suffixes
            "tion": ("noun", "action/state"),
            "sion": ("noun", "action/state"),
            "ment": ("noun", "action/result"),
            "ness": ("noun", "quality"),
            "ity": ("noun", "quality"),
            "er": ("noun", "one who"),
            "or": ("noun", "one who"),
            "ist": ("noun", "one who"),
            "ism": ("noun", "belief/practice"),
            "dom": ("noun", "state/realm"),
            "ship": ("noun", "state/skill"),
            "hood": ("noun", "state"),
            "age": ("noun", "action/result"),
            
            # Verb suffixes
            "ize": ("verb", "make"),
            "ise": ("verb", "make"),
            "ify": ("verb", "make"),
            "ate": ("verb", "make"),
            "en": ("verb", "make"),
            
            # Adjective suffixes
            "able": ("adjective", "capable of"),
            "ible": ("adjective", "capable of"),
            "ful": ("adjective", "full of"),
            "less": ("adjective", "without"),
            "ous": ("adjective", "having quality"),
            "ive": ("adjective", "having quality"),
            "al": ("adjective", "relating to"),
            "ic": ("adjective", "relating to"),
            "ical": ("adjective", "relating to"),
            "ish": ("adjective", "somewhat"),
            "ly": ("adjective/adverb", "manner"),
            
            # Adverb suffixes
            "ward": ("adverb", "direction"),
            "wise": ("adverb", "manner"),
        }
        
    def analyze(self, word: str) -> Dict[str, Any]:
        """
        Analyze word morphology.
        
        Args:
            word: Word to analyze
            
        Returns:
            Dict with morphological analysis
        """
        word_lower = word.lower()
        
        result = {
            "word": word,
            "root": word_lower,
            "prefixes": [],
            "suffixes": [],
            "derived_pos": None,
            "is_compound": False
        }
        
        # Check for prefixes
        for prefix, meaning in self.prefixes.items():
            if word_lower.startswith(prefix) and len(word_lower) > len(prefix) + 2:
                result["prefixes"].append({
                    "prefix": prefix,
                    "meaning": meaning
                })
                result["root"] = word_lower[len(prefix):]
                break
                
        # Check for suffixes
        for suffix, (pos, meaning) in self.suffixes.items():
            if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 2:
                result["suffixes"].append({
                    "suffix": suffix,
                    "pos": pos,
                    "meaning": meaning
                })
                result["derived_pos"] = pos
                # Update root
                root_end = len(word_lower) - len(suffix)
                result["root"] = result["root"][:root_end] if len(result["root"]) > root_end else result["root"]
                break
                
        # Check for compound words (simple heuristic)
        if len(word_lower) > 8 and word_lower not in {"something", "everything", "anything"}:
            # Look for common compound patterns
            compound_parts = self._find_compound_parts(word_lower)
            if compound_parts:
                result["is_compound"] = True
                result["compound_parts"] = compound_parts
                
        return result
        
    def _find_compound_parts(self, word: str) -> Optional[List[str]]:
        """Try to identify parts of a compound word."""
        # Common compound word parts
        common_parts = {
            "any", "every", "some", "no", "thing", "one", "body", "where",
            "book", "case", "day", "door", "foot", "hand", "home", "land",
            "light", "line", "man", "night", "out", "over", "room", "side",
            "time", "under", "up", "water", "way", "week", "work", "world"
        }
        
        for i in range(3, len(word) - 2):
            part1 = word[:i]
            part2 = word[i:]
            if part1 in common_parts and part2 in common_parts:
                return [part1, part2]
                
        return None
        
    def get_word_family(self, root: str) -> Dict[str, List[str]]:
        """
        Generate word family from a root.
        
        Args:
            root: Word root
            
        Returns:
            Dict with different forms
        """
        family = {
            "nouns": [],
            "verbs": [],
            "adjectives": [],
            "adverbs": []
        }
        
        # Generate noun forms
        for suffix, (pos, _) in self.suffixes.items():
            if pos == "noun":
                family["nouns"].append(root + suffix)
                
        # Generate verb forms
        for suffix, (pos, _) in self.suffixes.items():
            if pos == "verb":
                family["verbs"].append(root + suffix)
                
        # Generate adjective forms
        for suffix, (pos, _) in self.suffixes.items():
            if "adjective" in pos:
                family["adjectives"].append(root + suffix)
                
        # Generate adverb forms (typically from adjectives)
        family["adverbs"].append(root + "ly")
        
        return family


# =============================================================================
# SINGLETON & HELPER FUNCTIONS
# =============================================================================

_grammar_analyzer: Optional[GrammarAnalyzer] = None
_text_normalizer: Optional[TextNormalizer] = None
_morphological_analyzer: Optional[MorphologicalAnalyzer] = None


def get_grammar_analyzer() -> GrammarAnalyzer:
    """Get the global grammar analyzer instance."""
    global _grammar_analyzer
    if _grammar_analyzer is None:
        _grammar_analyzer = GrammarAnalyzer()
    return _grammar_analyzer


def get_text_normalizer() -> TextNormalizer:
    """Get the global text normalizer instance."""
    global _text_normalizer
    if _text_normalizer is None:
        _text_normalizer = TextNormalizer()
    return _text_normalizer


def get_morphological_analyzer() -> MorphologicalAnalyzer:
    """Get the global morphological analyzer instance."""
    global _morphological_analyzer
    if _morphological_analyzer is None:
        _morphological_analyzer = MorphologicalAnalyzer()
    return _morphological_analyzer


def analyze_grammar(text: str) -> SentenceAnalysis:
    """Quick grammar analysis."""
    return get_grammar_analyzer().analyze(text)


def normalize_text(text: str, **kwargs) -> str:
    """Quick text normalization."""
    return get_text_normalizer().normalize(text, **kwargs)


def analyze_morphology(word: str) -> Dict[str, Any]:
    """Quick morphological analysis."""
    return get_morphological_analyzer().analyze(word)
