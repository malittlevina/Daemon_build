# unimind/models/native/embeddings.py
# Native Embedding System - Local text embeddings without external APIs

import math
import hashlib
import json
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import re


@dataclass
class EmbeddingConfig:
    """Configuration for embedding models."""
    dimension: int = 384
    max_seq_length: int = 512
    normalize: bool = True
    pooling: str = "mean"  # "mean", "max", "cls"
    

@dataclass
class EmbeddingResult:
    """Result from embedding generation."""
    embedding: List[float]
    text: str
    tokens_used: int
    model: str
    processing_time_ms: float = 0.0
    

class TFIDFEmbedding:
    """
    TF-IDF based embedding generator.
    
    A simple but effective embedding method that doesn't require
    neural networks. Good for semantic similarity when vocabulary
    is relatively fixed.
    """
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vocabulary: Dict[str, int] = {}
        self.idf_scores: Dict[str, float] = {}
        self.document_count = 0
        
    def fit(self, documents: List[str]):
        """
        Fit the TF-IDF model on documents.
        
        Args:
            documents: List of training documents
        """
        self.document_count = len(documents)
        word_doc_freq = {}
        
        # Build vocabulary and document frequencies
        for doc in documents:
            words = self._tokenize(doc)
            unique_words = set(words)
            
            for word in unique_words:
                if word not in self.vocabulary:
                    self.vocabulary[word] = len(self.vocabulary)
                word_doc_freq[word] = word_doc_freq.get(word, 0) + 1
                
        # Calculate IDF scores
        for word, doc_freq in word_doc_freq.items():
            self.idf_scores[word] = math.log(self.document_count / (doc_freq + 1)) + 1
            
        print(f"[TFIDFEmbedding] Fitted on {len(documents)} docs, vocab size: {len(self.vocabulary)}")
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        return words
        
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        words = self._tokenize(text)
        word_counts = {}
        
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
            
        # Calculate TF-IDF scores
        tfidf = {}
        for word, count in word_counts.items():
            tf = count / len(words) if words else 0
            idf = self.idf_scores.get(word, 1.0)
            tfidf[word] = tf * idf
            
        # Project to fixed dimension using hashing
        embedding = [0.0] * self.dimension
        
        for word, score in tfidf.items():
            # Hash word to get dimension indices
            hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
            indices = [
                hash_val % self.dimension,
                (hash_val >> 8) % self.dimension,
                (hash_val >> 16) % self.dimension,
            ]
            sign = 1 if (hash_val >> 24) % 2 == 0 else -1
            
            for idx in indices:
                embedding[idx] += sign * score
                
        # Normalize
        norm = math.sqrt(sum(x * x for x in embedding))
        if norm > 0:
            embedding = [x / norm for x in embedding]
            
        return embedding
        
    def save(self, path: str):
        """Save model to file."""
        data = {
            "dimension": self.dimension,
            "vocabulary": self.vocabulary,
            "idf_scores": self.idf_scores,
            "document_count": self.document_count
        }
        with open(path, "w") as f:
            json.dump(data, f)
            
    def load(self, path: str):
        """Load model from file."""
        with open(path) as f:
            data = json.load(f)
        self.dimension = data["dimension"]
        self.vocabulary = data["vocabulary"]
        self.idf_scores = data["idf_scores"]
        self.document_count = data["document_count"]


