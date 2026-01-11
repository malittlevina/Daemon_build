# unimind/models/native/native_llm.py
# Native LLM - Complete local language model system

import os
import json
import time
import subprocess
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum

from unimind.models.native.model_manager import (
    NativeModelManager, get_model_manager,
    ModelType, ModelFormat, QuantizationType, ModelMetadata
)
from unimind.models.native.tokenizer import (
    BPETokenizer, TokenizerConfig, TokenizerFactory, create_basic_tokenizer
)
from unimind.models.native.inference_engine import (
    NativeInferenceEngine, NativeLanguageModel,
    GenerationConfig, GenerationResult, SamplingMethod
)
from unimind.models.native.embeddings import (
    NativeEmbeddingEngine, EmbeddingConfig, EmbeddingResult
)


class InferenceBackend(Enum):
    """Available inference backends."""
    NATIVE = "native"       # Pure Python (portable but slower)
    OLLAMA = "ollama"       # Ollama (fast, requires install)
    LLAMACPP = "llamacpp"   # llama.cpp (fast, requires build)
    CTRANSFORMERS = "ctransformers"  # CTransformers (moderate)


@dataclass
class NativeLLMConfig:
    """Configuration for the Native LLM."""
    # Model settings
    default_model: str = "tinyllama-1b"
    context_length: int = 2048
    
    # Generation defaults
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repetition_penalty: float = 1.1
    
    # Backend settings
    preferred_backend: InferenceBackend = InferenceBackend.NATIVE
    fallback_to_native: bool = True
    
    # Embedding settings
    embedding_dimension: int = 384
    
    # Cache settings
    enable_kv_cache: bool = True
    enable_response_cache: bool = True
    cache_max_size: int = 1000
    
    # Performance settings
    num_threads: int = 4
    batch_size: int = 1
    
    def to_dict(self) -> Dict:
        return {
            "default_model": self.default_model,
            "context_length": self.context_length,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "preferred_backend": self.preferred_backend.value
        }


@dataclass
class ConversationMessage:
    """A message in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {"role": self.role, "content": self.content}


class ResponseCache:
    """Cache for LLM responses."""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, str] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        
    def _make_key(self, prompt: str, config: GenerationConfig) -> str:
        """Create cache key."""
        import hashlib
        key_data = f"{prompt}:{config.temperature}:{config.top_p}:{config.max_tokens}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
        
    def get(self, prompt: str, config: GenerationConfig) -> Optional[str]:
        """Get cached response."""
        key = self._make_key(prompt, config)
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
        
    def set(self, prompt: str, config: GenerationConfig, response: str):
        """Cache a response."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            if self.cache:
                oldest = next(iter(self.cache))
                del self.cache[oldest]
                
        key = self._make_key(prompt, config)
        self.cache[key] = response
        
    def clear(self):
        self.cache.clear()
        
    def get_stats(self) -> Dict:
        total = self.hits + self.misses
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / total if total > 0 else 0
        }


class OllamaBackend:
    """Backend using Ollama for inference."""
    
    def __init__(self):
        self.available = self._check_available()
        self.current_model: Optional[str] = None
        
    def _check_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
            
    def is_available(self) -> bool:
        return self.available
        
    def list_models(self) -> List[str]:
        """List installed Ollama models."""
        if not self.available:
            return []
            
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]
                return [line.split()[0] for line in lines if line.strip()]
        except:
            pass
        return []
        
    def generate(
        self,
        prompt: str,
        model: str = "llama3",
        config: GenerationConfig = None
    ) -> GenerationResult:
        """Generate using Ollama."""
        config = config or GenerationConfig()
        start = time.time()
        
        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            elapsed = (time.time() - start) * 1000
            
            if result.returncode == 0:
                text = result.stdout.strip()
                tokens = len(text.split())
                
                return GenerationResult(
                    text=text,
                    tokens_generated=tokens,
                    tokens_per_second=tokens / (elapsed / 1000) if elapsed > 0 else 0,
                    finish_reason="stop",
                    total_time_ms=elapsed
                )
                
        except subprocess.TimeoutExpired:
            return GenerationResult(
                text="[Timeout]",
                tokens_generated=0,
                tokens_per_second=0,
                finish_reason="timeout",
                total_time_ms=60000
            )
        except Exception as e:
            return GenerationResult(
                text=f"[Error: {e}]",
                tokens_generated=0,
                tokens_per_second=0,
                finish_reason="error"
            )


