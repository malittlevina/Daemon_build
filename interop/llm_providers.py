# interop/llm_providers.py
"""
LLM Provider Abstraction - Unified interface to multiple LLM backends

Supports:
- Ollama (local)
- OpenAI API
- Anthropic API
- Custom endpoints
"""

from typing import Dict, Any, List, Optional, Generator, Callable
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
import json
import os
import threading


class ProviderType(Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


@dataclass
class Message:
    """A message in a conversation."""
    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CompletionRequest:
    """Request for LLM completion."""
    messages: List[Message]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024
    stop: Optional[List[str]] = None
    stream: bool = False
    tools: Optional[List[Dict]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompletionResponse:
    """Response from LLM completion."""
    content: str
    model: str
    finish_reason: str = "stop"
    usage: Dict[str, int] = field(default_factory=dict)
    tool_calls: Optional[List[Dict]] = None
    latency_ms: float = 0
    raw_response: Optional[Dict] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._lock = threading.Lock()
        self._request_count = 0
        self._total_tokens = 0
    
    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the provider type."""
        pass
    
    @property
    @abstractmethod
    def available_models(self) -> List[str]:
        """Return list of available models."""
        pass
    
    @abstractmethod
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Generate a completion."""
        pass
    
    @abstractmethod
    def stream_complete(
        self, 
        request: CompletionRequest
    ) -> Generator[str, None, None]:
        """Stream a completion."""
        pass
    
    def chat(
        self,
        user_message: str,
        system_prompt: str = None,
        history: List[Message] = None,
        **kwargs
    ) -> str:
        """Convenience method for simple chat."""
        messages = []
        
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        
        if history:
            messages.extend(history)
        
        messages.append(Message(role="user", content=user_message))
        
        request = CompletionRequest(messages=messages, **kwargs)
        response = self.complete(request)
        
        return response.content
    
    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics."""
        return {
            "provider": self.provider_type.value,
            "request_count": self._request_count,
            "total_tokens": self._total_tokens
        }


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.default_model = config.get("default_model", "llama3")
        self._models_cache = None
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OLLAMA
    
    @property
    def available_models(self) -> List[str]:
        if self._models_cache:
            return self._models_cache
        
        try:
            import subprocess
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                models = [line.split()[0] for line in lines if line.strip()]
                self._models_cache = models
                return models
        except Exception:
            pass
        
        return [self.default_model]
    
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Generate completion using Ollama."""
        import subprocess
        import time
        
        start_time = time.time()
        model = request.model or self.default_model
        
        # Build prompt from messages
        prompt = self._build_prompt(request.messages)
        
        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            latency = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                content = result.stdout.strip()
                
                with self._lock:
                    self._request_count += 1
                    self._total_tokens += len(content.split())  # Rough estimate
                
                return CompletionResponse(
                    content=content,
                    model=model,
                    finish_reason="stop",
                    latency_ms=latency
                )
            else:
                return CompletionResponse(
                    content=f"Error: {result.stderr}",
                    model=model,
                    finish_reason="error",
                    latency_ms=latency
                )
                
        except subprocess.TimeoutExpired:
            return CompletionResponse(
                content="Error: Request timed out",
                model=model,
                finish_reason="timeout",
                latency_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return CompletionResponse(
                content=f"Error: {str(e)}",
                model=model,
                finish_reason="error"
            )
    
    def stream_complete(
        self, 
        request: CompletionRequest
    ) -> Generator[str, None, None]:
        """Stream completion (simplified - returns full response)."""
        response = self.complete(request)
        yield response.content
    
    def _build_prompt(self, messages: List[Message]) -> str:
        """Build prompt string from messages."""
        parts = []
        for msg in messages:
            if msg.role == "system":
                parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                parts.append(f"Assistant: {msg.content}")
        
        return "\n\n".join(parts)


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.api_key = config.get("api_key") or os.environ.get("OPENAI_API_KEY")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.default_model = config.get("default_model", "gpt-4")
        self.org_id = config.get("org_id")
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENAI
    
    @property
    def available_models(self) -> List[str]:
        return ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"]
    
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Generate completion using OpenAI API."""
        import time
        
        if not self.api_key:
            return CompletionResponse(
                content="Error: OpenAI API key not configured",
                model=request.model or self.default_model,
                finish_reason="error"
            )
        
        start_time = time.time()
        model = request.model or self.default_model
        
        try:
            # Use urllib to avoid external dependencies
            import urllib.request
            import urllib.error
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            if self.org_id:
                headers["OpenAI-Organization"] = self.org_id
            
            payload = {
                "model": model,
                "messages": [
                    {"role": msg.role, "content": msg.content}
                    for msg in request.messages
                ],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens
            }
            
            if request.stop:
                payload["stop"] = request.stop
            
            if request.tools:
                payload["tools"] = request.tools
            
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(payload).encode(),
                headers=headers,
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                data = json.loads(response.read().decode())
            
            latency = (time.time() - start_time) * 1000
            
            choice = data["choices"][0]
            
            with self._lock:
                self._request_count += 1
                if "usage" in data:
                    self._total_tokens += data["usage"].get("total_tokens", 0)
            
            return CompletionResponse(
                content=choice["message"]["content"],
                model=data.get("model", model),
                finish_reason=choice.get("finish_reason", "stop"),
                usage=data.get("usage", {}),
                tool_calls=choice["message"].get("tool_calls"),
                latency_ms=latency,
                raw_response=data
            )
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else str(e)
            return CompletionResponse(
                content=f"API Error: {error_body}",
                model=model,
                finish_reason="error",
                latency_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return CompletionResponse(
                content=f"Error: {str(e)}",
                model=model,
                finish_reason="error",
                latency_ms=(time.time() - start_time) * 1000
            )
    
    def stream_complete(
        self, 
        request: CompletionRequest
    ) -> Generator[str, None, None]:
        """Stream completion (simplified)."""
        response = self.complete(request)
        yield response.content


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.api_key = config.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
        self.base_url = config.get("base_url", "https://api.anthropic.com/v1")
        self.default_model = config.get("default_model", "claude-3-opus-20240229")
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.ANTHROPIC
    
    @property
    def available_models(self) -> List[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022"
        ]
    
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Generate completion using Anthropic API."""
        import time
        
        if not self.api_key:
            return CompletionResponse(
                content="Error: Anthropic API key not configured",
                model=request.model or self.default_model,
                finish_reason="error"
            )
        
        start_time = time.time()
        model = request.model or self.default_model
        
        try:
            import urllib.request
            import urllib.error
            
            # Extract system message
            system_content = ""
            messages = []
            for msg in request.messages:
                if msg.role == "system":
                    system_content = msg.content
                else:
                    messages.append({"role": msg.role, "content": msg.content})
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": request.max_tokens
            }
            
            if system_content:
                payload["system"] = system_content
            
            if request.tools:
                payload["tools"] = request.tools
            
            req = urllib.request.Request(
                f"{self.base_url}/messages",
                data=json.dumps(payload).encode(),
                headers=headers,
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                data = json.loads(response.read().decode())
            
            latency = (time.time() - start_time) * 1000
            
            # Extract content from response
            content = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    content += block.get("text", "")
            
            with self._lock:
                self._request_count += 1
                usage = data.get("usage", {})
                self._total_tokens += usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
            
            return CompletionResponse(
                content=content,
                model=data.get("model", model),
                finish_reason=data.get("stop_reason", "stop"),
                usage={
                    "prompt_tokens": usage.get("input_tokens", 0),
                    "completion_tokens": usage.get("output_tokens", 0),
                    "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                },
                latency_ms=latency,
                raw_response=data
            )
            
        except Exception as e:
            return CompletionResponse(
                content=f"Error: {str(e)}",
                model=model,
                finish_reason="error",
                latency_ms=(time.time() - start_time) * 1000
            )
    
    def stream_complete(
        self, 
        request: CompletionRequest
    ) -> Generator[str, None, None]:
        """Stream completion (simplified)."""
        response = self.complete(request)
        yield response.content


class LLMRouter:
    """
    Routes requests to appropriate LLM providers.
    
    Features:
    - Provider selection by capability
    - Fallback handling
    - Load balancing
    - Cost optimization
    """
    
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.default_provider: Optional[str] = None
        self._fallback_chain: List[str] = []
    
    def register_provider(
        self,
        name: str,
        provider: LLMProvider,
        is_default: bool = False
    ):
        """Register an LLM provider."""
        self.providers[name] = provider
        if is_default or not self.default_provider:
            self.default_provider = name
        print(f"[LLMRouter] Registered provider: {name} ({provider.provider_type.value})")
    
    def set_fallback_chain(self, providers: List[str]):
        """Set the fallback chain for failed requests."""
        self._fallback_chain = providers
    
    def complete(
        self,
        request: CompletionRequest,
        provider_name: str = None,
        use_fallback: bool = True
    ) -> CompletionResponse:
        """Route completion request to a provider."""
        provider_name = provider_name or self.default_provider
        
        if not provider_name or provider_name not in self.providers:
            return CompletionResponse(
                content="Error: No provider available",
                model="none",
                finish_reason="error"
            )
        
        # Try primary provider
        response = self.providers[provider_name].complete(request)
        
        # Use fallback if failed
        if use_fallback and response.finish_reason == "error":
            for fallback_name in self._fallback_chain:
                if fallback_name != provider_name and fallback_name in self.providers:
                    response = self.providers[fallback_name].complete(request)
                    if response.finish_reason != "error":
                        break
        
        return response
    
    def chat(
        self,
        message: str,
        provider_name: str = None,
        **kwargs
    ) -> str:
        """Simple chat interface."""
        provider_name = provider_name or self.default_provider
        if provider_name and provider_name in self.providers:
            return self.providers[provider_name].chat(message, **kwargs)
        return "Error: No provider available"
    
    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """Get a provider by name."""
        return self.providers.get(name)
    
    def list_providers(self) -> List[Dict[str, Any]]:
        """List all registered providers."""
        return [
            {
                "name": name,
                "type": provider.provider_type.value,
                "models": provider.available_models,
                "stats": provider.get_stats()
            }
            for name, provider in self.providers.items()
        ]


# Global router instance
_router = LLMRouter()


def get_provider(name: str = None) -> Optional[LLMProvider]:
    """Get a provider from the global router."""
    if name:
        return _router.get_provider(name)
    return _router.get_provider(_router.default_provider) if _router.default_provider else None


def register_provider(name: str, provider: LLMProvider, is_default: bool = False):
    """Register a provider with the global router."""
    _router.register_provider(name, provider, is_default)


def chat(message: str, provider: str = None, **kwargs) -> str:
    """Simple chat using global router."""
    return _router.chat(message, provider, **kwargs)


def complete(request: CompletionRequest, provider: str = None) -> CompletionResponse:
    """Complete using global router."""
    return _router.complete(request, provider)