class Word2VecEmbedding:
    """
    Simple Word2Vec-style embeddings.
    
    Uses skip-gram with negative sampling (simplified).
    Can be trained on local text data.
    """
    
    def __init__(self, dimension: int = 100, window: int = 5):
        self.dimension = dimension
        self.window = window
        self.vocabulary: Dict[str, int] = {}
        self.embeddings: List[List[float]] = []
        self.word_counts: Dict[str, int] = {}
        
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text."""
        return re.findall(r'\b\w+\b', text.lower())
        
    def train(
        self,
        texts: List[str],
        epochs: int = 5,
        learning_rate: float = 0.025,
        min_count: int = 5
    ):
        """
        Train Word2Vec embeddings.
        
        Args:
            texts: Training texts
            epochs: Number of training epochs
            learning_rate: Learning rate
            min_count: Minimum word frequency
        """
        print(f"[Word2VecEmbedding] Training on {len(texts)} texts")
        
        # Build vocabulary
        for text in texts:
            words = self._tokenize(text)
            for word in words:
                self.word_counts[word] = self.word_counts.get(word, 0) + 1
                
        # Filter by min_count
        for word, count in self.word_counts.items():
            if count >= min_count:
                self.vocabulary[word] = len(self.vocabulary)
                
        # Initialize embeddings
        vocab_size = len(self.vocabulary)
        self.embeddings = [
            [random.gauss(0, 0.1) for _ in range(self.dimension)]
            for _ in range(vocab_size)
        ]
        
        # Context embeddings (for training)
        context_embeddings = [
            [random.gauss(0, 0.1) for _ in range(self.dimension)]
            for _ in range(vocab_size)
        ]
        
        # Training loop (simplified skip-gram)
        for epoch in range(epochs):
            total_loss = 0.0
            pairs = 0
            
            for text in texts:
                words = self._tokenize(text)
                word_ids = [self.vocabulary.get(w) for w in words]
                word_ids = [w for w in word_ids if w is not None]
                
                for i, center_id in enumerate(word_ids):
                    # Context window
                    start = max(0, i - self.window)
                    end = min(len(word_ids), i + self.window + 1)
                    
                    for j in range(start, end):
                        if i == j:
                            continue
                            
                        context_id = word_ids[j]
                        
                        # Positive sample update
                        center_emb = self.embeddings[center_id]
                        context_emb = context_embeddings[context_id]
                        
                        # Dot product
                        dot = sum(c * ctx for c, ctx in zip(center_emb, context_emb))
                        sigmoid = 1 / (1 + math.exp(-dot))
                        
                        # Update
                        grad = learning_rate * (1 - sigmoid)
                        for d in range(self.dimension):
                            self.embeddings[center_id][d] += grad * context_emb[d]
                            context_embeddings[context_id][d] += grad * center_emb[d]
                            
                        total_loss += -math.log(sigmoid + 1e-10)
                        pairs += 1
                        
            if epoch % 1 == 0:
                avg_loss = total_loss / pairs if pairs > 0 else 0
                print(f"  Epoch {epoch + 1}/{epochs}: loss = {avg_loss:.4f}")
                
        print(f"[Word2VecEmbedding] Training complete. Vocab: {len(self.vocabulary)}")
        
    def embed_word(self, word: str) -> Optional[List[float]]:
        """Get embedding for a single word."""
        word_id = self.vocabulary.get(word.lower())
        if word_id is not None:
            return self.embeddings[word_id]
        return None
        
    def embed(self, text: str, pooling: str = "mean") -> List[float]:
        """
        Get embedding for text.
        
        Args:
            text: Input text
            pooling: "mean", "max", or "sum"
            
        Returns:
            Text embedding
        """
        words = self._tokenize(text)
        word_embeddings = []
        
        for word in words:
            emb = self.embed_word(word)
            if emb is not None:
                word_embeddings.append(emb)
                
        if not word_embeddings:
            return [0.0] * self.dimension
            
        # Pool embeddings
        if pooling == "mean":
            result = [
                sum(emb[d] for emb in word_embeddings) / len(word_embeddings)
                for d in range(self.dimension)
            ]
        elif pooling == "max":
            result = [
                max(emb[d] for emb in word_embeddings)
                for d in range(self.dimension)
            ]
        else:  # sum
            result = [
                sum(emb[d] for emb in word_embeddings)
                for d in range(self.dimension)
            ]
            
        # Normalize
        norm = math.sqrt(sum(x * x for x in result))
        if norm > 0:
            result = [x / norm for x in result]
            
        return result
        
    def similarity(self, word1: str, word2: str) -> float:
        """Calculate cosine similarity between words."""
        emb1 = self.embed_word(word1)
        emb2 = self.embed_word(word2)
        
        if emb1 is None or emb2 is None:
            return 0.0
            
        dot = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = math.sqrt(sum(a * a for a in emb1))
        norm2 = math.sqrt(sum(b * b for b in emb2))
        
        return dot / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0
        
    def most_similar(self, word: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Find most similar words."""
        emb = self.embed_word(word)
        if emb is None:
            return []
            
        similarities = []
        for other_word, idx in self.vocabulary.items():
            if other_word == word.lower():
                continue
            other_emb = self.embeddings[idx]
            sim = sum(a * b for a, b in zip(emb, other_emb))
            similarities.append((other_word, sim))
            
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
        
    def save(self, path: str):
        """Save model."""
        data = {
            "dimension": self.dimension,
            "vocabulary": self.vocabulary,
            "embeddings": self.embeddings
        }
        with open(path, "w") as f:
            json.dump(data, f)
            
    def load(self, path: str):
        """Load model."""
        with open(path) as f:
            data = json.load(f)
        self.dimension = data["dimension"]
        self.vocabulary = data["vocabulary"]
        self.embeddings = data["embeddings"]


