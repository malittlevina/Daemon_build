# memory_tree/semantic_index.py
"""
Semantic Index - Vector-based semantic memory search

Provides semantic similarity search using:
- TF-IDF based embeddings (lightweight)
- Optional dense embeddings via external models
- Approximate nearest neighbor search
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import math
import re
from collections import Counter
import json
import os


@dataclass
class IndexedDocument:
    """A document indexed for semantic search."""
    doc_id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    tf_idf_vector: Optional[Dict[str, float]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class SemanticIndex:
    """
    Semantic index for memory search.
    
    Features:
    - TF-IDF based similarity (no external dependencies)
    - Incremental indexing
    - Efficient k-NN search
    - Optional dense embedding support
    """
    
    def __init__(self, storage_path: str = "memory_tree/index"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Document store
        self.documents: Dict[str, IndexedDocument] = {}
        
        # Inverted index for fast lookup
        self.inverted_index: Dict[str, Dict[str, float]] = {}  # term -> {doc_id: tf-idf}
        
        # Document frequency for IDF calculation
        self.document_frequency: Dict[str, int] = {}
        
        # Vocabulary
        self.vocabulary: set = set()
        
        # IDF cache
        self._idf_cache: Dict[str, float] = {}
        
        # Stopwords
        self.stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare",
            "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
            "from", "as", "into", "through", "during", "before", "after", "above",
            "below", "between", "under", "again", "further", "then", "once", "here",
            "there", "when", "where", "why", "how", "all", "each", "few", "more",
            "most", "other", "some", "such", "no", "nor", "not", "only", "own",
            "same", "so", "than", "too", "very", "just", "and", "but", "if", "or",
            "because", "until", "while", "although", "though", "after", "before",
            "that", "which", "who", "whom", "this", "these", "those", "what",
            "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you",
            "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself",
            "she", "her", "hers", "herself", "it", "its", "itself", "they", "them",
            "their", "theirs", "themselves", "am"
        }
        
        # Load existing index
        self._load_index()
        
        print(f"[SemanticIndex] Initialized with {len(self.documents)} documents.")
    
    def add_document(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Add or update a document in the index."""
        if not content.strip():
            return False
        
        # Tokenize and compute TF
        tokens = self._tokenize(content)
        if not tokens:
            return False
        
        term_freq = Counter(tokens)
        
        # Update document frequency (if new doc or updating)
        old_terms = set()
        if doc_id in self.documents:
            old_doc = self.documents[doc_id]
            if old_doc.tf_idf_vector:
                old_terms = set(old_doc.tf_idf_vector.keys())
        
        new_terms = set(term_freq.keys())
        
        # Update DF for removed terms
        for term in old_terms - new_terms:
            self.document_frequency[term] = max(0, self.document_frequency.get(term, 1) - 1)
        
        # Update DF for new terms
        for term in new_terms - old_terms:
            self.document_frequency[term] = self.document_frequency.get(term, 0) + 1
        
        self.vocabulary.update(new_terms)
        
        # Invalidate IDF cache
        self._idf_cache.clear()
        
        # Compute TF-IDF vector
        tf_idf = {}
        max_tf = max(term_freq.values())
        
        for term, freq in term_freq.items():
            tf = 0.5 + 0.5 * (freq / max_tf)  # Augmented TF
            idf = self._compute_idf(term)
            tf_idf[term] = tf * idf
        
        # Normalize vector
        magnitude = math.sqrt(sum(v ** 2 for v in tf_idf.values()))
        if magnitude > 0:
            tf_idf = {k: v / magnitude for k, v in tf_idf.items()}
        
        # Store document
        doc = IndexedDocument(
            doc_id=doc_id,
            content=content,
            metadata=metadata or {},
            tf_idf_vector=tf_idf
        )
        self.documents[doc_id] = doc
        
        # Update inverted index
        for term, weight in tf_idf.items():
            if term not in self.inverted_index:
                self.inverted_index[term] = {}
            self.inverted_index[term][doc_id] = weight
        
        return True
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the index."""
        if doc_id not in self.documents:
            return False
        
        doc = self.documents[doc_id]
        
        # Update inverted index
        if doc.tf_idf_vector:
            for term in doc.tf_idf_vector.keys():
                if term in self.inverted_index:
                    self.inverted_index[term].pop(doc_id, None)
                    if not self.inverted_index[term]:
                        del self.inverted_index[term]
                
                # Update document frequency
                self.document_frequency[term] = max(0, self.document_frequency.get(term, 1) - 1)
        
        del self.documents[doc_id]
        self._idf_cache.clear()
        
        return True
    
    def search(
        self,
        query: str,
        limit: int = 10,
        min_score: float = 0.1,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for documents similar to query.
        
        Returns list of (doc_id, score, metadata) tuples.
        """
        if not query.strip():
            return []
        
        # Tokenize query
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        
        # Compute query TF-IDF
        term_freq = Counter(query_tokens)
        max_tf = max(term_freq.values())
        
        query_vector = {}
        for term, freq in term_freq.items():
            tf = 0.5 + 0.5 * (freq / max_tf)
            idf = self._compute_idf(term)
            query_vector[term] = tf * idf
        
        # Normalize query vector
        magnitude = math.sqrt(sum(v ** 2 for v in query_vector.values()))
        if magnitude > 0:
            query_vector = {k: v / magnitude for k, v in query_vector.items()}
        
        # Score documents using inverted index
        doc_scores: Dict[str, float] = {}
        
        for term, weight in query_vector.items():
            if term in self.inverted_index:
                for doc_id, doc_weight in self.inverted_index[term].items():
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + weight * doc_weight
        
        # Filter and sort
        results = []
        for doc_id, score in doc_scores.items():
            if score < min_score:
                continue
            
            doc = self.documents.get(doc_id)
            if not doc:
                continue
            
            # Apply metadata filter
            if filter_metadata:
                if not all(
                    doc.metadata.get(k) == v
                    for k, v in filter_metadata.items()
                ):
                    continue
            
            results.append((doc_id, score, doc.metadata))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def find_similar(
        self,
        doc_id: str,
        limit: int = 5,
        min_score: float = 0.2
    ) -> List[Tuple[str, float]]:
        """Find documents similar to a given document."""
        doc = self.documents.get(doc_id)
        if not doc or not doc.tf_idf_vector:
            return []
        
        # Score all other documents
        results = []
        
        for other_id, other_doc in self.documents.items():
            if other_id == doc_id:
                continue
            
            if not other_doc.tf_idf_vector:
                continue
            
            # Cosine similarity
            score = self._cosine_similarity(doc.tf_idf_vector, other_doc.tf_idf_vector)
            
            if score >= min_score:
                results.append((other_id, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def get_keywords(self, doc_id: str, limit: int = 10) -> List[Tuple[str, float]]:
        """Get top keywords for a document."""
        doc = self.documents.get(doc_id)
        if not doc or not doc.tf_idf_vector:
            return []
        
        sorted_terms = sorted(
            doc.tf_idf_vector.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_terms[:limit]
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms."""
        # Lowercase and extract words
        text = text.lower()
        tokens = re.findall(r'\b[a-z][a-z0-9]*\b', text)
        
        # Remove stopwords and short tokens
        tokens = [t for t in tokens if t not in self.stopwords and len(t) > 2]
        
        return tokens
    
    def _compute_idf(self, term: str) -> float:
        """Compute IDF for a term."""
        if term in self._idf_cache:
            return self._idf_cache[term]
        
        n_docs = len(self.documents)
        if n_docs == 0:
            return 0
        
        df = self.document_frequency.get(term, 0)
        if df == 0:
            idf = 0
        else:
            idf = math.log((n_docs + 1) / (df + 1)) + 1  # Smoothed IDF
        
        self._idf_cache[term] = idf
        return idf
    
    def _cosine_similarity(
        self,
        vec1: Dict[str, float],
        vec2: Dict[str, float]
    ) -> float:
        """Compute cosine similarity between two sparse vectors."""
        # Both vectors should already be normalized
        common_terms = set(vec1.keys()) & set(vec2.keys())
        
        if not common_terms:
            return 0.0
        
        return sum(vec1[t] * vec2[t] for t in common_terms)
    
    def _save_index(self):
        """Save index to disk."""
        try:
            path = os.path.join(self.storage_path, "semantic_index.json")
            
            data = {
                "documents": {
                    doc_id: {
                        "content": doc.content[:1000],
                        "metadata": doc.metadata,
                        "tf_idf_vector": doc.tf_idf_vector
                    }
                    for doc_id, doc in self.documents.items()
                },
                "document_frequency": dict(self.document_frequency),
                "vocabulary_size": len(self.vocabulary)
            }
            
            with open(path, "w") as f:
                json.dump(data, f)
            
            print(f"[SemanticIndex] Saved index with {len(self.documents)} documents.")
            
        except Exception as e:
            print(f"[SemanticIndex] Error saving index: {e}")
    
    def _load_index(self):
        """Load index from disk."""
        try:
            path = os.path.join(self.storage_path, "semantic_index.json")
            
            if not os.path.exists(path):
                return
            
            with open(path, "r") as f:
                data = json.load(f)
            
            # Restore documents
            for doc_id, doc_data in data.get("documents", {}).items():
                doc = IndexedDocument(
                    doc_id=doc_id,
                    content=doc_data["content"],
                    metadata=doc_data.get("metadata", {}),
                    tf_idf_vector=doc_data.get("tf_idf_vector")
                )
                self.documents[doc_id] = doc
                
                # Rebuild inverted index
                if doc.tf_idf_vector:
                    for term, weight in doc.tf_idf_vector.items():
                        if term not in self.inverted_index:
                            self.inverted_index[term] = {}
                        self.inverted_index[term][doc_id] = weight
            
            # Restore document frequency
            self.document_frequency = data.get("document_frequency", {})
            self.vocabulary = set(self.document_frequency.keys())
            
            print(f"[SemanticIndex] Loaded index with {len(self.documents)} documents.")
            
        except Exception as e:
            print(f"[SemanticIndex] Error loading index: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "document_count": len(self.documents),
            "vocabulary_size": len(self.vocabulary),
            "inverted_index_terms": len(self.inverted_index),
            "avg_doc_length": sum(
                len(d.content.split()) for d in self.documents.values()
            ) / max(1, len(self.documents))
        }
