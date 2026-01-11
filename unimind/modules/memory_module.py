# unimind/modules/memory_module.py
"""
Memory Module - Working memory and recall capabilities

Provides memory-based reasoning:
- Working memory management
- Associative recall
- Context-aware retrieval
- Memory consolidation triggers
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import re
import math


@dataclass
class MemoryTrace:
    """A memory trace with activation and decay."""
    content: str
    memory_type: str  # episodic, semantic, procedural
    created_at: datetime
    last_accessed: datetime
    access_count: int = 1
    importance: float = 0.5
    associations: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def get_activation(self) -> float:
        """Calculate current activation level using ACT-R style decay."""
        # Time-based decay
        hours_since_access = (datetime.utcnow() - self.last_accessed).total_seconds() / 3600
        time_decay = math.exp(-0.5 * hours_since_access)
        
        # Frequency bonus (log of access count)
        frequency_bonus = math.log(1 + self.access_count) * 0.2
        
        # Importance weight
        importance_weight = self.importance
        
        return min(1.0, (time_decay + frequency_bonus) * importance_weight)


class MemoryModule:
    """
    Memory cognitive module for Unimind.
    
    Capabilities:
    - Working memory buffer
    - Long-term memory simulation
    - Associative retrieval
    - Memory priming
    - Forgetting curve modeling
    """
    
    name = "memory_module"
    
    def __init__(self, working_memory_capacity: int = 7):
        self.active = True
        self.working_memory_capacity = working_memory_capacity
        
        # Working memory (limited capacity, high activation)
        self.working_memory: List[MemoryTrace] = []
        
        # Long-term memory (unlimited, decaying activation)
        self.long_term_memory: List[MemoryTrace] = []
        
        # Semantic associations
        self.associations: Dict[str, List[str]] = {}
        
        # Retrieval history for pattern detection
        self.retrieval_history: List[Dict] = []
    
    def process(self, input_data: Any, context: Any) -> List[Any]:
        """
        Process input using memory-based reasoning.
        
        Returns list of Thought objects.
        """
        from unimind.core import Thought
        
        thoughts = []
        input_str = str(input_data).lower()
        
        # Extract key terms for retrieval
        key_terms = self._extract_key_terms(input_str)
        
        # Check working memory for relevant items
        wm_matches = self._search_working_memory(key_terms)
        for match, relevance in wm_matches[:3]:
            thoughts.append(Thought(
                content=f"[Memory/working] Recent context: {match.content[:100]}...",
                thought_type="memory",
                confidence=0.8 * relevance,
                source_module="memory_module"
            ))
        
        # Retrieve from long-term memory
        ltm_matches = self._retrieve_from_ltm(key_terms)
        for match, activation in ltm_matches[:3]:
            thoughts.append(Thought(
                content=f"[Memory/recall] {match.content[:100]}...",
                thought_type="memory",
                confidence=activation,
                source_module="memory_module"
            ))
            # Boost activation of retrieved memory
            match.last_accessed = datetime.utcnow()
            match.access_count += 1
        
        # Check for associations
        associated = self._get_associations(key_terms)
        if associated:
            thoughts.append(Thought(
                content=f"[Memory/association] Related concepts: {', '.join(associated[:5])}",
                thought_type="inference",
                confidence=0.6,
                source_module="memory_module"
            ))
        
        # Memory-based inference
        inference = self._memory_inference(input_str, wm_matches, ltm_matches)
        if inference:
            thoughts.append(Thought(
                content=f"[Memory/inference] {inference}",
                thought_type="inference",
                confidence=0.7,
                source_module="memory_module"
            ))
        
        # Store current input in working memory
        self._add_to_working_memory(input_str, context)
        
        # Record retrieval for patterns
        self.retrieval_history.append({
            "query_terms": key_terms,
            "wm_hits": len(wm_matches),
            "ltm_hits": len(ltm_matches),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return thoughts
    
    def evaluate(self, thoughts: List[Any]) -> float:
        """Evaluate memory contribution to reasoning."""
        if not thoughts:
            return 0.5
        
        memory_thoughts = [t for t in thoughts if "memory" in t.source_module.lower()]
        
        # Score based on memory contribution
        if not memory_thoughts:
            return 0.4
        
        avg_confidence = sum(t.confidence for t in memory_thoughts) / len(memory_thoughts)
        coverage = min(1.0, len(memory_thoughts) / 3)
        
        return (avg_confidence + coverage) / 2
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms for memory retrieval."""
        # Remove common words
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "of", "to", "in", "for", "on", "with", "at", "by",
            "from", "as", "into", "through", "during", "before", "after",
            "above", "below", "between", "under", "again", "further",
            "then", "once", "here", "there", "when", "where", "why",
            "how", "all", "each", "few", "more", "most", "other", "some",
            "such", "no", "nor", "not", "only", "own", "same", "so",
            "than", "too", "very", "just", "and", "but", "if", "or",
            "because", "until", "while", "about", "what", "which", "who",
            "this", "that", "these", "those", "i", "me", "my", "myself",
            "we", "our", "you", "your", "he", "him", "she", "her", "it"
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        key_terms = [w for w in words if w not in stopwords and len(w) > 2]
        
        return list(set(key_terms))
    
    def _search_working_memory(
        self,
        terms: List[str]
    ) -> List[Tuple[MemoryTrace, float]]:
        """Search working memory for relevant items."""
        results = []
        
        for trace in self.working_memory:
            relevance = self._calculate_relevance(trace.content, terms)
            if relevance > 0.3:
                results.append((trace, relevance))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def _retrieve_from_ltm(
        self,
        terms: List[str],
        threshold: float = 0.2
    ) -> List[Tuple[MemoryTrace, float]]:
        """Retrieve from long-term memory using spreading activation."""
        results = []
        
        for trace in self.long_term_memory:
            # Base activation
            activation = trace.get_activation()
            
            # Relevance boost
            relevance = self._calculate_relevance(trace.content, terms)
            
            # Association boost (spreading activation)
            association_boost = 0
            for term in terms:
                if term in self.associations:
                    for assoc in self.associations[term]:
                        if assoc.lower() in trace.content.lower():
                            association_boost += 0.1
            
            total_activation = min(1.0, activation + relevance + association_boost)
            
            if total_activation > threshold:
                results.append((trace, total_activation))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def _calculate_relevance(self, content: str, terms: List[str]) -> float:
        """Calculate relevance of content to search terms."""
        content_lower = content.lower()
        matches = sum(1 for term in terms if term in content_lower)
        return matches / len(terms) if terms else 0
    
    def _get_associations(self, terms: List[str]) -> List[str]:
        """Get associated concepts for terms."""
        associated = set()
        
        for term in terms:
            if term in self.associations:
                associated.update(self.associations[term])
        
        return list(associated - set(terms))
    
    def _memory_inference(
        self,
        input_str: str,
        wm_matches: List[Tuple],
        ltm_matches: List[Tuple]
    ) -> Optional[str]:
        """Generate inference based on memory matches."""
        # Check for pattern repetition
        if len(wm_matches) > 2:
            return "This topic has been discussed recently in context"
        
        # Check for new vs. familiar
        if ltm_matches and not wm_matches:
            return "This relates to established knowledge, not recent context"
        
        # Check for completely novel
        if not wm_matches and not ltm_matches:
            return "This appears to be a new topic without prior memory associations"
        
        return None
    
    def _add_to_working_memory(self, content: str, context: Any):
        """Add item to working memory with capacity management."""
        trace = MemoryTrace(
            content=content,
            memory_type="episodic",
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            context={"original_context": str(context)[:200] if context else ""}
        )
        
        self.working_memory.append(trace)
        
        # Enforce capacity limit
        if len(self.working_memory) > self.working_memory_capacity:
            # Remove lowest activation item
            self.working_memory.sort(key=lambda t: t.get_activation())
            removed = self.working_memory.pop(0)
            
            # Potentially consolidate to LTM
            if removed.importance > 0.5 or removed.access_count > 2:
                self._consolidate_to_ltm(removed)
    
    def _consolidate_to_ltm(self, trace: MemoryTrace):
        """Consolidate memory from working to long-term memory."""
        trace.memory_type = "semantic"
        self.long_term_memory.append(trace)
        
        # Extract associations
        terms = self._extract_key_terms(trace.content)
        for i, term1 in enumerate(terms):
            for term2 in terms[i+1:]:
                if term1 not in self.associations:
                    self.associations[term1] = []
                if term2 not in self.associations[term1]:
                    self.associations[term1].append(term2)
    
    def store(
        self,
        content: str,
        memory_type: str = "semantic",
        importance: float = 0.5,
        associations: List[str] = None
    ):
        """Explicitly store a memory."""
        trace = MemoryTrace(
            content=content,
            memory_type=memory_type,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            importance=importance,
            associations=associations or []
        )
        
        if memory_type == "episodic":
            self._add_to_working_memory(content, None)
        else:
            self.long_term_memory.append(trace)
            
            # Store associations
            for assoc in (associations or []):
                terms = self._extract_key_terms(content)
                for term in terms:
                    if term not in self.associations:
                        self.associations[term] = []
                    if assoc not in self.associations[term]:
                        self.associations[term].append(assoc)
    
    def forget(self, threshold: float = 0.1):
        """Remove memories below activation threshold."""
        self.long_term_memory = [
            trace for trace in self.long_term_memory
            if trace.get_activation() > threshold
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            "working_memory_size": len(self.working_memory),
            "working_memory_capacity": self.working_memory_capacity,
            "ltm_size": len(self.long_term_memory),
            "association_count": sum(len(v) for v in self.associations.values()),
            "retrieval_count": len(self.retrieval_history)
        }
