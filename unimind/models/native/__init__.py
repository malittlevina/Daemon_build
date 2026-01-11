# unimind/models/native/__init__.py
# Native AI Models Package - Local, self-contained AI capabilities

"""
Native AI Models Package

This package provides local, self-contained AI capabilities without
requiring external API dependencies.

Components:
- NativeLLM: Complete local language model system
- NativeModelManager: Model downloading and management
- Tokenizers: BPE, WordPiece, Character-level
- Embeddings: TF-IDF, Word2Vec, Sentence embeddings
- InferenceEngine: Local text generation

Example:
    from unimind.models.native import get_native_llm
    
    llm = get_native_llm()
    
    # Generate text
    result = llm.generate("Explain machine learning")
    print(result.text)
    
    # Chat
    response = llm.chat("Hello, how are you?")
    print(response)
    
    # Embeddings
    embedding = llm.embed("This is a test")
    similarity = llm.similarity("Hello", "Hi there")
"""

# Main NativeLLM
from unimind.models.native.native_llm import (
    NativeLLM,
    NativeLLMConfig,
    ConversationMessage,
    InferenceBackend,
    get_native_llm,
    create_native_llm,
    quick_generate,
    quick_chat,
)

# Model Manager
from unimind.models.native.model_manager import (
    NativeModelManager,
    ModelMetadata,
    ModelFormat,
    ModelType,
    QuantizationType,
    get_model_manager,
    KNOWN_MODELS,
)

# Tokenizers
from unimind.models.native.tokenizer import (
    BPETokenizer,
    WordPieceTokenizer,
    CharacterTokenizer,
    TokenizerConfig,
    TokenizerFactory,
    create_basic_tokenizer,
)

# Inference Engine
from unimind.models.native.inference_engine import (
    NativeInferenceEngine,
    NativeLanguageModel,
    GenerationConfig,
    GenerationResult,
    SamplingMethod,
    TopKSampler,
    TopPSampler,
    BeamSearcher,
    create_inference_engine,
)

# Embeddings
from unimind.models.native.embeddings import (
    NativeEmbeddingEngine,
    EmbeddingConfig,
    EmbeddingResult,
    TFIDFEmbedding,
    Word2VecEmbedding,
    SentenceEmbedding,
    create_embedding_engine,
    quick_embed,
)

# Brain Integration
from unimind.models.native.brain_connector import (
    NativeBrainConnector,
    BrainCapability,
    connect_native_llm_to_brain,
    create_self_contained_brain,
)

# Bootstrap & Pre-training
from unimind.models.native.pretrain_data import (
    COMMAND_PATTERNS,
    RESPONSE_TEMPLATES,
    DOMAIN_KNOWLEDGE,
    get_all_training_texts,
    get_conversation_pairs,
    get_command_intents,
)

from unimind.models.native.bootstrap import (
    BootstrapConfig,
    ConversationEngine,
    IntentClassifier,
    PretrainedDaemon,
    bootstrap_daemon,
    get_pretrained_daemon,
    quick_respond,
    quick_teach,
    create_pretrained_native_llm,
)

from unimind.models.native.first_boot import (
    FirstBootStatus,
    FirstBootInitializer,
    ensure_initialized,
    get_ready_daemon,
    quick_start,
    show_welcome,
)

# Vocabulary System
from unimind.models.native.vocabulary import (
    EnglishVocabulary,
    WordEntry,
    PartOfSpeech,
    WordFrequency,
    get_vocabulary,
    CORE_100_WORDS,
    SEMANTIC_CATEGORIES,
    SYNONYMS,
    ANTONYMS,
)

from unimind.models.native.vocabulary_extended import (
    EXTENDED_VERBS,
    EXTENDED_NOUNS,
    EXTENDED_ADJECTIVES,
    EXTENDED_ADVERBS,
    load_extended_vocabulary,
    get_vocabulary_stats,
)

from unimind.models.native.vocabulary_domains import (
    TECHNOLOGY_VOCAB,
    SCIENCE_VOCAB,
    BUSINESS_VOCAB,
    EDUCATION_VOCAB,
    HEALTH_VOCAB,
    load_domain_vocabulary,
    get_domain_stats,
)

from unimind.models.native.vocabulary_common import (
    MORE_VERBS,
    MORE_NOUNS,
    MORE_ADJECTIVES,
    load_common_vocabulary,
    get_common_stats,
)

from unimind.models.native.vocabulary_expansion import (
    SPORTS_VOCAB,
    ENTERTAINMENT_VOCAB,
    LEGAL_VOCAB,
    EMOTIONS_VOCAB,
    ARTS_VOCAB,
    SOCIAL_VOCAB,
    load_expansion_vocabulary,
    get_expansion_stats,
)

