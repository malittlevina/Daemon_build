# dictionary/__init__.py
"""
Daemon Dictionary Training System

This module provides pronunciation, enunciation, and speech recognition
training data for the Prometheus daemon system.

Modules:
    - lexicon_loader: Load and query the daemon vocabulary with IPA pronunciation
    - phonetic_trainer: Training utilities for pronunciation practice and validation

Data Files:
    - daemon_lexicon.json: Core vocabulary with phonetic data
    - pronunciation_rules.json: Enunciation rules and patterns
    - training_phrases.json: Speech recognition training data

Usage:
    from dictionary import get_lexicon, get_trainer
    
    # Look up pronunciation
    lexicon = get_lexicon()
    entry = lexicon.lookup("prometheus")
    print(entry["ipa"])  # /prəˈmiːθiəs/
    
    # Generate practice drills
    trainer = get_trainer()
    drills = trainer.generate_drill_session(drill_type="mixed", num_items=5)
"""

from dictionary.lexicon_loader import (
    LexiconLoader,
    get_lexicon,
    lookup,
    get_ipa,
    get_phonetic,
    match_command
)

from dictionary.phonetic_trainer import (
    PhoneticTrainer,
    get_trainer
)

__all__ = [
    # Lexicon
    "LexiconLoader",
    "get_lexicon",
    "lookup",
    "get_ipa",
    "get_phonetic",
    "match_command",
    # Trainer
    "PhoneticTrainer",
    "get_trainer"
]

__version__ = "1.0.0"
