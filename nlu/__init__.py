# nlu/__init__.py
"""
NLU - Natural Language Understanding
=====================================
Provides natural language understanding capabilities for the daemon.

Components:
- NLUEngine: Main NLU processor
- SpellingCorrector: Spelling correction with Levenshtein distance
- WordEmbeddings: Word vectors and similarity
- EntityLinking: Entity resolution
- LanguageDetector: Language identification
- DependencyParser: Syntactic parsing
- EnhancedNLU: Advanced NLU with all features combined
"""

from .nlu_engine import NLUEngine
from .device_commands import DeviceCommandHandler, handle_device_command

# Spelling correction
try:
    from .spelling import SpellingCorrector, SpellingSuggestion
except ImportError:
    SpellingCorrector = None
    SpellingSuggestion = None

# Word embeddings
try:
    from .word_embeddings import WordEmbeddings, EmbeddingModel
except ImportError:
    WordEmbeddings = None
    EmbeddingModel = None

# Entity linking
try:
    from .entity_linking import EntityLinker, LinkedEntity
except ImportError:
    EntityLinker = None
    LinkedEntity = None

# Language detection
try:
    from .language_detection import LanguageDetector, DetectedLanguage
except ImportError:
    LanguageDetector = None
    DetectedLanguage = None

# Dependency parsing
try:
    from .dependency_parsing import DependencyParser, ParsedSentence
except ImportError:
    DependencyParser = None
    ParsedSentence = None

# Enhanced NLU
try:
    from .enhanced_nlu import EnhancedNLU
except ImportError:
    EnhancedNLU = None

__all__ = [
    # Core
    'NLUEngine',
    'DeviceCommandHandler',
    'handle_device_command',
    
    # Spelling
    'SpellingCorrector',
    'SpellingSuggestion',
    
    # Embeddings
    'WordEmbeddings',
    'EmbeddingModel',
    
    # Entity Linking
    'EntityLinker',
    'LinkedEntity',
    
    # Language Detection
    'LanguageDetector',
    'DetectedLanguage',
    
    # Dependency Parsing
    'DependencyParser',
    'ParsedSentence',
    
    # Enhanced
    'EnhancedNLU',
]