class NativeLLM:
    """
    Native Large Language Model - Self-contained AI system.
    
    Features:
    - Multiple inference backends (Native, Ollama, llama.cpp)
    - Local model management and downloading
    - Native tokenization (BPE, WordPiece)
    - Local embeddings (TF-IDF, Word2Vec)
    - Response caching
    - Conversation memory
    - No external API dependencies
    """
    
    def __init__(self, config: NativeLLMConfig = None):
        self.config = config or NativeLLMConfig()
        
        # Initialize components
        self.model_manager = get_model_manager()
        self.tokenizer = create_basic_tokenizer()
        self.native_engine = NativeInferenceEngine()
        self.embedding_engine = NativeEmbeddingEngine(
            EmbeddingConfig(dimension=self.config.embedding_dimension)
        )
        
        # Load a default native model for the engine
        default_model = NativeLanguageModel(
            vocab_size=self.tokenizer.vocab_size,
            d_model=256,
            n_layers=4,
            n_heads=4
        )
        self.native_engine.load_model(default_model)
        self.native_engine.set_tokenizer(self.tokenizer)
        
        # Backends
        self.ollama_backend = OllamaBackend()
        self.active_backend: InferenceBackend = self._select_backend()
        
        # Caching
        self.response_cache = ResponseCache(self.config.cache_max_size)
        
        # Conversation state
        self.conversations: Dict[str, List[ConversationMessage]] = {}
        self.active_conversation: Optional[str] = None
        
        # Stats
        self.stats = {
            "total_generations": 0,
            "total_tokens": 0,
            "total_time_ms": 0
        }
        
        print(f"[NativeLLM] Initialized with backend: {self.active_backend.value}")
        
    def _select_backend(self) -> InferenceBackend:
        """Select the best available backend."""
        preferred = self.config.preferred_backend
        
        if preferred == InferenceBackend.OLLAMA:
            if self.ollama_backend.is_available():
                return InferenceBackend.OLLAMA
            elif self.config.fallback_to_native:
                print("[NativeLLM] Ollama not available, falling back to native")
                return InferenceBackend.NATIVE
                
        return InferenceBackend.NATIVE
        
    def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        top_p: float = None,
        stop_sequences: List[str] = None,
        use_cache: bool = True,
        stream: bool = False
    ) -> GenerationResult:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling threshold
            stop_sequences: Stop generation sequences
            use_cache: Whether to use response caching
            stream: Whether to stream output
            
        Returns:
            GenerationResult
        """
        # Build generation config
        config = GenerationConfig(
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=temperature or self.config.temperature,
            top_p=top_p or self.config.top_p,
            stop_sequences=stop_sequences or [],
            sampling_method=SamplingMethod.TOP_P
        )
        
        # Check cache
        if use_cache and self.config.enable_response_cache:
            cached = self.response_cache.get(prompt, config)
            if cached:
                return GenerationResult(
                    text=cached,
                    tokens_generated=len(cached.split()),
                    tokens_per_second=0,
                    finish_reason="cached"
                )
                
        # Generate based on backend
        if self.active_backend == InferenceBackend.OLLAMA:
            # Get installed Ollama model
            models = self.ollama_backend.list_models()
            model = models[0] if models else "llama3"
            result = self.ollama_backend.generate(prompt, model, config)
        else:
            # Use native engine
            self.native_engine.set_tokenizer(self.tokenizer)
            result = self.native_engine.generate(prompt, config)
            
        # Update cache
        if use_cache and self.config.enable_response_cache:
            self.response_cache.set(prompt, config, result.text)
            
        # Update stats
        self.stats["total_generations"] += 1
        self.stats["total_tokens"] += result.tokens_generated
        self.stats["total_time_ms"] += result.total_time_ms
        
        return result
        
    def chat(
        self,
        message: str,
        conversation_id: str = None,
        system_prompt: str = None
    ) -> str:
        """
        Chat interface with conversation memory.
        
        Args:
            message: User message
            conversation_id: Conversation ID (creates new if None)
            system_prompt: System prompt for new conversations
            
        Returns:
            Assistant response
        """
        # Get or create conversation
        if conversation_id is None:
            conversation_id = f"conv_{int(time.time())}"
            
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
            
            # Add system prompt
            if system_prompt:
                self.conversations[conversation_id].append(
                    ConversationMessage(role="system", content=system_prompt)
                )
                
        self.active_conversation = conversation_id
        
        # Add user message
        self.conversations[conversation_id].append(
            ConversationMessage(role="user", content=message)
        )
        
        # Build prompt from conversation
        prompt = self._build_chat_prompt(conversation_id)
        
        # Generate response
        result = self.generate(prompt, use_cache=False)
        
        # Add assistant response
        self.conversations[conversation_id].append(
            ConversationMessage(role="assistant", content=result.text)
        )
        
        return result.text
        
    def _build_chat_prompt(self, conversation_id: str) -> str:
        """Build prompt from conversation history."""
        messages = self.conversations.get(conversation_id, [])
        
        parts = []
        for msg in messages:
            if msg.role == "system":
                parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                parts.append(f"Assistant: {msg.content}")
                
        parts.append("Assistant:")
        return "\n\n".join(parts)
        
    def embed(self, text: str, model: str = "tfidf") -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
            model: Embedding model ("tfidf", "word2vec", "sentence")
            
        Returns:
            Embedding vector
        """
        result = self.embedding_engine.embed(text, model)
        return result.embedding
        
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        return self.embedding_engine.similarity(text1, text2)
        
    def find_similar(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5
    ) -> List[tuple]:
        """Find most similar texts."""
        return self.embedding_engine.find_similar(query, candidates, top_k)
        
    def train_embeddings(self, texts: List[str]):
        """Train embedding models on local data."""
        self.embedding_engine.train(texts, model="all")
        
    def train_tokenizer(self, texts: List[str], vocab_size: int = 32000):
        """Train tokenizer on local data."""
        self.tokenizer = BPETokenizer()
        self.tokenizer.train(texts, vocab_size)
        
    def install_model(
        self,
        model_id: str,
        source_url: str = None,
        progress_callback=None
    ) -> bool:
        """
        Install a model for local use.
        
        Args:
            model_id: Model identifier (e.g., "tinyllama-1b")
            source_url: Optional direct download URL
            progress_callback: Progress callback function
            
        Returns:
            True if successful
        """
        return self.model_manager.download_model(
            model_id, source_url, progress_callback
        )
        
    def list_available_models(self) -> List[Dict]:
        """List models available for installation."""
        return self.model_manager.list_available_models()
        
    def list_installed_models(self) -> List[Dict]:
        """List installed models."""
        installed = self.model_manager.list_installed_models()
        
        # Also list Ollama models
        if self.ollama_backend.is_available():
            for name in self.ollama_backend.list_models():
                installed.append({
                    "model_id": f"ollama:{name}",
                    "name": name,
                    "format": "ollama",
                    "backend": "ollama"
                })
                
        return installed
        
    def clear_conversation(self, conversation_id: str = None):
        """Clear conversation history."""
        if conversation_id:
            if conversation_id in self.conversations:
                del self.conversations[conversation_id]
        else:
            self.conversations.clear()
            self.active_conversation = None
            
    def get_conversation(self, conversation_id: str = None) -> List[Dict]:
        """Get conversation history."""
        cid = conversation_id or self.active_conversation
        if cid and cid in self.conversations:
            return [m.to_dict() for m in self.conversations[cid]]
        return []
        
    def save_state(self, path: str):
        """Save LLM state to file."""
        state = {
            "config": self.config.to_dict(),
            "conversations": {
                cid: [m.to_dict() for m in msgs]
                for cid, msgs in self.conversations.items()
            },
            "stats": self.stats,
            "cache_stats": self.response_cache.get_stats()
        }
        
        with open(path, "w") as f:
            json.dump(state, f, indent=2)
            
        print(f"[NativeLLM] State saved to {path}")
        
    def load_state(self, path: str):
        """Load LLM state from file."""
        with open(path) as f:
            state = json.load(f)
            
        self.stats = state.get("stats", self.stats)
        
        # Restore conversations
        for cid, msgs in state.get("conversations", {}).items():
            self.conversations[cid] = [
                ConversationMessage(**m) for m in msgs
            ]
            
        print(f"[NativeLLM] State loaded from {path}")
        
    def get_status(self) -> Dict:
        """Get LLM status."""
        avg_time = (
            self.stats["total_time_ms"] / self.stats["total_generations"]
            if self.stats["total_generations"] > 0 else 0
        )
        
        return {
            "backend": self.active_backend.value,
            "ollama_available": self.ollama_backend.is_available(),
            "installed_models": len(self.model_manager.list_installed_models()),
            "conversations": len(self.conversations),
            "stats": {
                **self.stats,
                "average_time_ms": avg_time,
                "tokens_per_second": (
                    self.stats["total_tokens"] / (self.stats["total_time_ms"] / 1000)
                    if self.stats["total_time_ms"] > 0 else 0
                )
            },
            "cache": self.response_cache.get_stats(),
            "embedding_stats": self.embedding_engine.get_stats()
        }
        
    def reset_stats(self):
        """Reset statistics."""
        self.stats = {
            "total_generations": 0,
            "total_tokens": 0,
            "total_time_ms": 0
        }
        self.response_cache.clear()


# =============================================================================
# Singleton and Factory Functions
# =============================================================================

_native_llm: Optional[NativeLLM] = None


def get_native_llm() -> NativeLLM:
    """Get the global NativeLLM instance."""
    global _native_llm
    if _native_llm is None:
        _native_llm = NativeLLM()
    return _native_llm


def create_native_llm(config: NativeLLMConfig = None) -> NativeLLM:
    """Create a new NativeLLM instance."""
    return NativeLLM(config)


def quick_generate(prompt: str, max_tokens: int = 256) -> str:
    """Quick generation using default settings."""
    llm = get_native_llm()
    result = llm.generate(prompt, max_tokens=max_tokens)
    return result.text


def quick_chat(message: str) -> str:
    """Quick chat using default settings."""
    llm = get_native_llm()
    return llm.chat(message)
