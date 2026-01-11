# unimind/models/llm_providers.py
# Advanced LLM Provider System - Support for multiple LLM backends

import os
import json
import time
import hashlib
import subprocess
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Generator, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
from collections import deque


class LLMProvider(Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    MOCK = "mock"


class ModelCapability(Enum):
    """Model capabilities."""
    TEXT_GENERATION = "text_generation"
    REASONING = "reasoning"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    CONVERSATION = "conversation"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CREATIVE_WRITING = "creative_writing"
    INSTRUCTION_FOLLOWING = "instruction_following"
    CHAIN_OF_THOUGHT = "chain_of_thought"


@dataclass
class LLMConfig:
    """Configuration for an LLM model."""
    provider: LLMProvider
    model_name: str
    context_window: int = 4096
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    stop_sequences: List[str] = field(default_factory=list)
    system_prompt: str = ""
    capabilities: List[ModelCapability] = field(default_factory=list)
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    timeout: int = 60
    
    def to_dict(self) -> Dict:
        return {
            "provider": self.provider.value,
            "model_name": self.model_name,
            "context_window": self.context_window,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "capabilities": [c.value for c in self.capabilities]
        }


@dataclass
class LLMResponse:
    """Response from an LLM."""
    text: str
    model: str
    provider: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    finish_reason: str = "complete"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "model": self.model,
            "provider": self.provider,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "finish_reason": self.finish_reason
        }


@dataclass
class Message:
    """A chat message."""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {"role": self.role, "content": self.content}


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.conversation_history: List[Message] = []
        self.total_tokens_used = 0
        self.request_count = 0
        
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text from a prompt."""
        pass
    
    @abstractmethod
    def chat(self, messages: List[Message], **kwargs) -> LLMResponse:
        """Chat with the model."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        
    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        self.conversation_history.append(Message(role=role, content=content))
        
    def get_stats(self) -> Dict:
        """Get provider statistics."""
        return {
            "provider": self.config.provider.value,
            "model": self.config.model_name,
            "total_tokens": self.total_tokens_used,
            "requests": self.request_count,
            "history_length": len(self.conversation_history)
        }


