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
]
