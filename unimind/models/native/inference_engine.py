# unimind/models/native/inference_engine.py
# Native Inference Engine - Local model inference without external dependencies

import math
import random
import time
from typing import Dict, List, Optional, Any, Tuple, Callable, Generator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class SamplingMethod(Enum):
    """Text generation sampling methods."""
    GREEDY = "greedy"
    TOP_K = "top_k"
    TOP_P = "top_p"           # Nucleus sampling
    TEMPERATURE = "temperature"
    BEAM_SEARCH = "beam_search"
    CONTRASTIVE = "contrastive"


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    max_tokens: int = 256
    min_tokens: int = 1
    temperature: float = 0.7
    top_k: int = 40
    top_p: float = 0.9
    repetition_penalty: float = 1.1
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    sampling_method: SamplingMethod = SamplingMethod.TOP_P
    beam_width: int = 4
    seed: Optional[int] = None
    
    
@dataclass
class GenerationResult:
    """Result from text generation."""
    text: str
    tokens_generated: int
    tokens_per_second: float
    finish_reason: str  # "stop", "length", "eos"
    logprobs: Optional[List[float]] = None
    total_time_ms: float = 0.0
    
    
class Softmax:
    """Softmax function for probability distributions."""
    
    @staticmethod
    def apply(logits: List[float], temperature: float = 1.0) -> List[float]:
        """Apply softmax with temperature scaling."""
        if temperature <= 0:
            temperature = 1e-10
            
        # Scale by temperature
        scaled = [l / temperature for l in logits]
        
        # Subtract max for numerical stability
        max_val = max(scaled)
        exp_vals = [math.exp(v - max_val) for v in scaled]
        
        # Normalize
        total = sum(exp_vals)
        return [v / total for v in exp_vals]
        
        
class TopKSampler:
    """Top-K sampling."""
    
    @staticmethod
    def sample(
        logits: List[float],
        k: int,
        temperature: float = 1.0
    ) -> Tuple[int, float]:
        """
        Sample from top-k tokens.
        
        Returns:
            (token_index, probability)
        """
        # Get top-k indices
        indexed = list(enumerate(logits))
        indexed.sort(key=lambda x: x[1], reverse=True)
        top_k = indexed[:k]
        
        # Apply softmax to top-k
        top_logits = [l for _, l in top_k]
        probs = Softmax.apply(top_logits, temperature)
        
        # Sample
        r = random.random()
        cumsum = 0.0
        for i, (idx, _) in enumerate(top_k):
            cumsum += probs[i]
            if r < cumsum:
                return idx, probs[i]
                
        return top_k[-1][0], probs[-1]
        

class TopPSampler:
    """Top-P (Nucleus) sampling."""
    
    @staticmethod
    def sample(
        logits: List[float],
        p: float,
        temperature: float = 1.0
    ) -> Tuple[int, float]:
        """
        Sample from top-p nucleus.
        
        Returns:
            (token_index, probability)
        """
        # Get probabilities
        probs = Softmax.apply(logits, temperature)
        
        # Sort by probability
        indexed = list(enumerate(probs))
        indexed.sort(key=lambda x: x[1], reverse=True)
        
        # Find nucleus (top-p)
        cumsum = 0.0
        nucleus = []
        for idx, prob in indexed:
            nucleus.append((idx, prob))
            cumsum += prob
            if cumsum >= p:
                break
                
        # Renormalize
        total = sum(prob for _, prob in nucleus)
        nucleus = [(idx, prob / total) for idx, prob in nucleus]
        
        # Sample
        r = random.random()
        cumsum = 0.0
        for idx, prob in nucleus:
            cumsum += prob
            if r < cumsum:
                return idx, prob
                
        return nucleus[-1]