class OllamaProvider(BaseLLMProvider):
    """Provider for local Ollama models."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.api_base or "http://localhost:11434"
        
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
            
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text using Ollama."""
        start_time = time.time()
        
        # Merge kwargs with config
        temperature = kwargs.get("temperature", self.config.temperature)
        max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
        
        try:
            # Build the full prompt with system message
            full_prompt = prompt
            if self.config.system_prompt:
                full_prompt = f"System: {self.config.system_prompt}\n\nUser: {prompt}\n\nAssistant:"
            
            # Call Ollama CLI
            result = subprocess.run(
                ["ollama", "run", self.config.model_name, full_prompt],
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            latency = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                text = result.stdout.strip()
                self.request_count += 1
                # Estimate tokens (rough approximation)
                tokens = len(text.split()) + len(prompt.split())
                self.total_tokens_used += tokens
                
                return LLMResponse(
                    text=text,
                    model=self.config.model_name,
                    provider="ollama",
                    tokens_used=tokens,
                    latency_ms=latency,
                    finish_reason="complete"
                )
            else:
                return LLMResponse(
                    text=f"Error: {result.stderr}",
                    model=self.config.model_name,
                    provider="ollama",
                    latency_ms=latency,
                    finish_reason="error"
                )
                
        except subprocess.TimeoutExpired:
            return LLMResponse(
                text="Error: Request timed out",
                model=self.config.model_name,
                provider="ollama",
                finish_reason="timeout"
            )
        except Exception as e:
            return LLMResponse(
                text=f"Error: {str(e)}",
                model=self.config.model_name,
                provider="ollama",
                finish_reason="error"
            )
            
    def chat(self, messages: List[Message], **kwargs) -> LLMResponse:
        """Chat using Ollama."""
        # Build prompt from messages
        prompt_parts = []
        for msg in messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")
                
        prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"
        return self.generate(prompt, **kwargs)
    
    def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                return [line.split()[0] for line in lines if line.strip()]
        except:
            pass
        return []


class MockProvider(BaseLLMProvider):
    """Mock provider for testing without actual LLM."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.responses = {
            "default": "This is a mock response from the AI model.",
            "reasoning": "Let me think through this step by step:\n1. First, I analyze the problem\n2. Then, I consider the options\n3. Finally, I reach a conclusion",
            "code": "```python\ndef solution():\n    return 'Mock code solution'\n```",
            "creative": "Once upon a time, in a digital realm far away...",
        }
        
    def is_available(self) -> bool:
        return True
        
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate mock response based on prompt content."""
        start_time = time.time()
        
        prompt_lower = prompt.lower()
        
        # Choose response based on prompt content
        if any(w in prompt_lower for w in ["think", "reason", "analyze", "step"]):
            response_text = self.responses["reasoning"]
        elif any(w in prompt_lower for w in ["code", "program", "function", "implement"]):
            response_text = self.responses["code"]
        elif any(w in prompt_lower for w in ["story", "creative", "imagine", "write"]):
            response_text = self.responses["creative"]
        else:
            response_text = self.responses["default"]
            
        # Add context from prompt
        response_text = f"{response_text}\n\n[Based on: {prompt[:100]}...]"
        
        latency = (time.time() - start_time) * 1000
        self.request_count += 1
        
        return LLMResponse(
            text=response_text,
            model=self.config.model_name,
            provider="mock",
            tokens_used=len(response_text.split()),
            latency_ms=latency,
            finish_reason="complete"
        )
        
    def chat(self, messages: List[Message], **kwargs) -> LLMResponse:
        """Mock chat response."""
        last_user_msg = ""
        for msg in reversed(messages):
            if msg.role == "user":
                last_user_msg = msg.content
                break
        return self.generate(last_user_msg, **kwargs)
    
    def set_response(self, key: str, response: str):
        """Set a custom response for a key."""
        self.responses[key] = response


class OpenAIProvider(BaseLLMProvider):
    """Provider for OpenAI API (requires API key)."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key or os.environ.get("OPENAI_API_KEY")
        self.api_base = config.api_base or "https://api.openai.com/v1"
        
    def is_available(self) -> bool:
        """Check if OpenAI API is available."""
        return self.api_key is not None
        
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate using OpenAI API."""
        if not self.is_available():
            return LLMResponse(
                text="Error: OpenAI API key not configured",
                model=self.config.model_name,
                provider="openai",
                finish_reason="error"
            )
            
        start_time = time.time()
        
        try:
            import urllib.request
            import urllib.error
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.config.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature)
            }
            
            if self.config.system_prompt:
                data["messages"].insert(0, {"role": "system", "content": self.config.system_prompt})
            
            req = urllib.request.Request(
                f"{self.api_base}/chat/completions",
                data=json.dumps(data).encode(),
                headers=headers,
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                result = json.loads(response.read().decode())
                
            latency = (time.time() - start_time) * 1000
            
            text = result["choices"][0]["message"]["content"]
            tokens = result.get("usage", {}).get("total_tokens", 0)
            
            self.request_count += 1
            self.total_tokens_used += tokens
            
            return LLMResponse(
                text=text,
                model=self.config.model_name,
                provider="openai",
                tokens_used=tokens,
                latency_ms=latency,
                finish_reason=result["choices"][0].get("finish_reason", "complete")
            )
            
        except Exception as e:
            return LLMResponse(
                text=f"Error: {str(e)}",
                model=self.config.model_name,
                provider="openai",
                finish_reason="error"
            )
            
    def chat(self, messages: List[Message], **kwargs) -> LLMResponse:
        """Chat using OpenAI API."""
        if not self.is_available():
            return LLMResponse(
                text="Error: OpenAI API key not configured",
                model=self.config.model_name,
                provider="openai",
                finish_reason="error"
            )
            
        prompt = messages[-1].content if messages else ""
        return self.generate(prompt, **kwargs)


class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    @staticmethod
    def create(config: LLMConfig) -> BaseLLMProvider:
        """Create a provider based on config."""
        if config.provider == LLMProvider.OLLAMA:
            return OllamaProvider(config)
        elif config.provider == LLMProvider.OPENAI:
            return OpenAIProvider(config)
        elif config.provider == LLMProvider.MOCK:
            return MockProvider(config)
        else:
            # Default to mock
            return MockProvider(config)
            
    @staticmethod
    def create_default(provider_type: str = "mock", model_name: str = "default") -> BaseLLMProvider:
        """Create a default provider."""
        provider = LLMProvider(provider_type.lower())
        
        # Default configs for each provider
        configs = {
            LLMProvider.OLLAMA: LLMConfig(
                provider=LLMProvider.OLLAMA,
                model_name=model_name or "llama3",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.REASONING,
                    ModelCapability.CONVERSATION
                ]
            ),
            LLMProvider.OPENAI: LLMConfig(
                provider=LLMProvider.OPENAI,
                model_name=model_name or "gpt-4",
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.REASONING,
                    ModelCapability.CODE_GENERATION,
                    ModelCapability.CONVERSATION,
                    ModelCapability.CHAIN_OF_THOUGHT
                ]
            ),
            LLMProvider.MOCK: LLMConfig(
                provider=LLMProvider.MOCK,
                model_name=model_name or "mock-model",
                capabilities=[ModelCapability.TEXT_GENERATION]
            )
        }
        
        config = configs.get(provider, configs[LLMProvider.MOCK])
        return LLMProviderFactory.create(config)