class SentenceEmbedding:
    """
    Sentence-level embedding using simple neural approach.
    
    Combines word embeddings with positional information
    and uses attention-like mechanism for sentence representation.
    """
    
    def __init__(self, dimension: int = 384, max_length: int = 128):
        self.dimension = dimension
        self.max_length = max_length
        self.word_embeddings = Word2VecEmbedding(dimension=dimension)
        self.position_embeddings: List[List[float]] = []
        self._init_position_embeddings()
        
    def _init_position_embeddings(self):
        """Initialize sinusoidal position embeddings."""
        for pos in range(self.max_length):
            pos_emb = []
            for i in range(self.dimension):
                if i % 2 == 0:
                    pos_emb.append(math.sin(pos / (10000 ** (i / self.dimension))))
                else:
                    pos_emb.append(math.cos(pos / (10000 ** ((i - 1) / self.dimension))))
            self.position_embeddings.append(pos_emb)
            
    def train(self, texts: List[str], **kwargs):
        """Train underlying word embeddings."""
        self.word_embeddings.train(texts, **kwargs)
        
    def embed(self, text: str) -> List[float]:
        """
        Generate sentence embedding.
        
        Args:
            text: Input sentence
            
        Returns:
            Sentence embedding vector
        """
        words = re.findall(r'\b\w+\b', text.lower())[:self.max_length]
        
        if not words:
            return [0.0] * self.dimension
            
        # Get word embeddings with position
        token_embeddings = []
        
        for pos, word in enumerate(words):
            word_emb = self.word_embeddings.embed_word(word)
            if word_emb is None:
                word_emb = [0.0] * self.dimension
                
            # Add position embedding
            pos_emb = self.position_embeddings[pos]
            combined = [w + p for w, p in zip(word_emb, pos_emb)]
            token_embeddings.append(combined)
            
        # Simple attention-like pooling
        # Calculate importance scores based on word embedding norms
        scores = []
        for emb in token_embeddings:
            norm = math.sqrt(sum(x * x for x in emb))
            scores.append(norm)
            
        # Softmax
        max_score = max(scores) if scores else 0
        exp_scores = [math.exp(s - max_score) for s in scores]
        total = sum(exp_scores)
        weights = [s / total for s in exp_scores]
        
        # Weighted sum
        result = [0.0] * self.dimension
        for weight, emb in zip(weights, token_embeddings):
            for d in range(self.dimension):
                result[d] += weight * emb[d]
                
        # Normalize
        norm = math.sqrt(sum(x * x for x in result))
        if norm > 0:
            result = [x / norm for x in result]
            
        return result
        
    def batch_embed(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        return [self.embed(text) for text in texts]


class NativeEmbeddingEngine:
    """
    Main embedding engine for the daemon.
    
    Provides a unified interface for different embedding methods
    and handles caching, similarity search, etc.
    """
    
    def __init__(self, config: EmbeddingConfig = None):
        self.config = config or EmbeddingConfig()
        
        # Embedding models
        self.tfidf = TFIDFEmbedding(self.config.dimension)
        self.word2vec = Word2VecEmbedding(self.config.dimension)
        self.sentence = SentenceEmbedding(self.config.dimension, self.config.max_seq_length)
        
        # Embedding cache
        self.cache: Dict[str, List[float]] = {}
        self.cache_max_size = 10000
        
        # Stats
        self.stats = {
            "embeddings_generated": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Default model
        self.active_model = "tfidf"
        
    def train(self, texts: List[str], model: str = "all"):
        """
        Train embedding models on texts.
        
        Args:
            texts: Training texts
            model: "tfidf", "word2vec", "sentence", or "all"
        """
        if model in ["tfidf", "all"]:
            self.tfidf.fit(texts)
            
        if model in ["word2vec", "all"]:
            self.word2vec.train(texts)
            
        if model in ["sentence", "all"]:
            self.sentence.train(texts)
            
    def embed(
        self,
        text: str,
        model: str = None,
        use_cache: bool = True
    ) -> EmbeddingResult:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
            model: Embedding model to use (default: active_model)
            use_cache: Whether to use caching
            
        Returns:
            EmbeddingResult
        """
        import time
        start = time.time()
        
        model = model or self.active_model
        cache_key = f"{model}:{text[:100]}"
        
        # Check cache
        if use_cache and cache_key in self.cache:
            self.stats["cache_hits"] += 1
            return EmbeddingResult(
                embedding=self.cache[cache_key],
                text=text,
                tokens_used=len(text.split()),
                model=model,
                processing_time_ms=0
            )
            
        self.stats["cache_misses"] += 1
        
        # Generate embedding
        if model == "tfidf":
            embedding = self.tfidf.embed(text)
        elif model == "word2vec":
            embedding = self.word2vec.embed(text)
        elif model == "sentence":
            embedding = self.sentence.embed(text)
        else:
            embedding = self.tfidf.embed(text)
            
        # Normalize if configured
        if self.config.normalize:
            norm = math.sqrt(sum(x * x for x in embedding))
            if norm > 0:
                embedding = [x / norm for x in embedding]
                
        # Update cache
        if use_cache and len(self.cache) < self.cache_max_size:
            self.cache[cache_key] = embedding
            
        elapsed = (time.time() - start) * 1000
        self.stats["embeddings_generated"] += 1
        
        return EmbeddingResult(
            embedding=embedding,
            text=text,
            tokens_used=len(text.split()),
            model=model,
            processing_time_ms=elapsed
        )
        
    def batch_embed(
        self,
        texts: List[str],
        model: str = None
    ) -> List[EmbeddingResult]:
        """Embed multiple texts."""
        return [self.embed(text, model) for text in texts]
        
    def similarity(
        self,
        text1: str,
        text2: str,
        model: str = None
    ) -> float:
        """
        Calculate similarity between two texts.
        
        Returns:
            Cosine similarity (-1 to 1)
        """
        emb1 = self.embed(text1, model).embedding
        emb2 = self.embed(text2, model).embedding
        
        dot = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = math.sqrt(sum(a * a for a in emb1))
        norm2 = math.sqrt(sum(b * b for b in emb2))
        
        return dot / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0
        
    def find_similar(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5,
        model: str = None
    ) -> List[Tuple[str, float]]:
        """
        Find most similar texts from candidates.
        
        Args:
            query: Query text
            candidates: List of candidate texts
            top_k: Number of results
            model: Embedding model to use
            
        Returns:
            List of (text, similarity) tuples
        """
        query_emb = self.embed(query, model).embedding
        
        results = []
        for candidate in candidates:
            cand_emb = self.embed(candidate, model).embedding
            
            dot = sum(a * b for a, b in zip(query_emb, cand_emb))
            norm1 = math.sqrt(sum(a * a for a in query_emb))
            norm2 = math.sqrt(sum(b * b for b in cand_emb))
            sim = dot / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0
            
            results.append((candidate, sim))
            
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
        
    def clear_cache(self):
        """Clear embedding cache."""
        self.cache.clear()
        
    def save(self, directory: str):
        """Save all models."""
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        
        self.tfidf.save(str(path / "tfidf.json"))
        self.word2vec.save(str(path / "word2vec.json"))
        
    def load(self, directory: str):
        """Load all models."""
        path = Path(directory)
        
        if (path / "tfidf.json").exists():
            self.tfidf.load(str(path / "tfidf.json"))
            
        if (path / "word2vec.json").exists():
            self.word2vec.load(str(path / "word2vec.json"))
            
    def get_stats(self) -> Dict:
        """Get engine statistics."""
        return {
            **self.stats,
            "cache_size": len(self.cache),
            "active_model": self.active_model,
            "dimension": self.config.dimension
        }


# Convenience functions
def create_embedding_engine(dimension: int = 384) -> NativeEmbeddingEngine:
    """Create a native embedding engine."""
    config = EmbeddingConfig(dimension=dimension)
    return NativeEmbeddingEngine(config)


def quick_embed(text: str, dimension: int = 384) -> List[float]:
    """Quick embedding using TF-IDF (no training required)."""
    engine = TFIDFEmbedding(dimension)
    return engine.embed(text)