from unimind.models.native.vocabulary_academic import (
    ACADEMIC_CORE,
    DISCOURSE_MARKERS,
    load_academic_vocabulary,
    get_academic_stats,
)

from unimind.models.native.vocabulary_massive import (
    EXTENSIVE_VERBS,
    EXTENSIVE_NOUNS,
    load_massive_vocabulary,
    get_massive_stats,
)

from unimind.models.native.vocabulary_comprehensive import (
    FOOD_VOCAB,
    HOUSEHOLD_VOCAB,
    CLOTHING_VOCAB,
    NATURE_VOCAB,
    BODY_VOCAB,
    PROFESSION_VOCAB,
    DESCRIPTIVE_ADJ,
    MANNER_ADV,
    load_comprehensive_vocabulary,
    get_comprehensive_stats,
)

from unimind.models.native.vocabulary_advanced import (
    TRAVEL_VOCAB,
    BUILDING_VOCAB,
    MATERIAL_VOCAB,
    QUANTITY_VOCAB,
    TIME_VOCAB,
    COLOR_VOCAB,
    SOUND_VOCAB,
    SHAPE_VOCAB,
    load_advanced_vocabulary,
    get_advanced_stats,
)

from unimind.models.native.vocabulary_c2 import (
    SOPHISTICATED_VERBS,
    SOPHISTICATED_NOUNS,
    SOPHISTICATED_ADJ,
    GENERAL_EXPANSION,
    load_c2_vocabulary,
    get_c2_stats,
)


__all__ = [
    # Main LLM
    "NativeLLM",
    "NativeLLMConfig",
    "ConversationMessage",
    "InferenceBackend",
    "get_native_llm",
    "create_native_llm",
    "quick_generate",
    "quick_chat",
    
    # Model Manager
    "NativeModelManager",
    "ModelMetadata",
    "ModelFormat",
    "ModelType",
    "QuantizationType",
    "get_model_manager",
    "KNOWN_MODELS",
    
    # Tokenizers
    "BPETokenizer",
    "WordPieceTokenizer",
    "CharacterTokenizer",
    "TokenizerConfig",
    "TokenizerFactory",
    "create_basic_tokenizer",
    
    # Inference
    "NativeInferenceEngine",
    "NativeLanguageModel",
    "GenerationConfig",
    "GenerationResult",
    "SamplingMethod",
    "TopKSampler",
    "TopPSampler",
    "BeamSearcher",
    "create_inference_engine",
    
    # Embeddings
    "NativeEmbeddingEngine",
    "EmbeddingConfig",
    "EmbeddingResult",
    "TFIDFEmbedding",
    "Word2VecEmbedding",
    "SentenceEmbedding",
    "create_embedding_engine",
    "quick_embed",
    
    # Brain Integration
    "NativeBrainConnector",
    "BrainCapability",
    "connect_native_llm_to_brain",
    "create_self_contained_brain",
    
    # Pre-training Data
    "COMMAND_PATTERNS",
    "RESPONSE_TEMPLATES",
    "DOMAIN_KNOWLEDGE",
    "get_all_training_texts",
    "get_conversation_pairs",
    "get_command_intents",
    
    # Bootstrap
    "BootstrapConfig",
    "ConversationEngine",
    "IntentClassifier",
    "PretrainedDaemon",
    "bootstrap_daemon",
    "get_pretrained_daemon",
    "quick_respond",
    "quick_teach",
    "create_pretrained_native_llm",
    
    # First Boot
    "FirstBootStatus",
    "FirstBootInitializer",
    "ensure_initialized",
    "get_ready_daemon",
    "quick_start",
    "show_welcome",
    
    # Vocabulary
    "EnglishVocabulary",
    "WordEntry",
    "PartOfSpeech",
    "WordFrequency",
    "get_vocabulary",
    "CORE_100_WORDS",
    "SEMANTIC_CATEGORIES",
    "SYNONYMS",
    "ANTONYMS",
    "EXTENDED_VERBS",
    "EXTENDED_NOUNS",
    "EXTENDED_ADJECTIVES",
    "EXTENDED_ADVERBS",
    "load_extended_vocabulary",
    "get_vocabulary_stats",
    "TECHNOLOGY_VOCAB",
    "SCIENCE_VOCAB",
    "BUSINESS_VOCAB",
    "EDUCATION_VOCAB",
    "HEALTH_VOCAB",
    "load_domain_vocabulary",
    "get_domain_stats",
    "MORE_VERBS",
    "MORE_NOUNS",
    "MORE_ADJECTIVES",
    "load_common_vocabulary",
    "get_common_stats",
    "SPORTS_VOCAB",
    "ENTERTAINMENT_VOCAB",
    "LEGAL_VOCAB",
    "EMOTIONS_VOCAB",
    "ARTS_VOCAB",
    "SOCIAL_VOCAB",
    "load_expansion_vocabulary",
    "get_expansion_stats",
]
