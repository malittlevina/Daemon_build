# memory_tree/advanced_memory.py
"""
Advanced Memory System - Multi-store memory architecture

Implements a biologically-inspired memory system with:
- Episodic memory (autobiographical events)
- Semantic memory (facts and concepts)
- Procedural memory (skills and procedures)
- Working memory buffer
- Consolidation mechanisms
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import math
import json
import os
import hashlib


class MemoryType(Enum):
    """Types of long-term memory."""
    EPISODIC = "episodic"       # Personal experiences, events
    SEMANTIC = "semantic"       # Facts, concepts, knowledge
    PROCEDURAL = "procedural"   # Skills, how-to knowledge


class MemoryStrength(Enum):
    """Memory consolidation strength."""
    FRAGILE = "fragile"         # Newly formed, easily lost
    WEAK = "weak"               # Partially consolidated
    MODERATE = "moderate"       # Well-formed
    STRONG = "strong"           # Deeply consolidated
    PERMANENT = "permanent"     # Core knowledge


@dataclass
class MemoryNode:
    """A single memory unit."""
    memory_id: str
    content: str
    memory_type: MemoryType
    created_at: datetime
    last_accessed: datetime
    access_count: int = 1
    importance: float = 0.5
    emotional_valence: float = 0.0  # -1 to 1
    strength: MemoryStrength = MemoryStrength.FRAGILE
    tags: List[str] = field(default_factory=list)
    associations: Dict[str, float] = field(default_factory=dict)  # memory_id -> strength
    context: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None  # Vector embedding
    
    def calculate_activation(self) -> float:
        """Calculate current activation level using ACT-R base-level learning."""
        # Time decay
        time_since_access = (datetime.utcnow() - self.last_accessed).total_seconds()
        hours = time_since_access / 3600
        decay = math.exp(-0.5 * hours)
        
        # Frequency effect (power law)
        frequency_factor = math.log(1 + self.access_count) * 0.3
        
        # Importance weight
        importance_factor = self.importance * 0.3
        
        # Strength multiplier
        strength_mult = {
            MemoryStrength.FRAGILE: 0.5,
            MemoryStrength.WEAK: 0.7,
            MemoryStrength.MODERATE: 0.9,
            MemoryStrength.STRONG: 1.0,
            MemoryStrength.PERMANENT: 1.1
        }[self.strength]
        
        return min(1.0, (decay + frequency_factor + importance_factor) * strength_mult)


@dataclass
class Episode:
    """An episodic memory - a sequence of events."""
    episode_id: str
    title: str
    events: List[MemoryNode]
    start_time: datetime
    end_time: Optional[datetime] = None
    participants: List[str] = field(default_factory=list)
    location: Optional[str] = None
    emotional_summary: float = 0.0
    
    def get_duration(self) -> Optional[timedelta]:
        if self.end_time:
            return self.end_time - self.start_time
        return None


@dataclass
class Concept:
    """A semantic memory node - a concept or fact."""
    concept_id: str
    name: str
    definition: str
    category: str
    properties: Dict[str, Any] = field(default_factory=dict)
    related_concepts: Dict[str, float] = field(default_factory=dict)  # concept_id -> relatedness
    instances: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.8


@dataclass
class Procedure:
    """A procedural memory - a skill or process."""
    procedure_id: str
    name: str
    description: str
    steps: List[Dict[str, str]]
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    success_rate: float = 0.5
    execution_count: int = 0
    avg_duration_ms: float = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


class AdvancedMemorySystem:
    """
    Multi-store memory system with consolidation.
    
    Architecture:
    - Sensory buffer (immediate, very short)
    - Working memory (seconds to minutes)
    - Long-term memory:
      - Episodic store
      - Semantic store
      - Procedural store
    """
    
    module_name = "advanced_memory"
    dependencies = []
    
    def __init__(self, storage_path: str = "memory_tree/storage"):
        self._lock = threading.RLock()
        self._kernel = None
        
        # Storage path
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Working memory buffer (limited capacity)
        self.working_memory: List[MemoryNode] = []
        self.working_memory_capacity = 7  # Miller's law
        
        # Long-term stores
        self.episodic_store: Dict[str, Episode] = {}
        self.semantic_store: Dict[str, Concept] = {}
        self.procedural_store: Dict[str, Procedure] = {}
        self.memory_index: Dict[str, MemoryNode] = {}
        
        # Association graph
        self.associations: Dict[str, Set[str]] = {}
        
        # Consolidation queue
        self._consolidation_queue: List[str] = []
        
        # Simple embedding cache (for semantic similarity)
        self._embedding_cache: Dict[str, List[float]] = {}
        
        # Load persisted memories
        self._load_from_storage()
        
        print("[AdvancedMemory] System initialized.")
    
    def initialize(self, kernel) -> bool:
        """Initialize with kernel reference."""
        self._kernel = kernel
        return True
    
    def start(self) -> bool:
        """Start memory services."""
        # Start consolidation thread
        self._start_consolidation_worker()
        return True
    
    def stop(self) -> bool:
        """Stop and persist."""
        self._save_to_storage()
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "status": "healthy",
            "working_memory_size": len(self.working_memory),
            "episodic_count": len(self.episodic_store),
            "semantic_count": len(self.semantic_store),
            "procedural_count": len(self.procedural_store),
            "total_memories": len(self.memory_index)
        }
    
    # ==================== Working Memory ====================
    
    def attend(self, content: str, importance: float = 0.5) -> str:
        """Add item to working memory (attention)."""
        memory_id = self._generate_id(content)
        
        node = MemoryNode(
            memory_id=memory_id,
            content=content,
            memory_type=MemoryType.EPISODIC,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            importance=importance
        )
        
        with self._lock:
            self.working_memory.append(node)
            
            # Enforce capacity - remove lowest activation
            if len(self.working_memory) > self.working_memory_capacity:
                self.working_memory.sort(key=lambda m: m.calculate_activation())
                displaced = self.working_memory.pop(0)
                
                # Queue displaced for consolidation
                self._consolidation_queue.append(displaced.memory_id)
                self.memory_index[displaced.memory_id] = displaced
        
        return memory_id
    
    def get_working_memory(self) -> List[Dict]:
        """Get current working memory contents."""
        with self._lock:
            return [
                {
                    "id": m.memory_id,
                    "content": m.content[:100],
                    "activation": m.calculate_activation()
                }
                for m in self.working_memory
            ]
    
    # ==================== Episodic Memory ====================
    
    def start_episode(
        self,
        title: str,
        participants: List[str] = None,
        location: str = None
    ) -> str:
        """Start recording an episode."""
        episode_id = self._generate_id(title)
        
        episode = Episode(
            episode_id=episode_id,
            title=title,
            events=[],
            start_time=datetime.utcnow(),
            participants=participants or [],
            location=location
        )
        
        with self._lock:
            self.episodic_store[episode_id] = episode
        
        return episode_id
    
    def add_event_to_episode(
        self,
        episode_id: str,
        content: str,
        emotional_valence: float = 0.0
    ) -> bool:
        """Add an event to an ongoing episode."""
        with self._lock:
            episode = self.episodic_store.get(episode_id)
            if not episode:
                return False
            
            event = MemoryNode(
                memory_id=self._generate_id(content),
                content=content,
                memory_type=MemoryType.EPISODIC,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                emotional_valence=emotional_valence
            )
            
            episode.events.append(event)
            self.memory_index[event.memory_id] = event
            
            return True
    
    def end_episode(self, episode_id: str) -> Optional[Episode]:
        """End an episode and calculate summary."""
        with self._lock:
            episode = self.episodic_store.get(episode_id)
            if not episode:
                return None
            
            episode.end_time = datetime.utcnow()
            
            # Calculate emotional summary
            if episode.events:
                episode.emotional_summary = sum(
                    e.emotional_valence for e in episode.events
                ) / len(episode.events)
            
            return episode
    
    def recall_episode(
        self,
        query: str,
        limit: int = 5
    ) -> List[Episode]:
        """Recall episodes related to a query."""
        with self._lock:
            scored_episodes = []
            
            for episode in self.episodic_store.values():
                # Score based on title and event content
                score = self._calculate_similarity(query, episode.title)
                
                for event in episode.events:
                    event_score = self._calculate_similarity(query, event.content)
                    score = max(score, event_score * 0.8)
                    
                    # Boost activation on access
                    event.last_accessed = datetime.utcnow()
                    event.access_count += 1
                
                if score > 0.2:
                    scored_episodes.append((episode, score))
            
            scored_episodes.sort(key=lambda x: x[1], reverse=True)
            return [ep for ep, _ in scored_episodes[:limit]]
    
    # ==================== Semantic Memory ====================
    
    def store_concept(
        self,
        name: str,
        definition: str,
        category: str,
        properties: Dict[str, Any] = None,
        related: List[str] = None
    ) -> str:
        """Store a concept in semantic memory."""
        concept_id = self._generate_id(name)
        
        concept = Concept(
            concept_id=concept_id,
            name=name,
            definition=definition,
            category=category,
            properties=properties or {}
        )
        
        with self._lock:
            # Create associations with related concepts
            if related:
                for rel_name in related:
                    rel_id = self._generate_id(rel_name)
                    if rel_id in self.semantic_store:
                        concept.related_concepts[rel_id] = 0.5
                        self.semantic_store[rel_id].related_concepts[concept_id] = 0.5
            
            self.semantic_store[concept_id] = concept
            
            # Also create a memory node for general retrieval
            node = MemoryNode(
                memory_id=concept_id,
                content=f"{name}: {definition}",
                memory_type=MemoryType.SEMANTIC,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                tags=[category] + (related or [])
            )
            self.memory_index[concept_id] = node
        
        return concept_id
    
    def query_concepts(
        self,
        query: str,
        category: str = None,
        limit: int = 10
    ) -> List[Concept]:
        """Query semantic memory for concepts."""
        with self._lock:
            scored = []
            
            for concept in self.semantic_store.values():
                if category and concept.category != category:
                    continue
                
                # Score based on name and definition
                name_score = self._calculate_similarity(query, concept.name)
                def_score = self._calculate_similarity(query, concept.definition)
                score = max(name_score * 1.2, def_score)
                
                if score > 0.15:
                    scored.append((concept, score))
            
            scored.sort(key=lambda x: x[1], reverse=True)
            return [c for c, _ in scored[:limit]]
    
    def get_related_concepts(
        self,
        concept_id: str,
        depth: int = 1
    ) -> List[Tuple[Concept, float]]:
        """Get concepts related to a given concept."""
        with self._lock:
            concept = self.semantic_store.get(concept_id)
            if not concept:
                return []
            
            related = []
            visited = {concept_id}
            
            def explore(cid: str, current_depth: int, base_strength: float):
                if current_depth > depth:
                    return
                
                c = self.semantic_store.get(cid)
                if not c:
                    return
                
                for rel_id, strength in c.related_concepts.items():
                    if rel_id not in visited:
                        visited.add(rel_id)
                        rel_concept = self.semantic_store.get(rel_id)
                        if rel_concept:
                            combined_strength = base_strength * strength
                            related.append((rel_concept, combined_strength))
                            explore(rel_id, current_depth + 1, combined_strength)
            
            explore(concept_id, 0, 1.0)
            related.sort(key=lambda x: x[1], reverse=True)
            return related
    
    # ==================== Procedural Memory ====================
    
    def store_procedure(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, str]],
        preconditions: List[str] = None,
        postconditions: List[str] = None
    ) -> str:
        """Store a procedure (skill/process)."""
        procedure_id = self._generate_id(name)
        
        procedure = Procedure(
            procedure_id=procedure_id,
            name=name,
            description=description,
            steps=steps,
            preconditions=preconditions or [],
            postconditions=postconditions or []
        )
        
        with self._lock:
            self.procedural_store[procedure_id] = procedure
            
            # Also index for general retrieval
            node = MemoryNode(
                memory_id=procedure_id,
                content=f"Procedure: {name} - {description}",
                memory_type=MemoryType.PROCEDURAL,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow()
            )
            self.memory_index[procedure_id] = node
        
        return procedure_id
    
    def get_procedure(self, name: str) -> Optional[Procedure]:
        """Get a procedure by name."""
        procedure_id = self._generate_id(name)
        return self.procedural_store.get(procedure_id)
    
    def record_procedure_execution(
        self,
        procedure_id: str,
        success: bool,
        duration_ms: float
    ):
        """Record procedure execution for learning."""
        with self._lock:
            procedure = self.procedural_store.get(procedure_id)
            if procedure:
                procedure.execution_count += 1
                
                # Update success rate with exponential moving average
                alpha = 0.2
                procedure.success_rate = (
                    alpha * (1.0 if success else 0.0) +
                    (1 - alpha) * procedure.success_rate
                )
                
                # Update average duration
                procedure.avg_duration_ms = (
                    (procedure.avg_duration_ms * (procedure.execution_count - 1) + duration_ms)
                    / procedure.execution_count
                )
    
    # ==================== General Retrieval ====================
    
    def remember(
        self,
        query: str,
        memory_types: List[MemoryType] = None,
        limit: int = 10,
        min_activation: float = 0.1
    ) -> List[Tuple[MemoryNode, float]]:
        """General memory retrieval with spreading activation."""
        with self._lock:
            if memory_types is None:
                memory_types = list(MemoryType)
            
            candidates = []
            
            for memory_id, node in self.memory_index.items():
                if node.memory_type not in memory_types:
                    continue
                
                # Calculate retrieval score
                activation = node.calculate_activation()
                if activation < min_activation:
                    continue
                
                similarity = self._calculate_similarity(query, node.content)
                
                # Spreading activation from associated memories
                association_boost = 0
                for assoc_id, strength in node.associations.items():
                    if assoc_id in self.memory_index:
                        assoc_sim = self._calculate_similarity(
                            query, self.memory_index[assoc_id].content
                        )
                        association_boost += assoc_sim * strength * 0.3
                
                total_score = activation * 0.3 + similarity * 0.5 + association_boost * 0.2
                
                if total_score > 0.1:
                    candidates.append((node, total_score))
                    
                    # Update access stats
                    node.last_accessed = datetime.utcnow()
                    node.access_count += 1
            
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[:limit]
    
    def forget(
        self,
        memory_type: MemoryType = None,
        older_than_days: int = 30,
        min_activation: float = 0.05
    ) -> int:
        """Forget (remove) weak memories."""
        cutoff = datetime.utcnow() - timedelta(days=older_than_days)
        forgotten = 0
        
        with self._lock:
            to_remove = []
            
            for memory_id, node in self.memory_index.items():
                if memory_type and node.memory_type != memory_type:
                    continue
                
                if node.created_at < cutoff and node.calculate_activation() < min_activation:
                    if node.strength not in (MemoryStrength.STRONG, MemoryStrength.PERMANENT):
                        to_remove.append(memory_id)
            
            for mid in to_remove:
                del self.memory_index[mid]
                forgotten += 1
        
        return forgotten
    
    # ==================== Consolidation ====================
    
    def consolidate(self):
        """Run memory consolidation (like sleep)."""
        with self._lock:
            # Process consolidation queue
            for memory_id in self._consolidation_queue:
                node = self.memory_index.get(memory_id)
                if not node:
                    continue
                
                # Strengthen based on importance and access
                if node.access_count > 3 or node.importance > 0.7:
                    self._strengthen_memory(node)
                
                # Create associations based on similarity
                self._create_associations(node)
            
            self._consolidation_queue.clear()
            
            # Decay weak memories
            for node in self.memory_index.values():
                if node.strength == MemoryStrength.FRAGILE:
                    # Some fragile memories strengthen, others fade
                    if node.access_count > 2:
                        node.strength = MemoryStrength.WEAK
                    elif node.calculate_activation() < 0.1:
                        node.strength = MemoryStrength.FRAGILE  # May be forgotten
    
    def _strengthen_memory(self, node: MemoryNode):
        """Strengthen a memory through consolidation."""
        strength_order = list(MemoryStrength)
        current_idx = strength_order.index(node.strength)
        
        if current_idx < len(strength_order) - 1:
            node.strength = strength_order[current_idx + 1]
    
    def _create_associations(self, node: MemoryNode):
        """Create associations between memories."""
        for other_id, other_node in self.memory_index.items():
            if other_id == node.memory_id:
                continue
            
            similarity = self._calculate_similarity(node.content, other_node.content)
            
            if similarity > 0.3:
                # Create bidirectional association
                node.associations[other_id] = similarity
                other_node.associations[node.memory_id] = similarity
    
    def _start_consolidation_worker(self):
        """Start background consolidation worker."""
        def worker():
            import time
            while True:
                time.sleep(300)  # Every 5 minutes
                self.consolidate()
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    # ==================== Utilities ====================
    
    def _generate_id(self, content: str) -> str:
        """Generate a unique ID for content."""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (simple word overlap)."""
        # Normalize
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Remove stopwords
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "to", "of", "and", "in", "that", "it", "for", "on", "with", "as", "at", "by", "this", "from"}
        words1 = words1 - stopwords
        words2 = words2 - stopwords
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _load_from_storage(self):
        """Load memories from disk."""
        try:
            index_path = os.path.join(self.storage_path, "memory_index.json")
            if os.path.exists(index_path):
                with open(index_path, "r") as f:
                    data = json.load(f)
                    # Simplified loading - in production would deserialize fully
                    print(f"[AdvancedMemory] Loaded {len(data)} memories from storage.")
        except Exception as e:
            print(f"[AdvancedMemory] Could not load from storage: {e}")
    
    def _save_to_storage(self):
        """Save memories to disk."""
        try:
            index_path = os.path.join(self.storage_path, "memory_index.json")
            
            # Serialize memories (simplified)
            data = {
                mid: {
                    "content": node.content[:500],
                    "type": node.memory_type.value,
                    "strength": node.strength.value,
                    "access_count": node.access_count
                }
                for mid, node in self.memory_index.items()
            }
            
            with open(index_path, "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"[AdvancedMemory] Saved {len(data)} memories to storage.")
        except Exception as e:
            print(f"[AdvancedMemory] Could not save to storage: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        with self._lock:
            strength_dist = {}
            for node in self.memory_index.values():
                s = node.strength.value
                strength_dist[s] = strength_dist.get(s, 0) + 1
            
            return {
                "working_memory_size": len(self.working_memory),
                "working_memory_capacity": self.working_memory_capacity,
                "episodic_episodes": len(self.episodic_store),
                "semantic_concepts": len(self.semantic_store),
                "procedural_skills": len(self.procedural_store),
                "total_indexed_memories": len(self.memory_index),
                "strength_distribution": strength_dist,
                "consolidation_queue": len(self._consolidation_queue)
            }