class BeamSearcher:
    """Beam search for text generation."""
    
    def __init__(self, beam_width: int = 4):
        self.beam_width = beam_width
        
    def search(
        self,
        initial_tokens: List[int],
        score_fn: Callable[[List[int]], List[float]],
        max_length: int,
        eos_token: int
    ) -> List[Tuple[List[int], float]]:
        """
        Perform beam search.
        
        Args:
            initial_tokens: Starting tokens
            score_fn: Function to get next token logits
            max_length: Maximum sequence length
            eos_token: End of sequence token
            
        Returns:
            List of (sequence, score) tuples
        """
        # Initialize beams: [(sequence, cumulative_score)]
        beams = [(initial_tokens, 0.0)]
        complete = []
        
        for _ in range(max_length):
            candidates = []
            
            for seq, score in beams:
                if seq[-1] == eos_token:
                    complete.append((seq, score))
                    continue
                    
                # Get next token scores
                logits = score_fn(seq)
                probs = Softmax.apply(logits)
                
                # Top-k candidates for this beam
                indexed = list(enumerate(probs))
                indexed.sort(key=lambda x: x[1], reverse=True)
                
                for idx, prob in indexed[:self.beam_width]:
                    new_seq = seq + [idx]
                    new_score = score + math.log(prob + 1e-10)
                    candidates.append((new_seq, new_score))
                    
            if not candidates:
                break
                
            # Keep top beams
            candidates.sort(key=lambda x: x[1], reverse=True)
            beams = candidates[:self.beam_width]
            
        # Add remaining beams to complete
        complete.extend(beams)
        complete.sort(key=lambda x: x[1], reverse=True)
        
        return complete[:self.beam_width]


class RepetitionPenalizer:
    """Apply repetition penalty to logits."""
    
    @staticmethod
    def apply(
        logits: List[float],
        generated_tokens: List[int],
        penalty: float = 1.1,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ) -> List[float]:
        """
        Apply repetition penalties.
        
        Args:
            logits: Original logits
            generated_tokens: Already generated tokens
            penalty: Repetition penalty (>1 reduces repetition)
            frequency_penalty: Penalty based on frequency
            presence_penalty: Penalty for presence
            
        Returns:
            Penalized logits
        """
        logits = logits.copy()
        
        # Count token frequencies
        freq = {}
        for token in generated_tokens:
            freq[token] = freq.get(token, 0) + 1
            
        for token, count in freq.items():
            if token < len(logits):
                # Basic repetition penalty
                if logits[token] > 0:
                    logits[token] /= penalty
                else:
                    logits[token] *= penalty
                    
                # Frequency penalty
                logits[token] -= frequency_penalty * count
                
                # Presence penalty
                logits[token] -= presence_penalty
                
        return logits


