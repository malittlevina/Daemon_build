# lam/experience_memory.py
# Experience Memory - Episodic memory system for learning from past experiences

import json
import os
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum
import hashlib


class MemoryType(Enum):
    """Types of memories stored."""
    EPISODE = "episode"             # Full interaction episode
    SUCCESS = "success"             # Successful action memory
    FAILURE = "failure"             # Failed action memory
    CORRECTION = "correction"       # User correction memory
    OBSERVATION = "observation"     # Passive observation
    INSIGHT = "insight"             # Derived insight


class MemoryImportance(Enum):
    """Importance levels for memories."""
    CRITICAL = "critical"           # Must remember (corrections, important lessons)
    HIGH = "high"                   # Very useful
    MEDIUM = "medium"               # Moderately useful
    LOW = "low"                     # Background information
    EPHEMERAL = "ephemeral"         # Short-term only


@dataclass
class MemoryEmbedding:
    """Lightweight embedding for semantic similarity."""
    keywords: List[str]
    action_types: List[str]
    context_keys: List[str]
    sentiment: float  # -1 to 1
    
    def similarity(self, other: "MemoryEmbedding") -> float:
        """Compute similarity between embeddings."""
        # Keyword overlap
        kw_overlap = len(set(self.keywords) & set(other.keywords))
        kw_total = len(set(self.keywords) | set(other.keywords))
        kw_sim = kw_overlap / kw_total if kw_total > 0 else 0
        
        # Action type overlap
        act_overlap = len(set(self.action_types) & set(other.action_types))
        act_total = len(set(self.action_types) | set(other.action_types))
        act_sim = act_overlap / act_total if act_total > 0 else 0
        
        # Sentiment similarity
        sent_sim = 1 - abs(self.sentiment - other.sentiment) / 2
        
        return 0.5 * kw_sim + 0.3 * act_sim + 0.2 * sent_sim


@dataclass
class EpisodicMemory:
    """A single episodic memory."""
    memory_id: str
    memory_type: MemoryType
    importance: MemoryImportance
    timestamp: str
    
    # Content
    input_text: str
    context: Dict[str, Any]
    action_taken: Dict[str, Any]
    outcome: str
    reward: float
    
    # Metadata
    feedback: Optional[str] = None
    lesson_learned: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)
    
    # Retrieval metadata
    access_count: int = 0
    last_accessed: str = ""
    embedding: Optional[Dict] = None
    
    # Decay and consolidation
    strength: float = 1.0           # Memory strength (decays over time)
    consolidated: bool = False       # Whether consolidated to long-term
    
    def decay(self, hours_passed: float, decay_rate: float = 0.01):
        """Apply memory decay based on time passed."""
        # Important memories decay slower
        importance_factor = {
            MemoryImportance.CRITICAL: 0.1,
            MemoryImportance.HIGH: 0.3,
            MemoryImportance.MEDIUM: 0.5,
            MemoryImportance.LOW: 0.8,
            MemoryImportance.EPHEMERAL: 1.5
        }.get(self.importance, 0.5)
        
        self.strength *= math.exp(-decay_rate * importance_factor * hours_passed)
        
    def reinforce(self, amount: float = 0.2):
        """Reinforce memory when accessed."""
        self.strength = min(1.0, self.strength + amount)
        self.access_count += 1
        self.last_accessed = datetime.now().isoformat()
        
    def to_dict(self) -> Dict:
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type.value,
            "importance": self.importance.value,
            "timestamp": self.timestamp,
            "input_text": self.input_text,
            "context": self.context,
            "action_taken": self.action_taken,
            "outcome": self.outcome,
            "reward": self.reward,
            "feedback": self.feedback,
            "lesson_learned": self.lesson_learned,
            "tags": self.tags,
            "related_memories": self.related_memories,
            "access_count": self.access_count,
            "strength": self.strength,
            "consolidated": self.consolidated
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "EpisodicMemory":
        return EpisodicMemory(
            memory_id=data["memory_id"],
            memory_type=MemoryType(data["memory_type"]),
            importance=MemoryImportance(data.get("importance", "medium")),
            timestamp=data["timestamp"],
            input_text=data["input_text"],
            context=data.get("context", {}),
            action_taken=data.get("action_taken", {}),
            outcome=data.get("outcome", "unknown"),
            reward=data.get("reward", 0.0),
            feedback=data.get("feedback"),
            lesson_learned=data.get("lesson_learned"),
            tags=data.get("tags", []),
            related_memories=data.get("related_memories", []),
            access_count=data.get("access_count", 0),
            strength=data.get("strength", 1.0),
            consolidated=data.get("consolidated", False)
        )


