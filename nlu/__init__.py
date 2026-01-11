# nlu/__init__.py
# Natural Language Understanding Package

"""
Natural Language Understanding Package

This package provides comprehensive NLU capabilities for the daemon:

1. Enhanced NLU Engine:
   - Intent classification (20+ intent types)
   - Entity extraction (NER)
   - Part-of-speech tagging
   - Sentiment analysis
   - Semantic role labeling
   - Key phrase extraction
   - Topic extraction
   - Context tracking

2. Grammar Analysis:
   - Sentence structure analysis
   - Phrase detection (NP, VP, PP)
   - Question type detection
   - Passive voice detection
   - Tense detection
   - Grammar issue detection

3. Text Normalization:
   - Contraction expansion
   - Spelling correction
   - Number normalization

4. Morphological Analysis:
   - Prefix/suffix detection
   - Word root extraction
   - Word family generation

5. Vocabulary System:
   - 5000+ English words
   - Synonyms and antonyms
   - Semantic categories
   - Domain-specific vocabulary

Example:
    from nlu import analyze, classify_intent, extract_entities
    
    # Complete analysis
    result = analyze("What time is the meeting tomorrow?")
    print(f"Intent: {result.intent.intent.value}")
    print(f"Entities: {[e.text for e in result.entities]}")
    print(f"Sentiment: {result.sentiment.sentiment.value}")
    
    # Quick intent classification
    intent = classify_intent("Help me with Python")
    print(f"Intent: {intent.intent.value}, Confidence: {intent.confidence}")

Fluency Levels by Vocabulary Size:
- A1 (Beginner): 500-1,000 words
- A2 (Elementary): 1,000-2,000 words
- B1 (Intermediate): 2,000-4,000 words
- B2 (Upper Intermediate): 4,000-8,000 words
- C1 (Advanced): 8,000-16,000 words
- C2 (Mastery): 16,000+ words
- Native Adult: 20,000-35,000 words
"""

# Enhanced NLU Engine
from nlu.enhanced_nlu import (
    # Main Engine
    EnhancedNLUEngine,
    get_nlu_engine,
    
    # Quick Functions
    analyze,
    classify_intent,
    extract_entities,
    analyze_sentiment,
    
    # Enums
    Intent,
    EntityType,
    POSTag,
    Sentiment,
    
    # Data Classes
    Entity,
    Token,
    IntentResult,
    SentimentResult,
    SemanticRole,
    NLUResult,
)

# Grammar Analysis
from nlu.grammar_analysis import (
    # Analyzers
    GrammarAnalyzer,
    TextNormalizer,
    MorphologicalAnalyzer,
    
    # Singleton Getters
    get_grammar_analyzer,
    get_text_normalizer,
    get_morphological_analyzer,
    
    # Quick Functions
    analyze_grammar,
    normalize_text,
    analyze_morphology,
    
    # Enums
    PhraseType,
    SentenceType,
    QuestionType,
    
    # Data Classes
    Phrase,
    GrammarIssue,
    SentenceAnalysis,
)

# Word Embeddings
from nlu.word_embeddings import (
    WordEmbeddings,
    WordVector,
    SemanticSearch,
    get_embeddings,
    word_similarity,
    sentence_similarity,
    find_similar,
    word_analogy,
)

# Spelling Correction
from nlu.spelling import (
    SpellingCorrector,
    SpellingSuggestion,
    get_spelling_corrector,
    check_spelling,
    get_suggestions,
    correct_word,
    correct_text,
)

# Language Detection
from nlu.language_detection import (
    LanguageDetector,
    LanguageResult,
    get_language_detector,
    detect_language,
    is_english,
    detect_script,
)

# Dependency Parsing & Coreference Resolution
from nlu.dependency_parsing import (
    DependencyParser,
    DependencyTree,
    DependencyNode,
    DependencyRelation,
    CoreferenceResolver,
    CoreferenceChain,
    Mention,
    get_dependency_parser,
    get_coreference_resolver,
    parse_dependencies,
    resolve_coreferences,
    get_resolved_text,
)

