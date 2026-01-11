# nlu/word_embeddings.py
# Word Embeddings for Semantic Similarity

"""
Word Embeddings Module

Provides semantic similarity using word embeddings:
- Pre-computed word vectors
- Semantic similarity calculation
- Word analogies
- Nearest neighbors search
- Context-aware embeddings
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import math
import re
from collections import defaultdict


@dataclass
class WordVector:
    """Word with its embedding vector."""
    word: str
    vector: List[float]
    
    def magnitude(self) -> float:
        """Calculate vector magnitude."""
        return math.sqrt(sum(v * v for v in self.vector))
    
    def normalize(self) -> 'WordVector':
        """Return normalized vector."""
        mag = self.magnitude()
        if mag == 0:
            return self
        return WordVector(self.word, [v / mag for v in self.vector])


class WordEmbeddings:
    """
    Word embedding system for semantic similarity.
    
    Uses a combination of:
    - Pre-defined semantic categories
    - Co-occurrence statistics
    - Learned embeddings from training data
    """
    
    def __init__(self, dimension: int = 50):
        self.dimension = dimension
        self.word_vectors: Dict[str, WordVector] = {}
        self.word_to_id: Dict[str, int] = {}
        self.id_to_word: Dict[int, str] = {}
        
        # Initialize with semantic categories
        self._initialize_semantic_embeddings()
        
    def _initialize_semantic_embeddings(self):
        """
        Initialize embeddings based on semantic categories.
        
        This creates vectors where similar words have similar vectors
        based on their semantic relationships.
        """
        # Define semantic dimensions (first 20 dimensions = semantic categories)
        semantic_categories = {
            0: {"positive", "good", "great", "excellent", "wonderful", "amazing", 
                "fantastic", "happy", "joy", "love", "like", "beautiful", "nice"},
            1: {"negative", "bad", "terrible", "awful", "horrible", "hate", 
                "angry", "sad", "ugly", "wrong", "poor", "worst"},
            2: {"person", "people", "man", "woman", "child", "friend", "family",
                "human", "individual", "someone", "anyone", "everyone"},
            3: {"action", "do", "make", "go", "come", "run", "walk", "move",
                "work", "play", "create", "build", "start", "stop"},
            4: {"think", "know", "believe", "understand", "learn", "study",
                "consider", "imagine", "remember", "forget", "realize"},
            5: {"time", "now", "then", "today", "tomorrow", "yesterday",
                "always", "never", "sometimes", "often", "soon", "later"},
            6: {"place", "here", "there", "where", "home", "house", "room",
                "city", "country", "world", "area", "location"},
            7: {"large", "big", "huge", "enormous", "massive", "great", "vast"},
            8: {"small", "little", "tiny", "minute", "slight", "minor"},
            9: {"fast", "quick", "rapid", "swift", "speedy", "instant"},
            10: {"slow", "gradual", "steady", "leisurely", "unhurried"},
            11: {"old", "ancient", "aged", "elderly", "previous", "former"},
            12: {"new", "young", "recent", "modern", "fresh", "latest"},
            13: {"question", "ask", "what", "who", "where", "when", "why", "how",
                 "which", "whose", "whom", "inquire", "query"},
            14: {"answer", "respond", "reply", "tell", "say", "explain",
                 "describe", "inform", "state", "announce"},
            15: {"help", "assist", "support", "aid", "serve", "contribute",
                 "facilitate", "enable", "encourage"},
            16: {"technology", "computer", "software", "internet", "digital",
                 "online", "data", "system", "program", "device"},
            17: {"nature", "natural", "earth", "environment", "animal",
                 "plant", "tree", "water", "air", "sky"},
            18: {"emotion", "feel", "feeling", "mood", "happy", "sad",
                 "angry", "afraid", "excited", "calm"},
            19: {"money", "cost", "price", "pay", "buy", "sell", "spend",
                 "save", "business", "economy", "financial"},
        }
        
        # Create vectors for words based on category membership
        all_words = set()
        for words in semantic_categories.values():
            all_words.update(words)
            
        for word in all_words:
            vector = [0.0] * self.dimension
            
            # Set semantic dimension values
            for cat_id, cat_words in semantic_categories.items():
                if word in cat_words:
                    vector[cat_id] = 1.0
                    
            # Add some random variation for uniqueness (dimensions 20-49)
            import hashlib
            word_hash = int(hashlib.md5(word.encode()).hexdigest(), 16)
            for i in range(20, self.dimension):
                vector[i] = ((word_hash >> (i * 2)) % 100) / 100.0 - 0.5
                
            self.add_word(word, vector)
            
        # Add common words not in categories
        self._add_common_words()
        
    def _add_common_words(self):
        """Add embeddings for common words not in semantic categories."""
        # Define relationships for common words
        word_relations = {
            # Verbs
            "is": {"action": 0.3, "neutral": 0.5},
            "are": {"action": 0.3, "neutral": 0.5},
            "was": {"action": 0.3, "time": 0.5},
            "were": {"action": 0.3, "time": 0.5},
            "have": {"action": 0.5},
            "has": {"action": 0.5},
            "had": {"action": 0.5, "time": 0.3},
            "can": {"action": 0.4, "positive": 0.2},
            "could": {"action": 0.4},
            "will": {"action": 0.4, "time": 0.3},
            "would": {"action": 0.4},
            "should": {"action": 0.4, "positive": 0.1},
            "must": {"action": 0.5},
            "may": {"action": 0.3},
            "might": {"action": 0.3},
            
            # Prepositions/Conjunctions
            "in": {"place": 0.5},
            "on": {"place": 0.5},
            "at": {"place": 0.4, "time": 0.3},
            "to": {"action": 0.2},
            "for": {"action": 0.2},
            "with": {"action": 0.2},
            "from": {"place": 0.3},
            "by": {"action": 0.2},
            "about": {"topic": 0.5},
            "and": {"neutral": 0.5},
            "or": {"neutral": 0.5},
            "but": {"negative": 0.2},
            "if": {"condition": 0.5},
            "because": {"reason": 0.5},
            
            # Pronouns
            "i": {"person": 0.8},
            "you": {"person": 0.8},
            "he": {"person": 0.8},
            "she": {"person": 0.8},
            "it": {"thing": 0.5},
            "we": {"person": 0.8},
            "they": {"person": 0.8},
            "this": {"near": 0.5},
            "that": {"far": 0.5},
            
            # Question words
            "what": {"question": 0.9},
            "who": {"question": 0.9, "person": 0.3},
            "where": {"question": 0.9, "place": 0.3},
            "when": {"question": 0.9, "time": 0.3},
            "why": {"question": 0.9},
            "how": {"question": 0.9},
            
            # Common adjectives
            "very": {"intensity": 0.8},
            "more": {"quantity": 0.5},
            "most": {"quantity": 0.7},
            "many": {"quantity": 0.6},
            "much": {"quantity": 0.6},
            "some": {"quantity": 0.3},
            "any": {"quantity": 0.2},
            "all": {"quantity": 0.8},
            "other": {"different": 0.5},
            "same": {"similar": 0.5},
            "different": {"different": 0.8},
        }
        
        category_dims = {
            "positive": 0, "negative": 1, "person": 2, "action": 3,
            "think": 4, "time": 5, "place": 6, "large": 7, "small": 8,
            "fast": 9, "slow": 10, "old": 11, "new": 12, "question": 13,
            "answer": 14, "help": 15, "technology": 16, "nature": 17,
            "emotion": 18, "money": 19
        }
        
        for word, relations in word_relations.items():
            if word in self.word_vectors:
                continue
                
            vector = [0.0] * self.dimension
            for rel, weight in relations.items():
                if rel in category_dims:
                    vector[category_dims[rel]] = weight
                    
            # Add variation
            import hashlib
            word_hash = int(hashlib.md5(word.encode()).hexdigest(), 16)
            for i in range(20, self.dimension):
                vector[i] = ((word_hash >> (i * 2)) % 100) / 100.0 - 0.5
                
            self.add_word(word, vector)
            
    def add_word(self, word: str, vector: List[float]):
        """Add a word with its vector to the embeddings."""
        word_lower = word.lower()
        word_id = len(self.word_to_id)
        self.word_to_id[word_lower] = word_id
        self.id_to_word[word_id] = word_lower
        self.word_vectors[word_lower] = WordVector(word_lower, vector)
        
    def get_vector(self, word: str) -> Optional[WordVector]:
        """Get the vector for a word."""
        return self.word_vectors.get(word.lower())
        
    def has_word(self, word: str) -> bool:
        """Check if word has an embedding."""
        return word.lower() in self.word_vectors
        
    def similarity(self, word1: str, word2: str) -> float:
        """
        Calculate cosine similarity between two words.
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            Similarity score between -1 and 1
        """
        vec1 = self.get_vector(word1)
        vec2 = self.get_vector(word2)
        
        if vec1 is None or vec2 is None:
            return 0.0
            
        return self._cosine_similarity(vec1.vector, vec2.vector)
        
    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a * a for a in v1))
        mag2 = math.sqrt(sum(b * b for b in v2))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
            
        return dot_product / (mag1 * mag2)
        
    def sentence_similarity(self, sent1: str, sent2: str) -> float:
        """
        Calculate similarity between two sentences.
        
        Uses average word vector approach.
        
        Args:
            sent1: First sentence
            sent2: Second sentence
            
        Returns:
            Similarity score between 0 and 1
        """
        vec1 = self._sentence_vector(sent1)
        vec2 = self._sentence_vector(sent2)
        
        if vec1 is None or vec2 is None:
            return 0.0
            
        sim = self._cosine_similarity(vec1, vec2)
        return (sim + 1) / 2  # Normalize to 0-1
        
    def _sentence_vector(self, sentence: str) -> Optional[List[float]]:
        """Get average vector for a sentence."""
        words = re.findall(r'\w+', sentence.lower())
        vectors = [self.get_vector(w) for w in words if self.has_word(w)]
        
        if not vectors:
            return None
            
        # Average the vectors
        avg_vector = [0.0] * self.dimension
        for wv in vectors:
            for i, v in enumerate(wv.vector):
                avg_vector[i] += v
                
        return [v / len(vectors) for v in avg_vector]
        
    def most_similar(self, word: str, n: int = 5) -> List[Tuple[str, float]]:
        """
        Find the n most similar words.
        
        Args:
            word: Query word
            n: Number of results
            
        Returns:
            List of (word, similarity) tuples
        """
        vec = self.get_vector(word)
        if vec is None:
            return []
            
        similarities = []
        for other_word, other_vec in self.word_vectors.items():
            if other_word != word.lower():
                sim = self._cosine_similarity(vec.vector, other_vec.vector)
                similarities.append((other_word, sim))
                
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n]
        
    def analogy(self, word1: str, word2: str, word3: str, n: int = 5) -> List[Tuple[str, float]]:
        """
        Find word that completes analogy: word1 is to word2 as word3 is to ?
        
        Example: king - man + woman = queen
        
        Args:
            word1: First word (king)
            word2: Second word (man)
            word3: Third word (woman)
            n: Number of results
            
        Returns:
            List of (word, score) tuples
        """
        v1 = self.get_vector(word1)
        v2 = self.get_vector(word2)
        v3 = self.get_vector(word3)
        
        if v1 is None or v2 is None or v3 is None:
            return []
            
        # target = word1 - word2 + word3
        target = [a - b + c for a, b, c in zip(v1.vector, v2.vector, v3.vector)]
        
        # Find closest words
        exclude = {word1.lower(), word2.lower(), word3.lower()}
        similarities = []
        
        for word, vec in self.word_vectors.items():
            if word not in exclude:
                sim = self._cosine_similarity(target, vec.vector)
                similarities.append((word, sim))
                
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n]
        
    def train_on_text(self, texts: List[str], window_size: int = 5):
        """
        Train embeddings on text using co-occurrence.
        
        Args:
            texts: List of text documents
            window_size: Context window size
        """
        # Build co-occurrence matrix
        cooccurrence = defaultdict(lambda: defaultdict(float))
        word_counts = defaultdict(int)
        
        for text in texts:
            words = re.findall(r'\w+', text.lower())
            for i, word in enumerate(words):
                word_counts[word] += 1
                
                # Context window
                start = max(0, i - window_size)
                end = min(len(words), i + window_size + 1)
                
                for j in range(start, end):
                    if i != j:
                        context_word = words[j]
                        distance = abs(i - j)
                        weight = 1.0 / distance  # Closer words have higher weight
                        cooccurrence[word][context_word] += weight
                        
        # Update vectors for co-occurring words
        for word, context in cooccurrence.items():
            if word not in self.word_vectors:
                self.add_word(word, [0.0] * self.dimension)
                
            vec = self.word_vectors[word].vector
            
            # Adjust vector based on co-occurrence
            for context_word, weight in context.items():
                if context_word in self.word_vectors:
                    context_vec = self.word_vectors[context_word].vector
                    # Small update toward co-occurring words
                    for i in range(self.dimension):
                        vec[i] += 0.01 * weight * context_vec[i]
                        
    def vocabulary_size(self) -> int:
        """Get number of words with embeddings."""
        return len(self.word_vectors)
        
    def get_stats(self) -> Dict:
        """Get embedding statistics."""
        return {
            "vocabulary_size": self.vocabulary_size(),
            "dimension": self.dimension,
            "avg_magnitude": sum(v.magnitude() for v in self.word_vectors.values()) / max(1, len(self.word_vectors))
        }


class SemanticSearch:
    """
    Semantic search using word embeddings.
    """
    
    def __init__(self, embeddings: WordEmbeddings = None):
        self.embeddings = embeddings or WordEmbeddings()
        self.documents: List[Tuple[str, List[float]]] = []
        
    def index_document(self, doc_id: str, text: str):
        """Add a document to the index."""
        vec = self.embeddings._sentence_vector(text)
        if vec:
            self.documents.append((doc_id, vec))
            
    def search(self, query: str, n: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            n: Number of results
            
        Returns:
            List of (doc_id, similarity) tuples
        """
        query_vec = self.embeddings._sentence_vector(query)
        if query_vec is None:
            return []
            
        results = []
        for doc_id, doc_vec in self.documents:
            sim = self.embeddings._cosine_similarity(query_vec, doc_vec)
            results.append((doc_id, sim))
            
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:n]


# =============================================================================
# SINGLETON & HELPER FUNCTIONS
# =============================================================================

_embeddings: Optional[WordEmbeddings] = None


def get_embeddings() -> WordEmbeddings:
    """Get the global word embeddings instance."""
    global _embeddings
    if _embeddings is None:
        _embeddings = WordEmbeddings()
    return _embeddings


def word_similarity(word1: str, word2: str) -> float:
    """Calculate similarity between two words."""
    return get_embeddings().similarity(word1, word2)


def sentence_similarity(sent1: str, sent2: str) -> float:
    """Calculate similarity between two sentences."""
    return get_embeddings().sentence_similarity(sent1, sent2)


def find_similar(word: str, n: int = 5) -> List[Tuple[str, float]]:
    """Find similar words."""
    return get_embeddings().most_similar(word, n)


def word_analogy(word1: str, word2: str, word3: str) -> List[Tuple[str, float]]:
    """Complete word analogy."""
    return get_embeddings().analogy(word1, word2, word3)