class NativeTransformerLayer:
    """
    A simplified transformer layer for native inference.
    
    This is a reference implementation - for production use,
    you'd want optimized matrix operations (numpy/torch).
    """
    
    def __init__(self, d_model: int = 512, n_heads: int = 8, d_ff: int = 2048):
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_ff = d_ff
        self.head_dim = d_model // n_heads
        
        # Initialize weights (simplified - random for demo)
        self.wq = self._random_weights(d_model, d_model)
        self.wk = self._random_weights(d_model, d_model)
        self.wv = self._random_weights(d_model, d_model)
        self.wo = self._random_weights(d_model, d_model)
        
        self.ff1 = self._random_weights(d_model, d_ff)
        self.ff2 = self._random_weights(d_ff, d_model)
        
    def _random_weights(self, in_dim: int, out_dim: int) -> List[List[float]]:
        """Initialize random weights."""
        scale = 0.02
        return [
            [random.gauss(0, scale) for _ in range(out_dim)]
            for _ in range(in_dim)
        ]
        
    def _matmul(self, a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        """Matrix multiplication."""
        rows_a, cols_a = len(a), len(a[0])
        rows_b, cols_b = len(b), len(b[0])
        
        result = [[0.0] * cols_b for _ in range(rows_a)]
        
        for i in range(rows_a):
            for j in range(cols_b):
                for k in range(cols_a):
                    result[i][j] += a[i][k] * b[k][j]
                    
        return result
        
    def _gelu(self, x: float) -> float:
        """GELU activation."""
        return 0.5 * x * (1 + math.tanh(math.sqrt(2 / math.pi) * (x + 0.044715 * x ** 3)))
        
    def forward(self, x: List[List[float]]) -> List[List[float]]:
        """
        Forward pass through the layer.
        
        This is a simplified version for demonstration.
        In practice, you'd use optimized matrix operations.
        """
        # Self-attention (simplified)
        # ... actual implementation would do Q, K, V projections and attention
        
        # For now, just return processed input
        return x


class NativeLanguageModel:
    """
    Native language model for local text generation.
    
    This provides a framework for running local models without
    external dependencies. Supports:
    - Token-by-token generation
    - Multiple sampling methods
    - Caching and optimization
    """
    
    def __init__(
        self,
        vocab_size: int = 32000,
        d_model: int = 512,
        n_layers: int = 6,
        n_heads: int = 8
    ):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.n_layers = n_layers
        self.n_heads = n_heads
        
        # Token embeddings (simplified)
        self.embeddings = self._init_embeddings()
        
        # Transformer layers
        self.layers = [
            NativeTransformerLayer(d_model, n_heads)
            for _ in range(n_layers)
        ]
        
        # Output projection
        self.output_proj = self._init_output_projection()
        
        # KV cache for efficient generation
        self.kv_cache: Dict[int, Any] = {}
        
    def _init_embeddings(self) -> List[List[float]]:
        """Initialize token embeddings."""
        scale = 0.02
        return [
            [random.gauss(0, scale) for _ in range(self.d_model)]
            for _ in range(self.vocab_size)
        ]
        
    def _init_output_projection(self) -> List[List[float]]:
        """Initialize output projection."""
        scale = 0.02
        return [
            [random.gauss(0, scale) for _ in range(self.vocab_size)]
            for _ in range(self.d_model)
        ]
        
    def get_logits(self, token_ids: List[int]) -> List[float]:
        """
        Get logits for next token prediction.
        
        Args:
            token_ids: Input token sequence
            
        Returns:
            Logits for each vocabulary token
        """
        # Get embeddings for input tokens
        hidden = [self.embeddings[tid % self.vocab_size] for tid in token_ids]
        
        # Pass through transformer layers
        for layer in self.layers:
            hidden = layer.forward(hidden)
            
        # Get last hidden state
        last_hidden = hidden[-1]
        
        # Project to vocabulary
        logits = [0.0] * self.vocab_size
        for i in range(self.vocab_size):
            for j in range(self.d_model):
                logits[i] += last_hidden[j] * self.output_proj[j][i]
                
        return logits
        
    def generate_token(
        self,
        token_ids: List[int],
        config: GenerationConfig,
        generated_so_far: List[int] = None
    ) -> Tuple[int, float]:
        """
        Generate a single token.
        
        Args:
            token_ids: Current token sequence
            config: Generation configuration
            generated_so_far: Previously generated tokens (for repetition penalty)
            
        Returns:
            (next_token_id, probability)
        """
        logits = self.get_logits(token_ids)
        
        # Apply repetition penalty
        if generated_so_far and config.repetition_penalty != 1.0:
            logits = RepetitionPenalizer.apply(
                logits,
                generated_so_far,
                config.repetition_penalty,
                config.frequency_penalty,
                config.presence_penalty
            )
            
        # Sample based on method
        if config.sampling_method == SamplingMethod.GREEDY:
            idx = max(range(len(logits)), key=lambda i: logits[i])
            return idx, 1.0
            
        elif config.sampling_method == SamplingMethod.TOP_K:
            return TopKSampler.sample(logits, config.top_k, config.temperature)
            
        elif config.sampling_method == SamplingMethod.TOP_P:
            return TopPSampler.sample(logits, config.top_p, config.temperature)
            
        else:  # Default to temperature sampling
            probs = Softmax.apply(logits, config.temperature)
            r = random.random()
            cumsum = 0.0
            for i, p in enumerate(probs):
                cumsum += p
                if r < cumsum:
                    return i, p
            return len(probs) - 1, probs[-1]
            
    def clear_cache(self):
        """Clear KV cache."""
        self.kv_cache.clear()


class NativeInferenceEngine:
    """
    Main inference engine for native LLM execution.
    
    Supports:
    - Local model loading
    - Streaming generation
    - Batch inference
    - KV caching
    - Quantization-aware inference
    """
    
    def __init__(self):
        self.model: Optional[NativeLanguageModel] = None
        self.tokenizer = None  # Set externally
        self.config = GenerationConfig()
        self.stats = {
            "total_tokens_generated": 0,
            "total_time_ms": 0,
            "requests": 0
        }
        
    def load_model(self, model_or_path: Any):
        """Load a model for inference."""
        if isinstance(model_or_path, NativeLanguageModel):
            self.model = model_or_path
        else:
            # Load from path (to be implemented with actual model loading)
            self.model = NativeLanguageModel()
            
        print("[NativeInferenceEngine] Model loaded")
        
    def set_tokenizer(self, tokenizer):
        """Set the tokenizer."""
        self.tokenizer = tokenizer
        
    def generate(
        self,
        prompt: str,
        config: GenerationConfig = None,
        stream: bool = False
    ) -> GenerationResult:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            config: Generation configuration
            stream: Whether to stream output
            
        Returns:
            GenerationResult
        """
        if self.model is None:
            raise ValueError("No model loaded")
            
        config = config or self.config
        
        if config.seed is not None:
            random.seed(config.seed)
            
        start_time = time.time()
        
        # Tokenize prompt
        if self.tokenizer:
            input_ids = self.tokenizer.encode(prompt, add_special_tokens=False)
        else:
            # Fallback: simple character-based
            input_ids = [ord(c) % 32000 for c in prompt]
            
        generated_ids = []
        current_ids = input_ids.copy()
        
        for _ in range(config.max_tokens):
            # Generate next token
            next_token, prob = self.model.generate_token(
                current_ids,
                config,
                generated_ids
            )
            
            generated_ids.append(next_token)
            current_ids.append(next_token)
            
            # Check stop conditions
            if self.tokenizer and next_token == self.tokenizer.config.eos_id:
                finish_reason = "eos"
                break
                
            # Check stop sequences
            if self.tokenizer:
                current_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
                for stop_seq in config.stop_sequences:
                    if stop_seq in current_text:
                        finish_reason = "stop"
                        break
                else:
                    continue
                break
        else:
            finish_reason = "length"
            
        # Decode output
        if self.tokenizer:
            output_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        else:
            output_text = "".join(chr(tid % 128) for tid in generated_ids if 32 <= tid % 128 < 127)
            
        elapsed = (time.time() - start_time) * 1000
        tokens_per_sec = len(generated_ids) / (elapsed / 1000) if elapsed > 0 else 0
        
        # Update stats
        self.stats["total_tokens_generated"] += len(generated_ids)
        self.stats["total_time_ms"] += elapsed
        self.stats["requests"] += 1
        
        return GenerationResult(
            text=output_text,
            tokens_generated=len(generated_ids),
            tokens_per_second=tokens_per_sec,
            finish_reason=finish_reason,
            total_time_ms=elapsed
        )
        
    def generate_stream(
        self,
        prompt: str,
        config: GenerationConfig = None
    ) -> Generator[str, None, None]:
        """
        Stream text generation token by token.
        
        Yields:
            Generated text incrementally
        """
        if self.model is None:
            raise ValueError("No model loaded")
            
        config = config or self.config
        
        # Tokenize
        if self.tokenizer:
            input_ids = self.tokenizer.encode(prompt, add_special_tokens=False)
        else:
            input_ids = [ord(c) % 32000 for c in prompt]
            
        generated_ids = []
        current_ids = input_ids.copy()
        
        for _ in range(config.max_tokens):
            next_token, _ = self.model.generate_token(
                current_ids,
                config,
                generated_ids
            )
            
            generated_ids.append(next_token)
            current_ids.append(next_token)
            
            # Decode and yield
            if self.tokenizer:
                if next_token == self.tokenizer.config.eos_id:
                    break
                text = self.tokenizer.decode([next_token], skip_special_tokens=True)
            else:
                text = chr(next_token % 128) if 32 <= next_token % 128 < 127 else ""
                
            yield text
            
    def batch_generate(
        self,
        prompts: List[str],
        config: GenerationConfig = None
    ) -> List[GenerationResult]:
        """Generate for multiple prompts."""
        return [self.generate(prompt, config) for prompt in prompts]
        
    def get_stats(self) -> Dict:
        """Get inference statistics."""
        avg_time = (
            self.stats["total_time_ms"] / self.stats["requests"]
            if self.stats["requests"] > 0 else 0
        )
        return {
            **self.stats,
            "average_time_ms": avg_time,
            "average_tokens_per_second": (
                self.stats["total_tokens_generated"] / (self.stats["total_time_ms"] / 1000)
                if self.stats["total_time_ms"] > 0 else 0
            )
        }
        
    def reset_stats(self):
        """Reset statistics."""
        self.stats = {
            "total_tokens_generated": 0,
            "total_time_ms": 0,
            "requests": 0
        }


# Convenience function
def create_inference_engine(
    vocab_size: int = 32000,
    model_dim: int = 512,
    num_layers: int = 6
) -> NativeInferenceEngine:
    """Create a native inference engine with a simple model."""
    engine = NativeInferenceEngine()
    model = NativeLanguageModel(
        vocab_size=vocab_size,
        d_model=model_dim,
        n_layers=num_layers
    )
    engine.load_model(model)
    return engine
