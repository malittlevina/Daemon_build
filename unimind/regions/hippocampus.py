# unimind/regions/hippocampus.py
# Hippocampus - Memory formation, consolidation, spatial navigation, episodic memory

import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib
import math


@dataclass
class EpisodicMemory:
    """An episodic memory - a specific event/experience."""
    memory_id: str
    content: Any
    context: Dict[str, Any]
    timestamp: str
    emotional_valence: float = 0.0      # -1 to 1
    importance: float = 0.5              # 0 to 1
    access_count: int = 0
    last_accessed: str = ""
    associations: List[str] = field(default_factory=list)
    consolidated: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "memory_id": self.memory_id,
            "content": str(self.content)[:200],
            "context": self.context,
            "timestamp": self.timestamp,
            "emotional_valence": self.emotional_valence,
            "importance": self.importance,
            "access_count": self.access_count,
            "consolidated": self.consolidated
        }


@dataclass
class SemanticNode:
    """A semantic memory node - factual knowledge."""
    node_id: str
    concept: str
    properties: Dict[str, Any]
    relations: Dict[str, List[str]]  # relation_type -> node_ids
    strength: float = 1.0
    
    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "concept": self.concept,
            "properties": self.properties,
            "relations": {k: len(v) for k, v in self.relations.items()}
        }


@dataclass
class SpatialMap:
    """A cognitive map for spatial navigation."""
    map_id: str
    name: str
    landmarks: Dict[str, Tuple[float, float, float]]  # landmark -> (x, y, z)
    paths: List[Dict[str, Any]]
    current_position: Tuple[float, float, float] = (0, 0, 0)
    
    def to_dict(self) -> Dict:
        return {
            "map_id": self.map_id,
            "name": self.name,
            "landmarks_count": len(self.landmarks),
            "paths_count": len(self.paths),
            "current_position": self.current_position
        }