# Named Entity Linking
from nlu.entity_linking import (
    EntityLinker,
    KnowledgeBase,
    KnowledgeEntry,
    LinkedEntity,
    EntityCategory,
    get_entity_linker,
    get_knowledge_base,
    link_entities,
    lookup_entity,
    search_knowledge_base,
    get_entity_facts,
)

# Legacy NLU Engine (for backwards compatibility)
try:
    from nlu.nlu_engine import (
        NLUEngine,
        run_self_analysis,
        nightly_reflection,
    )
except ImportError:
    # Legacy engine has unmet dependencies, provide stubs
    NLUEngine = None
    run_self_analysis = None
    nightly_reflection = None


__all__ = [
    # Enhanced NLU
    "EnhancedNLUEngine",
    "get_nlu_engine",
    "analyze",
    "classify_intent",
    "extract_entities",
    "analyze_sentiment",
    "Intent",
    "EntityType",
    "POSTag",
    "Sentiment",
    "Entity",
    "Token",
    "IntentResult",
    "SentimentResult",
    "SemanticRole",
    "NLUResult",
    
    # Grammar Analysis
    "GrammarAnalyzer",
    "TextNormalizer",
    "MorphologicalAnalyzer",
    "get_grammar_analyzer",
    "get_text_normalizer",
    "get_morphological_analyzer",
    "analyze_grammar",
    "normalize_text",
    "analyze_morphology",
    "PhraseType",
    "SentenceType",
    "QuestionType",
    "Phrase",
    "GrammarIssue",
    "SentenceAnalysis",
    
    # Word Embeddings
    "WordEmbeddings",
    "WordVector",
    "SemanticSearch",
    "get_embeddings",
    "word_similarity",
    "sentence_similarity",
    "find_similar",
    "word_analogy",
    
    # Spelling Correction
    "SpellingCorrector",
    "SpellingSuggestion",
    "get_spelling_corrector",
    "check_spelling",
    "get_suggestions",
    "correct_word",
    "correct_text",
    
    # Language Detection
    "LanguageDetector",
    "LanguageResult",
    "get_language_detector",
    "detect_language",
    "is_english",
    "detect_script",
    
    # Dependency Parsing
    "DependencyParser",
    "DependencyTree",
    "DependencyNode",
    "DependencyRelation",
    "get_dependency_parser",
    "parse_dependencies",
    
    # Coreference Resolution
    "CoreferenceResolver",
    "CoreferenceChain",
    "Mention",
    "get_coreference_resolver",
    "resolve_coreferences",
    "get_resolved_text",
    
    # Entity Linking
    "EntityLinker",
    "KnowledgeBase",
    "KnowledgeEntry",
    "LinkedEntity",
    "EntityCategory",
    "get_entity_linker",
    "get_knowledge_base",
    "link_entities",
    "lookup_entity",
    "search_knowledge_base",
    "get_entity_facts",
    
    # Legacy
    "NLUEngine",
    "run_self_analysis",
    "nightly_reflection",
]


# Convenience function for comprehensive analysis
def full_analysis(text: str) -> dict:
    """
    Perform comprehensive NLU and grammar analysis.
    
    Args:
        text: Input text
        
    Returns:
        Dict with all analysis results
    """
    nlu_result = analyze(text)
    grammar_result = analyze_grammar(text)
    normalized = normalize_text(text)
    
    return {
        "original": text,
        "normalized": normalized,
        "nlu": {
            "intent": nlu_result.intent.intent.value,
            "intent_confidence": nlu_result.intent.confidence,
            "entities": [{"text": e.text, "type": e.entity_type.value} for e in nlu_result.entities],
            "sentiment": nlu_result.sentiment.sentiment.value,
            "sentiment_score": nlu_result.sentiment.score,
            "key_phrases": nlu_result.key_phrases,
            "topics": nlu_result.topics,
        },
        "grammar": {
            "sentence_type": grammar_result.sentence_type.value,
            "question_type": grammar_result.question_type.value if grammar_result.question_type else None,
            "subject": grammar_result.subject,
            "predicate": grammar_result.predicate,
            "tense": grammar_result.tense,
            "is_passive": grammar_result.is_passive,
            "issues": [{"type": i.issue_type, "text": i.text, "suggestion": i.suggestion} 
                      for i in grammar_result.issues],
        }
    }