class ExperienceMemory:
    """
    Episodic memory system for the daemon.
    
    Provides:
    - Experience recording and retrieval
    - Similarity-based memory search
    - Memory consolidation and decay
    - Insight extraction from experiences
    - Failure analysis and pattern detection
    """
    
    def __init__(self, data_path: str = "data/lam/memory"):
        self.data_path = data_path
        self.memories: Dict[str, EpisodicMemory] = {}
        self.short_term: List[str] = []  # Recent memory IDs
        self.long_term: List[str] = []   # Consolidated memory IDs
        self.tag_index: Dict[str, List[str]] = defaultdict(list)
        self.failure_patterns: Dict[str, int] = defaultdict(int)
        
        self.max_short_term = 100
        self.max_long_term = 5000
        self.consolidation_threshold = 0.7  # Strength threshold for consolidation
        
        os.makedirs(data_path, exist_ok=True)
        self._load_memories()
        print("[ExperienceMemory] Initialized.")
        
    def _load_memories(self):
        """Load memories from disk."""
        memories_file = os.path.join(self.data_path, "episodic_memories.json")
        if os.path.exists(memories_file):
            try:
                with open(memories_file, "r") as f:
                    data = json.load(f)
                    for m in data.get("memories", []):
                        memory = EpisodicMemory.from_dict(m)
                        self.memories[memory.memory_id] = memory
                        
                        # Rebuild indices
                        for tag in memory.tags:
                            self.tag_index[tag].append(memory.memory_id)
                            
                        if memory.consolidated:
                            self.long_term.append(memory.memory_id)
                        else:
                            self.short_term.append(memory.memory_id)
                            
                print(f"[ExperienceMemory] Loaded {len(self.memories)} memories")
            except Exception as e:
                print(f"[ExperienceMemory] Error loading memories: {e}")
                
    def _save_memories(self):
        """Save memories to disk."""
        memories_file = os.path.join(self.data_path, "episodic_memories.json")
        data = {
            "memories": [m.to_dict() for m in self.memories.values()],
            "saved_at": datetime.now().isoformat(),
            "total_count": len(self.memories)
        }
        with open(memories_file, "w") as f:
            json.dump(data, f, indent=2)
            
    def _compute_embedding(self, text: str, action: Dict, context: Dict) -> MemoryEmbedding:
        """Compute a simple embedding for a memory."""
        # Extract keywords (simple tokenization)
        keywords = [w.lower() for w in text.split() if len(w) > 3][:20]
        
        # Extract action types
        action_types = [action.get("type", "unknown")] if action else []
        
        # Extract context keys
        context_keys = list(context.keys())[:10] if context else []
        
        # Simple sentiment (based on outcome words)
        positive_words = {"success", "good", "great", "correct", "right", "yes", "done"}
        negative_words = {"fail", "error", "wrong", "bad", "no", "cannot", "unable"}
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        sentiment = (pos_count - neg_count) / max(pos_count + neg_count, 1)
        
        return MemoryEmbedding(
            keywords=keywords,
            action_types=action_types,
            context_keys=context_keys,
            sentiment=sentiment
        )
        
    def record(
        self,
        input_text: str,
        context: Dict[str, Any],
        action_taken: Dict[str, Any],
        outcome: str,
        reward: float,
        feedback: Optional[str] = None,
        importance: str = "medium",
        tags: Optional[List[str]] = None
    ) -> EpisodicMemory:
        """
        Record a new experience.
        
        Args:
            input_text: The input that triggered the action
            context: Context at the time
            action_taken: The action taken
            outcome: "success", "failure", "partial", "unknown"
            reward: Numerical reward
            feedback: Optional feedback
            importance: Importance level
            tags: Optional tags
            
        Returns:
            Created EpisodicMemory
        """
        memory_id = f"mem_{int(time.time() * 1000)}_{hashlib.md5(input_text.encode()).hexdigest()[:6]}"
        
        # Determine memory type
        if outcome == "success":
            mem_type = MemoryType.SUCCESS
        elif outcome == "failure":
            mem_type = MemoryType.FAILURE
            # Track failure pattern
            action_type = action_taken.get("type", "unknown")
            self.failure_patterns[action_type] += 1
        elif feedback:
            mem_type = MemoryType.CORRECTION
        else:
            mem_type = MemoryType.EPISODE
            
        # Auto-adjust importance for failures with feedback
        if outcome == "failure" and feedback:
            importance = "high"
            
        memory = EpisodicMemory(
            memory_id=memory_id,
            memory_type=mem_type,
            importance=MemoryImportance(importance),
            timestamp=datetime.now().isoformat(),
            input_text=input_text,
            context=context,
            action_taken=action_taken,
            outcome=outcome,
            reward=reward,
            feedback=feedback,
            tags=tags or []
        )
        
        # Compute embedding
        embedding = self._compute_embedding(input_text, action_taken, context)
        memory.embedding = {
            "keywords": embedding.keywords,
            "action_types": embedding.action_types,
            "context_keys": embedding.context_keys,
            "sentiment": embedding.sentiment
        }
        
        # Auto-generate tags
        if outcome == "failure":
            memory.tags.append("failure")
        if outcome == "success":
            memory.tags.append("success")
        if action_taken:
            memory.tags.append(f"action:{action_taken.get('type', 'unknown')}")
            
        # Store memory
        self.memories[memory_id] = memory
        self.short_term.append(memory_id)
        
        # Update tag index
        for tag in memory.tags:
            self.tag_index[tag].append(memory_id)
            
        # Trim short-term memory
        while len(self.short_term) > self.max_short_term:
            oldest_id = self.short_term.pop(0)
            oldest = self.memories.get(oldest_id)
            if oldest and oldest.strength >= self.consolidation_threshold:
                self._consolidate(oldest_id)
            elif oldest and oldest.importance == MemoryImportance.EPHEMERAL:
                del self.memories[oldest_id]
                
        self._save_memories()
        return memory
    
    def _consolidate(self, memory_id: str):
        """Consolidate a memory to long-term storage."""
        if memory_id in self.memories:
            memory = self.memories[memory_id]
            memory.consolidated = True
            self.long_term.append(memory_id)
            
            # Trim long-term if needed
            while len(self.long_term) > self.max_long_term:
                # Remove lowest strength memories
                min_strength_id = min(
                    self.long_term,
                    key=lambda mid: self.memories.get(mid, EpisodicMemory("", MemoryType.EPISODE, MemoryImportance.LOW, "", "", {}, {}, "", 0)).strength
                )
                self.long_term.remove(min_strength_id)
                if min_strength_id in self.memories:
                    del self.memories[min_strength_id]
                    
    def recall(
        self,
        query: str,
        context: Optional[Dict] = None,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        top_k: int = 5,
        min_strength: float = 0.1
    ) -> List[EpisodicMemory]:
        """
        Recall memories similar to the query.
        
        Args:
            query: Query text
            context: Optional context to match
            memory_type: Filter by memory type
            tags: Filter by tags
            top_k: Number of memories to return
            min_strength: Minimum memory strength
            
        Returns:
            List of matching memories
        """
        # Compute query embedding
        query_embedding = self._compute_embedding(query, {}, context or {})
        
        candidates = []
        
        for memory in self.memories.values():
            # Apply filters
            if memory.strength < min_strength:
                continue
            if memory_type and memory.memory_type.value != memory_type:
                continue
            if tags and not any(t in memory.tags for t in tags):
                continue
                
            # Compute similarity
            if memory.embedding:
                mem_embedding = MemoryEmbedding(
                    keywords=memory.embedding["keywords"],
                    action_types=memory.embedding["action_types"],
                    context_keys=memory.embedding["context_keys"],
                    sentiment=memory.embedding["sentiment"]
                )
                similarity = query_embedding.similarity(mem_embedding)
            else:
                # Fallback to text matching
                overlap = len(set(query.lower().split()) & set(memory.input_text.lower().split()))
                similarity = overlap / max(len(query.split()), 1)
                
            # Weight by strength
            score = similarity * memory.strength
            
            if score > 0.1:
                candidates.append((memory, score))
                
        # Sort by score
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Reinforce accessed memories
        results = []
        for memory, score in candidates[:top_k]:
            memory.reinforce()
            results.append(memory)
            
        self._save_memories()
        return results
    
    def recall_by_action(self, action_type: str, outcome: Optional[str] = None) -> List[EpisodicMemory]:
        """Recall memories for a specific action type."""
        tag = f"action:{action_type}"
        memories = []
        
        for mid in self.tag_index.get(tag, []):
            memory = self.memories.get(mid)
            if memory:
                if outcome is None or memory.outcome == outcome:
                    memories.append(memory)
                    
        return sorted(memories, key=lambda m: m.strength, reverse=True)[:10]
    
    def get_failures_for_action(self, action_type: str) -> List[EpisodicMemory]:
        """Get failure memories for an action type."""
        return self.recall_by_action(action_type, outcome="failure")
    
    def get_successes_for_action(self, action_type: str) -> List[EpisodicMemory]:
        """Get success memories for an action type."""
        return self.recall_by_action(action_type, outcome="success")
    
    def extract_lessons(self, action_type: str) -> List[str]:
        """Extract learned lessons for an action type."""
        failures = self.get_failures_for_action(action_type)
        lessons = []
        
        for memory in failures:
            if memory.lesson_learned:
                lessons.append(memory.lesson_learned)
            elif memory.feedback:
                lessons.append(f"Feedback: {memory.feedback}")
                
        return lessons
    
    def record_correction(
        self,
        original_input: str,
        original_action: Dict,
        correct_action: Dict,
        feedback: str
    ) -> EpisodicMemory:
        """
        Record a correction/feedback experience.
        
        This is important for learning from mistakes.
        """
        memory = self.record(
            input_text=original_input,
            context={"correction": True, "original_action": original_action},
            action_taken=correct_action,
            outcome="correction",
            reward=0.8,  # Corrections are valuable
            feedback=feedback,
            importance="high",
            tags=["correction", "learning"]
        )
        
        # Generate lesson learned
        memory.lesson_learned = f"For input like '{original_input[:50]}...', use {correct_action.get('type', 'this action')} instead of {original_action.get('type', 'previous action')}"
        memory.memory_type = MemoryType.CORRECTION
        
        self._save_memories()
        return memory
    
    def record_insight(
        self,
        insight: str,
        source_memories: List[str],
        importance: str = "medium"
    ) -> EpisodicMemory:
        """Record a derived insight from multiple memories."""
        memory = EpisodicMemory(
            memory_id=f"insight_{int(time.time() * 1000)}",
            memory_type=MemoryType.INSIGHT,
            importance=MemoryImportance(importance),
            timestamp=datetime.now().isoformat(),
            input_text=insight,
            context={"source_type": "derived"},
            action_taken={},
            outcome="insight",
            reward=0.7,
            lesson_learned=insight,
            related_memories=source_memories,
            tags=["insight", "derived"]
        )
        
        self.memories[memory.memory_id] = memory
        self.long_term.append(memory.memory_id)  # Insights go to long-term
        memory.consolidated = True
        
        self._save_memories()
        return memory
    
    def apply_decay(self, hours: float = 24):
        """Apply decay to all memories."""
        for memory in self.memories.values():
            memory.decay(hours)
            
        # Remove very weak ephemeral memories
        to_remove = []
        for mid, memory in self.memories.items():
            if memory.strength < 0.05 and memory.importance == MemoryImportance.EPHEMERAL:
                to_remove.append(mid)
                
        for mid in to_remove:
            del self.memories[mid]
            if mid in self.short_term:
                self.short_term.remove(mid)
            if mid in self.long_term:
                self.long_term.remove(mid)
                
        self._save_memories()
        print(f"[ExperienceMemory] Applied decay, removed {len(to_remove)} weak memories")
        
    def get_failure_patterns(self) -> Dict[str, int]:
        """Get patterns of failures by action type."""
        return dict(self.failure_patterns)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics."""
        type_counts = defaultdict(int)
        importance_counts = defaultdict(int)
        outcome_counts = defaultdict(int)
        
        for memory in self.memories.values():
            type_counts[memory.memory_type.value] += 1
            importance_counts[memory.importance.value] += 1
            outcome_counts[memory.outcome] += 1
            
        return {
            "total_memories": len(self.memories),
            "short_term_count": len(self.short_term),
            "long_term_count": len(self.long_term),
            "by_type": dict(type_counts),
            "by_importance": dict(importance_counts),
            "by_outcome": dict(outcome_counts),
            "failure_patterns": dict(self.failure_patterns),
            "average_strength": sum(m.strength for m in self.memories.values()) / len(self.memories) if self.memories else 0
        }
    
    def analyze_for_patterns(self) -> Dict[str, Any]:
        """Analyze memories for patterns and insights."""
        analysis = {
            "common_failure_contexts": [],
            "successful_patterns": [],
            "areas_for_improvement": []
        }
        
        # Find common failure contexts
        failure_contexts = defaultdict(int)
        for memory in self.memories.values():
            if memory.outcome == "failure":
                context_mode = memory.context.get("mode", "unknown")
                failure_contexts[context_mode] += 1
                
        analysis["common_failure_contexts"] = sorted(
            failure_contexts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Find successful action patterns
        success_actions = defaultdict(int)
        for memory in self.memories.values():
            if memory.outcome == "success":
                action_type = memory.action_taken.get("type", "unknown")
                success_actions[action_type] += 1
                
        analysis["successful_patterns"] = sorted(
            success_actions.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Identify areas needing improvement
        for action_type, fail_count in self.failure_patterns.items():
            successes = len(self.get_successes_for_action(action_type))
            if fail_count > successes:
                analysis["areas_for_improvement"].append({
                    "action": action_type,
                    "failures": fail_count,
                    "successes": successes
                })
                
        return analysis