class Hippocampus:
    """
    Hippocampus module - Memory formation and spatial cognition.
    
    Responsible for:
    - Episodic memory formation and retrieval
    - Memory consolidation (short-term to long-term)
    - Spatial mapping and navigation
    - Pattern separation and completion
    - Memory replay during "sleep"
    - Associative linking between memories
    """
    
    def __init__(self, neural_bus=None, data_path: str = "data/unimind/hippocampus"):
        self.neural_bus = neural_bus
        self.data_path = data_path
        os.makedirs(data_path, exist_ok=True)
        
        # Episodic memories
        self.episodic_memories: Dict[str, EpisodicMemory] = {}
        self.memory_timeline: List[str] = []  # Ordered memory IDs
        
        # Semantic network
        self.semantic_nodes: Dict[str, SemanticNode] = {}
        
        # Spatial maps
        self.spatial_maps: Dict[str, SpatialMap] = {}
        self.active_map: Optional[str] = None
        
        # Index structures
        self.content_index: Dict[str, List[str]] = defaultdict(list)  # keyword -> memory_ids
        self.temporal_index: Dict[str, List[str]] = defaultdict(list)  # date -> memory_ids
        
        # Consolidation queue
        self.consolidation_queue: List[str] = []
        
        # AI model hooks
        self.embedding_model = None
        self.embeddings: Dict[str, List[float]] = {}
        
        # Capabilities
        self.capabilities = [
            "episodic_memory", "semantic_memory", "spatial_navigation",
            "memory_consolidation", "pattern_completion", "memory_replay"
        ]
        
        # Load existing memories
        self._load_memories()
        
        # Register with neural bus
        if self.neural_bus:
            self._register_with_bus()
            
        print("[Hippocampus] Memory systems initialized.")
        
    def _register_with_bus(self):
        """Register with neural bus."""
        self.neural_bus.register_region(
            region_id="hippocampus",
            name="Hippocampus",
            module_type="limbic",
            capabilities=self.capabilities,
            handler=self._handle_signal
        )
        
    def _handle_signal(self, signal) -> Optional[Any]:
        """Handle incoming neural signals."""
        from unimind.neural_bus import NeuralSignal, SignalType
        
        payload = signal.payload
        
        if signal.signal_type == SignalType.QUERY:
            capability = payload.get("capability")
            data = payload.get("data", {})
            
            if capability == "episodic_memory":
                if "store" in data:
                    memory = self.store_episodic(data["store"]["content"], data["store"].get("context", {}))
                    return NeuralSignal(
                        signal_id=f"hpc_store_{memory.memory_id}",
                        signal_type=SignalType.RESPONSE,
                        source="hippocampus",
                        target=signal.source,
                        payload={"stored": memory.to_dict()}
                    )
                elif "recall" in data:
                    memories = self.recall(data["recall"], top_k=data.get("top_k", 5))
                    return NeuralSignal(
                        signal_id=f"hpc_recall",
                        signal_type=SignalType.RESPONSE,
                        source="hippocampus",
                        target=signal.source,
                        payload={"memories": [m.to_dict() for m in memories]}
                    )
                    
        elif signal.signal_type == SignalType.MODULATORY:
            if payload.get("mode") == "consolidation":
                self.run_consolidation()
                
        return None
        
    def _load_memories(self):
        """Load memories from disk."""
        memories_file = os.path.join(self.data_path, "memories.json")
        if os.path.exists(memories_file):
            try:
                with open(memories_file, "r") as f:
                    data = json.load(f)
                    for m in data.get("episodic", []):
                        memory = EpisodicMemory(
                            memory_id=m["memory_id"],
                            content=m["content"],
                            context=m.get("context", {}),
                            timestamp=m["timestamp"],
                            emotional_valence=m.get("emotional_valence", 0),
                            importance=m.get("importance", 0.5),
                            access_count=m.get("access_count", 0),
                            consolidated=m.get("consolidated", False)
                        )
                        self.episodic_memories[memory.memory_id] = memory
                        self.memory_timeline.append(memory.memory_id)
                        self._index_memory(memory)
                print(f"[Hippocampus] Loaded {len(self.episodic_memories)} memories")
            except Exception as e:
                print(f"[Hippocampus] Error loading memories: {e}")
                
    def _save_memories(self):
        """Save memories to disk."""
        memories_file = os.path.join(self.data_path, "memories.json")
        data = {
            "episodic": [m.to_dict() for m in self.episodic_memories.values()],
            "saved_at": datetime.now().isoformat()
        }
        with open(memories_file, "w") as f:
            json.dump(data, f, indent=2)
            
    def _generate_memory_id(self, content: Any) -> str:
        """Generate unique memory ID."""
        content_hash = hashlib.md5(str(content).encode()).hexdigest()[:8]
        return f"mem_{int(time.time() * 1000)}_{content_hash}"
        
    def _index_memory(self, memory: EpisodicMemory):
        """Index memory for retrieval."""
        # Content-based index
        content_str = str(memory.content).lower()
        words = content_str.split()
        for word in words:
            if len(word) > 3:
                self.content_index[word].append(memory.memory_id)
                
        # Temporal index
        date = memory.timestamp[:10]  # YYYY-MM-DD
        self.temporal_index[date].append(memory.memory_id)
        
    def set_embedding_model(self, model: Any):
        """Set the embedding model for semantic search."""
        self.embedding_model = model
        print("[Hippocampus] Embedding model configured.")
        
    def store_episodic(
        self,
        content: Any,
        context: Dict[str, Any] = None,
        emotional_valence: float = 0.0,
        importance: float = 0.5
    ) -> EpisodicMemory:
        """
        Store a new episodic memory.
        
        Args:
            content: The memory content
            context: Contextual information
            emotional_valence: Emotional coloring (-1 to 1)
            importance: How important this memory is
            
        Returns:
            Created EpisodicMemory
        """
        memory_id = self._generate_memory_id(content)
        
        memory = EpisodicMemory(
            memory_id=memory_id,
            content=content,
            context=context or {},
            timestamp=datetime.now().isoformat(),
            emotional_valence=emotional_valence,
            importance=importance
        )
        
        self.episodic_memories[memory_id] = memory
        self.memory_timeline.append(memory_id)
        self._index_memory(memory)
        
        # Add to consolidation queue if important
        if importance > 0.6 or abs(emotional_valence) > 0.5:
            self.consolidation_queue.append(memory_id)
            
        # Generate embedding if model available
        if self.embedding_model:
            try:
                self.embeddings[memory_id] = self._compute_embedding(str(content))
            except:
                pass
                
        self._save_memories()
        
        print(f"[Hippocampus] Stored memory: {memory_id}")
        return memory
        
    def _compute_embedding(self, text: str) -> List[float]:
        """Compute embedding for text."""
        if not self.embedding_model:
            # Simple bag-of-words fallback
            words = text.lower().split()
            embedding = [0.0] * 100
            for i, word in enumerate(words[:100]):
                embedding[i % 100] += hash(word) % 100 / 100.0
            return embedding
        return self.embedding_model.embed(text)
        
    def recall(
        self,
        query: str,
        top_k: int = 5,
        time_range: Tuple[str, str] = None,
        min_importance: float = 0.0
    ) -> List[EpisodicMemory]:
        """
        Recall memories matching a query.
        
        Args:
            query: Search query
            top_k: Number of memories to return
            time_range: Optional (start, end) time filter
            min_importance: Minimum importance threshold
            
        Returns:
            List of matching memories
        """
        candidates = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for memory in self.episodic_memories.values():
            if memory.importance < min_importance:
                continue
                
            # Time filter
            if time_range:
                if not (time_range[0] <= memory.timestamp <= time_range[1]):
                    continue
                    
            # Compute similarity
            score = self._compute_similarity(query, memory)
            
            if score > 0.1:
                candidates.append((memory, score))
                
        # Sort by score
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Update access counts
        results = []
        for memory, score in candidates[:top_k]:
            memory.access_count += 1
            memory.last_accessed = datetime.now().isoformat()
            results.append(memory)
            
        self._save_memories()
        return results
        
    def _compute_similarity(self, query: str, memory: EpisodicMemory) -> float:
        """Compute similarity between query and memory."""
        query_lower = query.lower()
        content_str = str(memory.content).lower()
        
        # Use embeddings if available
        if memory.memory_id in self.embeddings:
            query_emb = self._compute_embedding(query)
            mem_emb = self.embeddings[memory.memory_id]
            # Cosine similarity
            dot = sum(a * b for a, b in zip(query_emb, mem_emb))
            norm_q = math.sqrt(sum(a * a for a in query_emb))
            norm_m = math.sqrt(sum(b * b for b in mem_emb))
            if norm_q > 0 and norm_m > 0:
                return dot / (norm_q * norm_m)
                
        # Fallback to keyword matching
        query_words = set(query_lower.split())
        content_words = set(content_str.split())
        
        overlap = len(query_words & content_words)
        if len(query_words) == 0:
            return 0.0
            
        return overlap / len(query_words)
        
    def recall_recent(self, count: int = 10) -> List[EpisodicMemory]:
        """Recall most recent memories."""
        recent_ids = self.memory_timeline[-count:]
        return [self.episodic_memories[mid] for mid in reversed(recent_ids) if mid in self.episodic_memories]
        
    def recall_by_emotion(self, valence_range: Tuple[float, float], top_k: int = 5) -> List[EpisodicMemory]:
        """Recall memories by emotional valence."""
        min_v, max_v = valence_range
        memories = [m for m in self.episodic_memories.values() if min_v <= m.emotional_valence <= max_v]
        memories.sort(key=lambda m: abs(m.emotional_valence), reverse=True)
        return memories[:top_k]
        
    def associate_memories(self, memory_id_1: str, memory_id_2: str, relation: str = "related"):
        """Create association between two memories."""
        if memory_id_1 in self.episodic_memories and memory_id_2 in self.episodic_memories:
            mem1 = self.episodic_memories[memory_id_1]
            mem2 = self.episodic_memories[memory_id_2]
            
            if memory_id_2 not in mem1.associations:
                mem1.associations.append(memory_id_2)
            if memory_id_1 not in mem2.associations:
                mem2.associations.append(memory_id_1)
                
            self._save_memories()
            
    def store_semantic(
        self,
        concept: str,
        properties: Dict[str, Any] = None,
        relations: Dict[str, List[str]] = None
    ) -> SemanticNode:
        """Store semantic knowledge (facts, concepts)."""
        node_id = f"sem_{concept.lower().replace(' ', '_')}"
        
        node = SemanticNode(
            node_id=node_id,
            concept=concept,
            properties=properties or {},
            relations=relations or {}
        )
        
        self.semantic_nodes[node_id] = node
        return node
        
    def query_semantic(self, concept: str) -> Optional[SemanticNode]:
        """Query semantic memory for a concept."""
        node_id = f"sem_{concept.lower().replace(' ', '_')}"
        return self.semantic_nodes.get(node_id)
        
    def create_spatial_map(self, name: str) -> SpatialMap:
        """Create a new spatial/cognitive map."""
        map_id = f"map_{int(time.time())}"
        
        spatial_map = SpatialMap(
            map_id=map_id,
            name=name,
            landmarks={},
            paths=[]
        )
        
        self.spatial_maps[map_id] = spatial_map
        return spatial_map
        
    def add_landmark(self, map_id: str, name: str, position: Tuple[float, float, float]):
        """Add a landmark to a spatial map."""
        if map_id in self.spatial_maps:
            self.spatial_maps[map_id].landmarks[name] = position
            
    def navigate_to(self, map_id: str, landmark: str) -> Optional[List[Dict]]:
        """Get path to a landmark (placeholder for pathfinding)."""
        if map_id not in self.spatial_maps:
            return None
            
        spatial_map = self.spatial_maps[map_id]
        if landmark not in spatial_map.landmarks:
            return None
            
        # Simple direct path
        return [{
            "from": spatial_map.current_position,
            "to": spatial_map.landmarks[landmark],
            "type": "direct"
        }]
        
    def run_consolidation(self) -> int:
        """
        Run memory consolidation - move important short-term to long-term.
        
        This simulates sleep-based memory consolidation.
        """
        consolidated = 0
        
        for memory_id in self.consolidation_queue[:]:
            if memory_id in self.episodic_memories:
                memory = self.episodic_memories[memory_id]
                
                if not memory.consolidated:
                    # Strengthen memory
                    memory.importance = min(1.0, memory.importance * 1.2)
                    memory.consolidated = True
                    consolidated += 1
                    
                    # Find and create associations
                    similar = self.recall(str(memory.content), top_k=3)
                    for sim_mem in similar:
                        if sim_mem.memory_id != memory_id:
                            self.associate_memories(memory_id, sim_mem.memory_id)
                            
                self.consolidation_queue.remove(memory_id)
                
        if consolidated > 0:
            self._save_memories()
            print(f"[Hippocampus] Consolidated {consolidated} memories")
            
        return consolidated
        
    def memory_replay(self, count: int = 5) -> List[EpisodicMemory]:
        """
        Replay memories for consolidation (simulates dream replay).
        
        Returns the replayed memories.
        """
        # Get important unconsolidated memories
        candidates = [m for m in self.episodic_memories.values() 
                      if not m.consolidated and m.importance > 0.4]
        
        # Sort by importance and recency
        candidates.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)
        
        replayed = candidates[:count]
        
        for memory in replayed:
            memory.access_count += 1
            # Replaying strengthens the memory
            memory.importance = min(1.0, memory.importance * 1.1)
            
        self._save_memories()
        return replayed
        
    def pattern_complete(self, partial: str) -> List[EpisodicMemory]:
        """
        Pattern completion - retrieve memories from partial cue.
        
        Args:
            partial: Partial memory cue
            
        Returns:
            Completed memories
        """
        return self.recall(partial, top_k=3)
        
    def get_status(self) -> Dict[str, Any]:
        """Get hippocampus status."""
        return {
            "episodic_count": len(self.episodic_memories),
            "semantic_count": len(self.semantic_nodes),
            "spatial_maps": len(self.spatial_maps),
            "consolidation_queue": len(self.consolidation_queue),
            "has_embedding_model": self.embedding_model is not None,
            "embeddings_count": len(self.embeddings)
        }
