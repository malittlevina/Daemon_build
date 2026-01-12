# nlu/language_detection.py
# Language Detection Module

"""
Language Detection Module

Detects the language of input text using:
- Character n-gram analysis
- Common word detection
- Script detection
- Statistical language models
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from collections import Counter
import re


@dataclass
class LanguageResult:
    """Language detection result."""
    language: str
    language_name: str
    confidence: float
    script: str
    is_english: bool


class LanguageDetector:
    """
    Language detection engine.
    
    Supports detection of:
    - English, Spanish, French, German, Italian, Portuguese
    - Chinese, Japanese, Korean
    - Russian, Arabic, Hindi
    - And more common languages
    """
    
    # Language codes and names
    LANGUAGES = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "nl": "Dutch",
        "ru": "Russian",
        "pl": "Polish",
        "cs": "Czech",
        "sv": "Swedish",
        "da": "Danish",
        "no": "Norwegian",
        "fi": "Finnish",
        "tr": "Turkish",
        "ar": "Arabic",
        "he": "Hebrew",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "hi": "Hindi",
        "th": "Thai",
        "vi": "Vietnamese",
        "id": "Indonesian",
        "ms": "Malay",
        "tl": "Filipino",
    }
    
    def __init__(self):
        # Common words for each language
        self.language_words = {
            "en": {
                "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
                "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
                "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
                "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
                "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
                "is", "are", "was", "were", "been", "being", "has", "had", "can", "could",
                "should", "would", "may", "might", "must", "shall", "will",
            },
            "es": {
                "de", "la", "que", "el", "en", "y", "a", "los", "del", "se",
                "las", "por", "un", "para", "con", "no", "una", "su", "al", "es",
                "lo", "como", "más", "pero", "sus", "le", "ya", "o", "fue", "este",
                "ha", "sí", "porque", "esta", "son", "entre", "está", "cuando", "muy", "sin",
                "sobre", "ser", "tiene", "también", "me", "hasta", "hay", "donde", "han", "quien",
            },
            "fr": {
                "de", "la", "le", "et", "les", "des", "en", "un", "du", "une",
                "que", "est", "pour", "qui", "dans", "ce", "il", "pas", "plus", "par",
                "sur", "ne", "se", "au", "avec", "son", "sont", "mais", "nous", "ou",
                "cette", "été", "tout", "elle", "même", "aux", "ont", "être", "fait", "peut",
                "comme", "aussi", "leurs", "bien", "après", "faire", "lui", "deux", "si", "ces",
            },
            "de": {
                "der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich",
                "des", "auf", "für", "ist", "im", "dem", "nicht", "ein", "eine", "als",
                "auch", "es", "an", "werden", "aus", "er", "hat", "dass", "sie", "nach",
                "wird", "bei", "einer", "um", "am", "sind", "noch", "wie", "einem", "über",
                "einen", "so", "zum", "kann", "nur", "sein", "ich", "wenn", "aber", "vor",
            },
            "it": {
                "di", "che", "e", "la", "il", "un", "a", "per", "in", "una",
                "del", "non", "sono", "da", "le", "si", "è", "con", "i", "al",
                "ha", "come", "più", "o", "questo", "anche", "lo", "ma", "essere", "nel",
                "della", "ho", "se", "alla", "ci", "gli", "dei", "sul", "molto", "stato",
            },
            "pt": {
                "de", "a", "o", "que", "e", "do", "da", "em", "um", "para",
                "é", "com", "não", "uma", "os", "no", "se", "na", "por", "mais",
                "as", "dos", "como", "mas", "foi", "ao", "ele", "das", "tem", "à",
                "seu", "sua", "ou", "ser", "quando", "muito", "há", "nos", "já", "está",
            },
            "ru": {
                "и", "в", "не", "на", "я", "что", "он", "с", "как", "это",
                "вы", "но", "по", "за", "все", "она", "так", "его", "же", "от",
                "мы", "к", "у", "из", "о", "было", "для", "то", "мне", "бы",
            },
            "zh": {
                "的", "一", "是", "了", "我", "不", "人", "在", "他", "有",
                "这", "个", "上", "们", "来", "到", "时", "大", "地", "为",
                "子", "中", "你", "说", "生", "国", "年", "着", "就", "那",
            },
            "ja": {
                "の", "に", "は", "を", "た", "が", "で", "て", "と", "し",
                "れ", "さ", "ある", "い", "も", "な", "る", "か", "から", "だ",
                "こと", "その", "ない", "です", "ます", "する", "この", "これ", "それ", "あの",
            },
            "ko": {
                "이", "그", "는", "에", "를", "은", "의", "가", "하", "다",
                "로", "을", "와", "으로", "에서", "도", "한", "것", "들", "있",
            },
            "ar": {
                "في", "من", "على", "إلى", "أن", "عن", "هذا", "مع", "و", "التي",
                "الذي", "هو", "كان", "لا", "ما", "هي", "ذلك", "لم", "بين", "كل",
            },
        }
        
        # Character patterns for script detection
        self.script_patterns = {
            "latin": r'[a-zA-ZÀ-ÿ]',
            "cyrillic": r'[а-яА-ЯёЁ]',
            "chinese": r'[\u4e00-\u9fff]',
            "japanese": r'[\u3040-\u309f\u30a0-\u30ff]',
            "korean": r'[\uac00-\ud7af\u1100-\u11ff]',
            "arabic": r'[\u0600-\u06ff]',
            "hebrew": r'[\u0590-\u05ff]',
            "devanagari": r'[\u0900-\u097f]',
            "thai": r'[\u0e00-\u0e7f]',
            "greek": r'[\u0370-\u03ff]',
        }
        
        # N-gram profiles for languages
        self.ngram_profiles = self._build_ngram_profiles()
        
    def _build_ngram_profiles(self) -> Dict[str, Counter]:
        """Build character n-gram profiles for each language."""
        profiles = {}
        
        # Sample text for each language (common phrases)
        sample_texts = {
            "en": "The quick brown fox jumps over the lazy dog. This is a sample text in English with common words and phrases.",
            "es": "El rápido zorro marrón salta sobre el perro perezoso. Este es un texto de muestra en español con palabras y frases comunes.",
            "fr": "Le renard brun rapide saute par-dessus le chien paresseux. Ceci est un exemple de texte en français avec des mots et des phrases courants.",
            "de": "Der schnelle braune Fuchs springt über den faulen Hund. Dies ist ein Beispieltext auf Deutsch mit häufigen Wörtern und Phrasen.",
            "it": "La volpe marrone veloce salta sopra il cane pigro. Questo è un testo di esempio in italiano con parole e frasi comuni.",
            "pt": "A rápida raposa marrom salta sobre o cão preguiçoso. Este é um texto de exemplo em português com palavras e frases comuns.",
        }
        
        for lang, text in sample_texts.items():
            profiles[lang] = self._get_ngrams(text.lower())
            
        return profiles
        
    def _get_ngrams(self, text: str, n: int = 3) -> Counter:
        """Get character n-grams from text."""
        text = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', text.lower())
        text = ' '.join(text.split())  # Normalize whitespace
        
        ngrams = Counter()
        for i in range(len(text) - n + 1):
            ngram = text[i:i+n]
            ngrams[ngram] += 1
            
        return ngrams
        
    def detect_script(self, text: str) -> str:
        """
        Detect the script (writing system) of text.
        
        Args:
            text: Input text
            
        Returns:
            Script name
        """
        script_counts = {}
        
        for script, pattern in self.script_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                script_counts[script] = len(matches)
                
        if not script_counts:
            return "unknown"
            
        return max(script_counts, key=script_counts.get)
        
    def detect(self, text: str) -> LanguageResult:
        """
        Detect the language of text.
        
        Args:
            text: Input text
            
        Returns:
            LanguageResult with detected language
        """
        if not text or not text.strip():
            return LanguageResult(
                language="unknown",
                language_name="Unknown",
                confidence=0.0,
                script="unknown",
                is_english=False
            )
            
        # Detect script first
        script = self.detect_script(text)
        
        # Handle non-Latin scripts
        if script == "chinese":
            return LanguageResult("zh", "Chinese", 0.95, script, False)
        elif script == "japanese":
            return LanguageResult("ja", "Japanese", 0.95, script, False)
        elif script == "korean":
            return LanguageResult("ko", "Korean", 0.95, script, False)
        elif script == "cyrillic":
            return LanguageResult("ru", "Russian", 0.85, script, False)
        elif script == "arabic":
            return LanguageResult("ar", "Arabic", 0.90, script, False)
        elif script == "hebrew":
            return LanguageResult("he", "Hebrew", 0.90, script, False)
        elif script == "devanagari":
            return LanguageResult("hi", "Hindi", 0.90, script, False)
        elif script == "thai":
            return LanguageResult("th", "Thai", 0.95, script, False)
        elif script == "greek":
            return LanguageResult("el", "Greek", 0.90, script, False)
            
        # For Latin script, use word matching and n-grams
        words = set(re.findall(r'\b[a-zA-ZÀ-ÿ]+\b', text.lower()))
        
        # Score each language by word matches
        word_scores = {}
        for lang, lang_words in self.language_words.items():
            matches = words & lang_words
            if matches:
                word_scores[lang] = len(matches) / len(words) if words else 0
                
        # Score by n-gram similarity
        text_ngrams = self._get_ngrams(text)
        ngram_scores = {}
        
        for lang, profile in self.ngram_profiles.items():
            if not profile:
                continue
            # Calculate cosine similarity
            common = set(text_ngrams.keys()) & set(profile.keys())
            if not common:
                continue
            dot_product = sum(text_ngrams[k] * profile[k] for k in common)
            mag1 = sum(v * v for v in text_ngrams.values()) ** 0.5
            mag2 = sum(v * v for v in profile.values()) ** 0.5
            if mag1 > 0 and mag2 > 0:
                ngram_scores[lang] = dot_product / (mag1 * mag2)
                
        # Combine scores
        combined_scores = {}
        for lang in set(word_scores.keys()) | set(ngram_scores.keys()):
            word_score = word_scores.get(lang, 0)
            ngram_score = ngram_scores.get(lang, 0)
            combined_scores[lang] = word_score * 0.7 + ngram_score * 0.3
            
        if not combined_scores:
            # Default to English for Latin script
            return LanguageResult("en", "English", 0.3, script, True)
            
        # Get best language
        best_lang = max(combined_scores, key=combined_scores.get)
        confidence = combined_scores[best_lang]
        
        # Normalize confidence
        confidence = min(0.99, confidence * 1.5)  # Scale up but cap at 0.99
        
        return LanguageResult(
            language=best_lang,
            language_name=self.LANGUAGES.get(best_lang, "Unknown"),
            confidence=confidence,
            script=script,
            is_english=(best_lang == "en")
        )
        
    def detect_multiple(self, text: str, n: int = 3) -> List[Tuple[str, float]]:
        """
        Detect multiple possible languages with scores.
        
        Args:
            text: Input text
            n: Number of results
            
        Returns:
            List of (language_code, confidence) tuples
        """
        words = set(re.findall(r'\b[a-zA-ZÀ-ÿ]+\b', text.lower()))
        
        scores = {}
        for lang, lang_words in self.language_words.items():
            matches = words & lang_words
            if matches:
                scores[lang] = len(matches) / max(1, len(words))
                
        # Sort by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_scores[:n]
        
    def is_english(self, text: str) -> bool:
        """
        Quick check if text is English.
        
        Args:
            text: Input text
            
        Returns:
            True if text is likely English
        """
        result = self.detect(text)
        return result.is_english and result.confidence > 0.5


# =============================================================================
# SINGLETON & HELPER FUNCTIONS
# =============================================================================

_detector: Optional[LanguageDetector] = None


def get_language_detector() -> LanguageDetector:
    """Get the global language detector instance."""
    global _detector
    if _detector is None:
        _detector = LanguageDetector()
    return _detector


def detect_language(text: str) -> LanguageResult:
    """Detect the language of text."""
    return get_language_detector().detect(text)


def is_english(text: str) -> bool:
    """Quick check if text is English."""
    return get_language_detector().is_english(text)


def detect_script(text: str) -> str:
    """Detect the script of text."""
    return get_language_detector().detect_script(text)
