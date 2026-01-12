# language/__init__.py
"""
Language Module
===============
Comprehensive language understanding and generation capabilities.

Components:
- Vocabulary: Word knowledge, definitions, relationships
- Grammar: Sentence structure, syntax rules, parsing
- Semantics: Meaning extraction and understanding
- Education: Learning tracking and tutoring

Integrates with Unimind's cognition pipeline for enhanced NLU.
"""

from .vocabulary import Vocabulary, Word, WordRelation
from .grammar import Grammar, SentenceParser, GrammarRule
from .semantics import SemanticAnalyzer, ConceptGraph
from .education import EducationModule, LearningSession, LearningProgress

__all__ = [
    # Vocabulary
    'Vocabulary',
    'Word',
    'WordRelation',
    
    # Grammar
    'Grammar',
    'SentenceParser',
    'GrammarRule',
    
    # Semantics
    'SemanticAnalyzer',
    'ConceptGraph',
    
    # Education
    'EducationModule',
    'LearningSession',
    'LearningProgress',
]
