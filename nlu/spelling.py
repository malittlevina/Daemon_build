# nlu/spelling.py
# Spelling Correction Module

"""
Spelling Correction Module

Provides:
- Levenshtein distance calculation
- Spelling suggestions
- Auto-correction
- Phonetic matching (Soundex)
- Common typo detection
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class SpellingSuggestion:
    """Spelling correction suggestion."""
    original: str
    suggestion: str
    distance: int
    confidence: float
    

class SpellingCorrector:
    """
    Spelling correction engine using multiple algorithms.
    
    Uses:
    - Levenshtein distance for edit distance
    - Phonetic matching for sound-alike words
    - Frequency-based ranking
    """
    
    def __init__(self):
        self.dictionary: Set[str] = set()
        self.word_frequencies: Dict[str, int] = {}
        
        # Common keyboard typos (adjacent keys)
        self.keyboard_adjacent = {
            'a': 'qwsz', 'b': 'vghn', 'c': 'xdfv', 'd': 'erfcxs',
            'e': 'wrsdf', 'f': 'rtgvcd', 'g': 'tyhbvf', 'h': 'yujnbg',
            'i': 'uojkl', 'j': 'uikmnh', 'k': 'iolmj', 'l': 'opk',
            'm': 'njk', 'n': 'bhjm', 'o': 'iplk', 'p': 'ol',
            'q': 'wa', 'r': 'edft', 's': 'awedxz', 't': 'rfgy',
            'u': 'yhji', 'v': 'cfgb', 'w': 'qase', 'x': 'zsdc',
            'y': 'tghu', 'z': 'asx'
        }
        
        # Common misspellings
        self.common_misspellings = {
            # Commonly confused
            "accomodate": "accommodate",
            "acheive": "achieve",
            "accross": "across",
            "agressive": "aggressive",
            "apparant": "apparent",
            "arguement": "argument",
            "begining": "beginning",
            "beleive": "believe",
            "calender": "calendar",
            "catagory": "category",
            "cemetary": "cemetery",
            "commited": "committed",
            "concious": "conscious",
            "definately": "definitely",
            "dissapoint": "disappoint",
            "embarass": "embarrass",
            "enviroment": "environment",
            "exagerate": "exaggerate",
            "existance": "existence",
            "experiance": "experience",
            "foriegn": "foreign",
            "freind": "friend",
            "goverment": "government",
            "grammer": "grammar",
            "gaurd": "guard",
            "happend": "happened",
            "harrass": "harass",
            "heighth": "height",
            "humourous": "humorous",
            "independant": "independent",
            "innoculate": "inoculate",
            "intresting": "interesting",
            "knowlege": "knowledge",
            "libary": "library",
            "liason": "liaison",
            "maintenence": "maintenance",
            "millenium": "millennium",
            "mispell": "misspell",
            "neccessary": "necessary",
            "noticable": "noticeable",
            "occassion": "occasion",
            "occured": "occurred",
            "occurence": "occurrence",
            "paralell": "parallel",
            "persistant": "persistent",
            "posession": "possession",
            "prefered": "preferred",
            "priviledge": "privilege",
            "pronounciation": "pronunciation",
            "publically": "publicly",
            "realy": "really",
            "recieve": "receive",
            "refered": "referred",
            "relevent": "relevant",
            "religous": "religious",
            "repetition": "repetition",
            "resistence": "resistance",
            "rythm": "rhythm",
            "seperate": "separate",
            "sieze": "seize",
            "similiar": "similar",
            "succesful": "successful",
            "suprise": "surprise",
            "temperture": "temperature",
            "thier": "their",
            "tommorow": "tomorrow",
            "truely": "truly",
            "untill": "until",
            "usualy": "usually",
            "vaccuum": "vacuum",
            "wierd": "weird",
            "wellfare": "welfare",
            "wether": "whether",
            "writting": "writing",
            
            # Common typos
            "teh": "the",
            "taht": "that",
            "adn": "and",
            "waht": "what",
            "hte": "the",
            "nto": "not",
            "ot": "to",
            "fo": "of",
            "ti": "it",
            "si": "is",
            "nad": "and",
            "hav": "have",
            "woudl": "would",
            "shoudl": "should",
            "coudl": "could",
            "dont": "don't",
            "cant": "can't",
            "wont": "won't",
            "didnt": "didn't",
            "doesnt": "doesn't",
            "isnt": "isn't",
            "wasnt": "wasn't",
            "werent": "weren't",
            "havent": "haven't",
            "hasnt": "hasn't",
            "hadnt": "hadn't",
            "wouldnt": "wouldn't",
            "shouldnt": "shouldn't",
            "couldnt": "couldn't",
            "im": "I'm",
            "youre": "you're",
            "theyre": "they're",
            "thats": "that's",
            "whats": "what's",
            "heres": "here's",
            "theres": "there's",
            "whos": "who's",
            "its": "it's",  # Context dependent
        }
        
        # Load basic dictionary
        self._load_basic_dictionary()
        
    def _load_basic_dictionary(self):
        """Load a basic English dictionary."""
        # Add common words
        common_words = [
            # Articles and prepositions
            "a", "an", "the", "in", "on", "at", "to", "for", "of", "with",
            "by", "from", "about", "into", "through", "during", "before",
            "after", "above", "below", "between", "under", "over",
            
            # Pronouns
            "i", "you", "he", "she", "it", "we", "they", "me", "him", "her",
            "us", "them", "my", "your", "his", "its", "our", "their",
            "myself", "yourself", "himself", "herself", "itself",
            
            # Common verbs
            "be", "am", "is", "are", "was", "were", "been", "being",
            "have", "has", "had", "having", "do", "does", "did", "doing",
            "go", "goes", "went", "gone", "going", "come", "comes", "came",
            "make", "makes", "made", "making", "take", "takes", "took",
            "get", "gets", "got", "getting", "give", "gives", "gave",
            "see", "sees", "saw", "seen", "know", "knows", "knew", "known",
            "think", "thinks", "thought", "want", "wants", "wanted",
            "use", "uses", "used", "find", "finds", "found",
            "tell", "tells", "told", "ask", "asks", "asked",
            "work", "works", "worked", "try", "tries", "tried",
            "need", "needs", "needed", "feel", "feels", "felt",
            "become", "becomes", "became", "leave", "leaves", "left",
            "put", "puts", "call", "calls", "called",
            "keep", "keeps", "kept", "let", "lets",
            "begin", "begins", "began", "seem", "seems", "seemed",
            "help", "helps", "helped", "show", "shows", "showed",
            "hear", "hears", "heard", "play", "plays", "played",
            "run", "runs", "ran", "move", "moves", "moved",
            "live", "lives", "lived", "believe", "believes", "believed",
            "hold", "holds", "held", "bring", "brings", "brought",
            "write", "writes", "wrote", "written",
            "read", "reads", "stand", "stands", "stood",
            "learn", "learns", "learned", "change", "changes", "changed",
            "follow", "follows", "followed", "stop", "stops", "stopped",
            "create", "creates", "created", "speak", "speaks", "spoke",
            "allow", "allows", "allowed", "add", "adds", "added",
            "spend", "spends", "spent", "grow", "grows", "grew",
            "open", "opens", "opened", "walk", "walks", "walked",
            "win", "wins", "won", "offer", "offers", "offered",
            "remember", "remembers", "remembered", "love", "loves", "loved",
            "consider", "considers", "considered", "appear", "appears", "appeared",
            "buy", "buys", "bought", "wait", "waits", "waited",
            "serve", "serves", "served", "die", "dies", "died",
            "send", "sends", "sent", "expect", "expects", "expected",
            "build", "builds", "built", "stay", "stays", "stayed",
            "fall", "falls", "fell", "cut", "cuts",
            "reach", "reaches", "reached", "kill", "kills", "killed",
            "remain", "remains", "remained", "suggest", "suggests", "suggested",
            "raise", "raises", "raised", "pass", "passes", "passed",
            "sell", "sells", "sold", "require", "requires", "required",
            "report", "reports", "reported", "decide", "decides", "decided",
            "pull", "pulls", "pulled",
            
            # Common nouns
            "time", "year", "people", "way", "day", "man", "thing", "woman",
            "life", "child", "world", "school", "state", "family", "student",
            "group", "country", "problem", "hand", "part", "place", "case",
            "week", "company", "system", "program", "question", "work", "government",
            "number", "night", "point", "home", "water", "room", "mother",
            "area", "money", "story", "fact", "month", "lot", "right", "study",
            "book", "eye", "job", "word", "business", "issue", "side", "kind",
            "head", "house", "service", "friend", "father", "power", "hour",
            "game", "line", "end", "member", "law", "car", "city", "community",
            "name", "president", "team", "minute", "idea", "kid", "body",
            "information", "back", "parent", "face", "others", "level", "office",
            "door", "health", "person", "art", "war", "history", "party",
            "result", "change", "morning", "reason", "research", "girl", "guy",
            "moment", "air", "teacher", "force", "education",
            
            # Common adjectives
            "good", "new", "first", "last", "long", "great", "little", "own",
            "other", "old", "right", "big", "high", "different", "small",
            "large", "next", "early", "young", "important", "few", "public",
            "bad", "same", "able", "human", "local", "sure", "free", "better",
            "true", "whole", "special", "hard", "real", "best", "possible",
            "full", "low", "late", "general", "specific", "strong", "happy",
            "serious", "ready", "simple", "left", "past", "current", "nice",
            "political", "natural", "open", "available", "likely", "short",
            "single", "personal", "international", "national", "major",
            "economic", "hot", "cold", "wrong", "clear", "easy", "quick",
            "fast", "slow", "beautiful", "black", "white", "red", "blue",
            
            # Common adverbs
            "not", "just", "more", "also", "very", "often", "however", "too",
            "usually", "really", "early", "never", "always", "sometimes",
            "together", "likely", "simply", "generally", "instead", "actually",
            "already", "especially", "ever", "quickly", "probably", "certainly",
            "finally", "almost", "perhaps", "definitely", "exactly", "recently",
            "clearly", "still", "well", "now", "then", "here", "there", "today",
            "where", "when", "only", "even", "back", "yet", "again", "once",
            
            # Technology
            "computer", "internet", "website", "software", "data", "email",
            "online", "digital", "technology", "network", "system", "program",
            "application", "file", "download", "upload", "search", "password",
            
            # Time
            "today", "tomorrow", "yesterday", "morning", "afternoon", "evening",
            "night", "monday", "tuesday", "wednesday", "thursday", "friday",
            "saturday", "sunday", "january", "february", "march", "april",
            "may", "june", "july", "august", "september", "october", "november",
            "december",
        ]
        
        for word in common_words:
            self.dictionary.add(word.lower())
            self.word_frequencies[word.lower()] = 1000  # Default frequency
            
        # Add misspelling corrections to dictionary
        for correct in self.common_misspellings.values():
            self.dictionary.add(correct.lower())
            
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate Levenshtein (edit) distance between two strings.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Minimum number of edits needed
        """
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
            
        if len(s2) == 0:
            return len(s1)
            
        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Insertions, deletions, substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]
        
    def damerau_levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate Damerau-Levenshtein distance (includes transpositions).
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Minimum number of edits needed
        """
        len1, len2 = len(s1), len(s2)
        
        # Create distance matrix
        d = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            d[i][0] = i
        for j in range(len2 + 1):
            d[0][j] = j
            
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                
                d[i][j] = min(
                    d[i-1][j] + 1,      # Deletion
                    d[i][j-1] + 1,      # Insertion
                    d[i-1][j-1] + cost  # Substitution
                )
                
                # Transposition
                if i > 1 and j > 1 and s1[i-1] == s2[j-2] and s1[i-2] == s2[j-1]:
                    d[i][j] = min(d[i][j], d[i-2][j-2] + cost)
                    
        return d[len1][len2]
        
    def soundex(self, word: str) -> str:
        """
        Calculate Soundex code for phonetic matching.
        
        Args:
            word: Input word
            
        Returns:
            4-character Soundex code
        """
        if not word:
            return "0000"
            
        word = word.upper()
        
        # Soundex coding table
        codes = {
            'B': '1', 'F': '1', 'P': '1', 'V': '1',
            'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
            'D': '3', 'T': '3',
            'L': '4',
            'M': '5', 'N': '5',
            'R': '6'
        }
        
        # Keep first letter
        result = word[0]
        prev_code = codes.get(word[0], '0')
        
        for char in word[1:]:
            code = codes.get(char, '0')
            if code != '0' and code != prev_code:
                result += code
            prev_code = code if code != '0' else prev_code
            
            if len(result) >= 4:
                break
                
        # Pad with zeros
        return (result + "0000")[:4]
        
    def add_word(self, word: str, frequency: int = 1):
        """Add a word to the dictionary."""
        word_lower = word.lower()
        self.dictionary.add(word_lower)
        self.word_frequencies[word_lower] = self.word_frequencies.get(word_lower, 0) + frequency
        
    def is_correct(self, word: str) -> bool:
        """Check if a word is spelled correctly."""
        return word.lower() in self.dictionary
        
    def suggest(self, word: str, max_distance: int = 2, n: int = 5) -> List[SpellingSuggestion]:
        """
        Get spelling suggestions for a word.
        
        Args:
            word: Potentially misspelled word
            max_distance: Maximum edit distance
            n: Number of suggestions
            
        Returns:
            List of SpellingSuggestion objects
        """
        word_lower = word.lower()
        
        # Check if word is correct
        if word_lower in self.dictionary:
            return []
            
        # Check common misspellings first
        if word_lower in self.common_misspellings:
            correct = self.common_misspellings[word_lower]
            return [SpellingSuggestion(
                original=word,
                suggestion=correct,
                distance=1,
                confidence=0.95
            )]
            
        suggestions = []
        word_soundex = self.soundex(word)
        
        for dict_word in self.dictionary:
            distance = self.damerau_levenshtein_distance(word_lower, dict_word)
            
            if distance <= max_distance:
                # Calculate confidence based on distance and frequency
                freq = self.word_frequencies.get(dict_word, 1)
                
                # Boost for same soundex (phonetic match)
                soundex_boost = 0.2 if self.soundex(dict_word) == word_soundex else 0
                
                # Boost for same first letter
                first_letter_boost = 0.1 if word_lower[0] == dict_word[0] else 0
                
                # Boost for similar length
                length_diff = abs(len(word_lower) - len(dict_word))
                length_boost = 0.1 if length_diff == 0 else 0.05 if length_diff == 1 else 0
                
                confidence = max(0, 1 - (distance * 0.3)) + soundex_boost + first_letter_boost + length_boost
                confidence = min(1.0, confidence * (1 + freq / 10000))
                
                suggestions.append(SpellingSuggestion(
                    original=word,
                    suggestion=dict_word,
                    distance=distance,
                    confidence=confidence
                ))
                
        # Sort by confidence (descending) and distance (ascending)
        suggestions.sort(key=lambda x: (-x.confidence, x.distance))
        
        return suggestions[:n]
        
    def correct(self, word: str) -> str:
        """
        Auto-correct a word.
        
        Args:
            word: Potentially misspelled word
            
        Returns:
            Corrected word or original if no correction
        """
        suggestions = self.suggest(word, max_distance=2, n=1)
        
        if suggestions and suggestions[0].confidence > 0.6:
            return suggestions[0].suggestion
            
        return word
        
    def correct_text(self, text: str) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Correct spelling in a text.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (corrected text, list of (original, correction) pairs)
        """
        import re
        words = re.findall(r'\b\w+\b', text)
        corrections = []
        
        result = text
        for word in words:
            if not self.is_correct(word) and len(word) > 1:
                corrected = self.correct(word)
                if corrected != word.lower():
                    corrections.append((word, corrected))
                    # Preserve original case
                    if word[0].isupper():
                        corrected = corrected.capitalize()
                    result = re.sub(r'\b' + re.escape(word) + r'\b', corrected, result, count=1)
                    
        return result, corrections
        
    def train_on_text(self, text: str):
        """Learn word frequencies from text."""
        import re
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        for word in words:
            if len(word) > 1:
                self.add_word(word)


# =============================================================================
# SINGLETON & HELPER FUNCTIONS
# =============================================================================

_corrector: Optional[SpellingCorrector] = None


def get_spelling_corrector() -> SpellingCorrector:
    """Get the global spelling corrector instance."""
    global _corrector
    if _corrector is None:
        _corrector = SpellingCorrector()
    return _corrector


def check_spelling(word: str) -> bool:
    """Check if a word is spelled correctly."""
    return get_spelling_corrector().is_correct(word)


def get_suggestions(word: str, n: int = 5) -> List[SpellingSuggestion]:
    """Get spelling suggestions."""
    return get_spelling_corrector().suggest(word, n=n)


def correct_word(word: str) -> str:
    """Auto-correct a word."""
    return get_spelling_corrector().correct(word)


def correct_text(text: str) -> str:
    """Correct spelling in text."""
    corrected, _ = get_spelling_corrector().correct_text(text)
    return corrected