class InferenceCache:
    """Cache for LLM inference results."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0
        self._lock = threading.Lock()
        
    def _make_key(self, prompt: str, model: str, **kwargs) -> str:
        """Create cache key from prompt and parameters."""
        key_data = f"{model}:{prompt}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
        
    def get(self, prompt: str, model: str, **kwargs) -> Optional[LLMResponse]:
        """Get cached response if available."""
        key = self._make_key(prompt, model, **kwargs)
        
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                # Check TTL
                if time.time() - entry["timestamp"] < self.ttl_seconds:
                    self.hits += 1
                    return entry["response"]
                else:
                    del self.cache[key]
                    
            self.misses += 1
            return None
            
    def set(self, prompt: str, model: str, response: LLMResponse, **kwargs):
        """Cache a response."""
        key = self._make_key(prompt, model, **kwargs)
        
        with self._lock:
            # Evict if at capacity
            if len(self.cache) >= self.max_size:
                # Remove oldest entry
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
                del self.cache[oldest_key]
                
            self.cache[key] = {
                "response": response,
                "timestamp": time.time()
            }
            
    def clear(self):
        """Clear the cache."""
        with self._lock:
            self.cache.clear()
            
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        total = self.hits + self.misses
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / total if total > 0 else 0
        }


class LLMManager:
    """
    Manages multiple LLM providers with failover and caching.
    
    Features:
    - Multiple provider support
    - Automatic failover
    - Response caching
    - Token tracking
    - Provider health monitoring
    """
    
    def __init__(self, enable_cache: bool = True):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.primary_provider: Optional[str] = None
        self.cache = InferenceCache() if enable_cache else None
        self.fallback_order: List[str] = []
        
    def add_provider(self, name: str, provider: BaseLLMProvider, primary: bool = False):
        """Add a provider to the manager."""
        self.providers[name] = provider
        self.fallback_order.append(name)
        
        if primary or self.primary_provider is None:
            self.primary_provider = name
            
        print(f"[LLMManager] Added provider: {name} ({provider.config.model_name})")
        
    def remove_provider(self, name: str):
        """Remove a provider."""
        if name in self.providers:
            del self.providers[name]
            self.fallback_order.remove(name)
            
            if self.primary_provider == name:
                self.primary_provider = self.fallback_order[0] if self.fallback_order else None
                
    def generate(self, prompt: str, provider_name: str = None, use_cache: bool = True, **kwargs) -> LLMResponse:
        """
        Generate text using available providers.
        
        Args:
            prompt: The prompt to process
            provider_name: Specific provider to use (optional)
            use_cache: Whether to use caching
            **kwargs: Additional generation parameters
            
        Returns:
            LLMResponse
        """
        # Check cache first
        if use_cache and self.cache:
            model = provider_name or self.primary_provider
            cached = self.cache.get(prompt, model, **kwargs)
            if cached:
                cached.metadata["cached"] = True
                return cached
                
        # Try specified provider or primary
        providers_to_try = []
        if provider_name and provider_name in self.providers:
            providers_to_try.append(provider_name)
        else:
            # Use fallback order
            providers_to_try = [self.primary_provider] + [
                p for p in self.fallback_order if p != self.primary_provider
            ]
            
        # Try each provider
        for name in providers_to_try:
            if name not in self.providers:
                continue
                
            provider = self.providers[name]
            
            if not provider.is_available():
                continue
                
            response = provider.generate(prompt, **kwargs)
            
            if response.finish_reason != "error":
                # Cache successful response
                if use_cache and self.cache:
                    self.cache.set(prompt, name, response, **kwargs)
                return response
                
        # All providers failed
        return LLMResponse(
            text="Error: All providers failed",
            model="none",
            provider="none",
            finish_reason="error"
        )
        
    def chat(self, messages: List[Message], provider_name: str = None, **kwargs) -> LLMResponse:
        """Chat with the model."""
        providers_to_try = [provider_name] if provider_name else [self.primary_provider]
        
        for name in providers_to_try:
            if name not in self.providers:
                continue
                
            provider = self.providers[name]
            if provider.is_available():
                return provider.chat(messages, **kwargs)
                
        return LLMResponse(
            text="Error: No provider available",
            model="none",
            provider="none",
            finish_reason="error"
        )
        
    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        """Get a specific provider."""
        return self.providers.get(name)
        
    def list_providers(self) -> List[Dict]:
        """List all providers and their status."""
        return [
            {
                "name": name,
                "model": p.config.model_name,
                "provider_type": p.config.provider.value,
                "available": p.is_available(),
                "stats": p.get_stats()
            }
            for name, p in self.providers.items()
        ]
        
    def get_status(self) -> Dict:
        """Get manager status."""
        return {
            "providers": len(self.providers),
            "primary": self.primary_provider,
            "cache_stats": self.cache.get_stats() if self.cache else None,
            "provider_list": self.list_providers()
        }


# Convenience function for quick setup
def create_llm_manager(use_ollama: bool = True, use_mock: bool = True) -> LLMManager:
    """Create a pre-configured LLM manager."""
    manager = LLMManager(enable_cache=True)
    
    if use_ollama:
        ollama_provider = LLMProviderFactory.create_default("ollama", "llama3")
        if ollama_provider.is_available():
            manager.add_provider("ollama", ollama_provider, primary=True)
            
    if use_mock:
        mock_provider = LLMProviderFactory.create_default("mock")
        manager.add_provider("mock", mock_provider, primary=not use_ollama)
        
    return manager
