# unimind/core.py
"""
Unimind - The Unified Mind Architecture

A symbolic reasoning engine that integrates multiple cognitive
modalities: logic, emotion, memory, ethics, and intuition.
"""

from typing import Dict, Any, Optional, List, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading


class CognitiveMode(Enum):
    """Operating modes for the reasoning engine."""
    ANALYTICAL = "analytical"      # Pure logic, step-by-step
    CREATIVE = "creative"          # Divergent thinking, associations
    INTUITIVE = "intuitive"        # Pattern-based, fast heuristics
    EMPATHETIC = "empathetic"      # Emotion-aware processing
    REFLECTIVE = "reflective"      # Meta-cognition, self-analysis


@dataclass
class Thought:
    """Represents a single thought or reasoning step."""
    content: str
    thought_type: str  # observation, inference, hypothesis, conclusion, question
    confidence: float  # 0.0 to 1.0
    source_module: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    related_thoughts: List[str] = field(default_factory=list)  # thought IDs
    
    def strengthen(self, evidence: str):
        """Add supporting evidence and boost confidence."""
        self.supporting_evidence.append(evidence)
        self.confidence = min(1.0, self.confidence + 0.1)
    
    def weaken(self, evidence: str):
        """Add contradicting evidence and reduce confidence."""
        self.contradicting_evidence.append(evidence)
        self.confidence = max(0.0, self.confidence - 0.15)


@dataclass
class ReasoningContext:
    """Context for a reasoning session."""
    goal: str
    mode: CognitiveMode
    constraints: List[str] = field(default_factory=list)
    relevant_memories: List[Dict] = field(default_factory=list)
    emotional_state: str = "neutral"
    ethical_guidelines: List[str] = field(default_factory=list)
    max_depth: int = 10
    timeout_seconds: float = 30.0


class CognitiveModule:
    """Base class for cognitive modules registered with Unimind."""
    
    def __init__(self, name: str):
        self.name = name
        self.active = True
    
    def process(self, input_data: Any, context: ReasoningContext) -> List[Thought]:
        """Process input and return thoughts."""
        raise NotImplementedError
    
    def evaluate(self, thoughts: List[Thought]) -> float:
        """Evaluate a set of thoughts, return quality score 0-1."""
        raise NotImplementedError


class Unimind:
    """
    The Unified Mind - Central reasoning orchestrator.
    
    Coordinates multiple cognitive modules to produce integrated,
    contextually-aware reasoning outputs.
    """
    
    # Module type weights for decision making
    module_name = "unimind"
    dependencies = []
    
    DEFAULT_WEIGHTS = {
        "logic": 0.35,
        "emotion": 0.15,
        "memory": 0.25,
        "ethics": 0.15,
        "intuition": 0.10
    }
    
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.modules: Dict[str, List[CognitiveModule]] = {
            "logic": [],
            "emotion": [],
            "memory": [],
            "ethics": [],
            "intuition": []
        }
        self._kernel = None
        self._lock = threading.RLock()
        
        # Working memory - short-term storage during reasoning
        self.working_memory: List[Thought] = []
        self.max_working_memory = 50
        
        # Reasoning history for meta-cognition
        self.reasoning_history: List[Dict] = []
        self.max_history = 100
        
        # Current cognitive state
        self.current_mode = CognitiveMode.ANALYTICAL
        self.attention_focus: Optional[str] = None
        
        print("[Unimind] Core initialized.")
    
    def initialize(self, kernel) -> bool:
        """Initialize with kernel reference."""
        self._kernel = kernel
        
        # Subscribe to relevant kernel events
        if kernel:
            kernel.subscribe("emotion.changed", self._on_emotion_change)
            kernel.subscribe("memory.recalled", self._on_memory_recall)
            kernel.subscribe("ethics.alert", self._on_ethics_alert)
        
        print("[Unimind] Connected to kernel.")
        return True
    
    def start(self) -> bool:
        """Start the reasoning engine."""
        return True
    
    def stop(self) -> bool:
        """Stop the reasoning engine."""
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "status": "healthy",
            "working_memory_size": len(self.working_memory),
            "registered_modules": {k: len(v) for k, v in self.modules.items()},
            "current_mode": self.current_mode.value
        }
    
    def register(self, module_type: str, module: CognitiveModule):
        """Register a cognitive module."""
        if module_type in self.modules:
            self.modules[module_type].append(module)
            print(f"[Unimind] Registered {module_type} module: {module.name}")
        else:
            print(f"[Unimind] Unknown module type: {module_type}")
    
    def set_mode(self, mode: CognitiveMode):
        """Set the current cognitive mode."""
        old_mode = self.current_mode
        self.current_mode = mode
        
        # Adjust weights based on mode
        if mode == CognitiveMode.ANALYTICAL:
            self.weights = {"logic": 0.5, "emotion": 0.05, "memory": 0.25, "ethics": 0.15, "intuition": 0.05}
        elif mode == CognitiveMode.CREATIVE:
            self.weights = {"logic": 0.2, "emotion": 0.2, "memory": 0.2, "ethics": 0.1, "intuition": 0.3}
        elif mode == CognitiveMode.INTUITIVE:
            self.weights = {"logic": 0.15, "emotion": 0.15, "memory": 0.3, "ethics": 0.1, "intuition": 0.3}
        elif mode == CognitiveMode.EMPATHETIC:
            self.weights = {"logic": 0.15, "emotion": 0.4, "memory": 0.25, "ethics": 0.15, "intuition": 0.05}
        elif mode == CognitiveMode.REFLECTIVE:
            self.weights = {"logic": 0.3, "emotion": 0.1, "memory": 0.35, "ethics": 0.15, "intuition": 0.1}
        
        print(f"[Unimind] Mode changed: {old_mode.value} → {mode.value}")
    
    def think(
        self,
        prompt: str,
        context: ReasoningContext = None,
        depth: int = 0
    ) -> Dict[str, Any]:
        """
        Process a prompt through the unified reasoning system.
        
        Args:
            prompt: The input to reason about
            context: Optional reasoning context
            depth: Current recursion depth
            
        Returns:
            Reasoning result with thoughts, conclusion, and metadata
        """
        if context is None:
            context = ReasoningContext(
                goal=f"Respond to: {prompt}",
                mode=self.current_mode
            )
        
        start_time = datetime.utcnow()
        
        # Phase 1: Perception - gather initial thoughts from all modules
        raw_thoughts = self._perceive(prompt, context)
        
        # Phase 2: Integration - combine and weight thoughts
        integrated = self._integrate(raw_thoughts, context)
        
        # Phase 3: Evaluation - assess quality and coherence
        evaluation = self._evaluate(integrated, context)
        
        # Phase 4: Synthesis - form conclusion
        conclusion = self._synthesize(integrated, evaluation, context)
        
        # Update working memory
        self._update_working_memory(integrated)
        
        # Record in history
        result = {
            "prompt": prompt,
            "mode": context.mode.value,
            "thoughts": [self._thought_to_dict(t) for t in integrated[:10]],
            "evaluation": evaluation,
            "conclusion": conclusion,
            "confidence": evaluation.get("overall_confidence", 0.5),
            "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
            "depth": depth
        }
        
        self._record_history(result)
        
        return result
    
    def _perceive(self, prompt: str, context: ReasoningContext) -> Dict[str, List[Thought]]:
        """Gather thoughts from all cognitive modules."""
        thoughts_by_type = {}
        
        for module_type, modules in self.modules.items():
            thoughts_by_type[module_type] = []
            for module in modules:
                if module.active:
                    try:
                        module_thoughts = module.process(prompt, context)
                        thoughts_by_type[module_type].extend(module_thoughts)
                    except Exception as e:
                        print(f"[Unimind] Module {module.name} error: {e}")
        
        # If no modules registered, generate basic thoughts
        if not any(thoughts_by_type.values()):
            thoughts_by_type["logic"] = [
                Thought(
                    content=f"Analyzing: {prompt}",
                    thought_type="observation",
                    confidence=0.7,
                    source_module="unimind_default"
                )
            ]
        
        return thoughts_by_type
    
    def _integrate(
        self,
        thoughts_by_type: Dict[str, List[Thought]],
        context: ReasoningContext
    ) -> List[Thought]:
        """Integrate thoughts using weighted combination."""
        all_thoughts = []
        
        for module_type, thoughts in thoughts_by_type.items():
            weight = self.weights.get(module_type, 0.1)
            for thought in thoughts:
                # Adjust confidence by module weight
                thought.confidence *= weight
                all_thoughts.append(thought)
        
        # Sort by confidence
        all_thoughts.sort(key=lambda t: t.confidence, reverse=True)
        
        # Check for contradictions
        for i, thought in enumerate(all_thoughts):
            for other in all_thoughts[i+1:]:
                if self._are_contradictory(thought, other):
                    # Reduce confidence of lower-ranked thought
                    other.weaken(f"Contradicts: {thought.content[:50]}")
        
        return all_thoughts
    
    def _evaluate(
        self,
        thoughts: List[Thought],
        context: ReasoningContext
    ) -> Dict[str, Any]:
        """Evaluate the quality of integrated thoughts."""
        if not thoughts:
            return {"overall_confidence": 0.0, "coherence": 0.0, "completeness": 0.0}
        
        # Calculate metrics
        avg_confidence = sum(t.confidence for t in thoughts) / len(thoughts)
        
        # Check coherence (how well thoughts align)
        coherence = self._calculate_coherence(thoughts)
        
        # Check completeness (do we have thoughts from multiple modalities?)
        modalities_present = len(set(t.source_module.split('_')[0] for t in thoughts))
        completeness = min(1.0, modalities_present / 3)
        
        # Overall quality score
        overall = (avg_confidence * 0.4) + (coherence * 0.3) + (completeness * 0.3)
        
        return {
            "overall_confidence": overall,
            "average_thought_confidence": avg_confidence,
            "coherence": coherence,
            "completeness": completeness,
            "thought_count": len(thoughts),
            "modalities_used": modalities_present
        }
    
    def _synthesize(
        self,
        thoughts: List[Thought],
        evaluation: Dict[str, Any],
        context: ReasoningContext
    ) -> str:
        """Synthesize thoughts into a coherent conclusion."""
        if not thoughts:
            return "No thoughts generated."
        
        # Get top thoughts
        top_thoughts = [t for t in thoughts[:5] if t.confidence > 0.3]
        
        if not top_thoughts:
            return f"Low confidence analysis of: {context.goal}"
        
        # Build conclusion from thought contents
        conclusion_parts = []
        for t in top_thoughts:
            if t.thought_type == "conclusion":
                conclusion_parts.insert(0, t.content)
            elif t.thought_type == "inference":
                conclusion_parts.append(t.content)
            elif t.thought_type == "observation" and t.confidence > 0.5:
                conclusion_parts.append(t.content)
        
        if conclusion_parts:
            conclusion = " ".join(conclusion_parts[:3])
        else:
            conclusion = thoughts[0].content
        
        # Add confidence qualifier
        conf = evaluation.get("overall_confidence", 0.5)
        if conf < 0.3:
            conclusion = f"[Uncertain] {conclusion}"
        elif conf > 0.8:
            conclusion = f"[High confidence] {conclusion}"
        
        return conclusion
    
    def _calculate_coherence(self, thoughts: List[Thought]) -> float:
        """Calculate how coherent a set of thoughts are."""
        if len(thoughts) < 2:
            return 1.0
        
        # Simple heuristic: check for contradictions and supporting relationships
        contradictions = 0
        supports = 0
        
        for thought in thoughts:
            contradictions += len(thought.contradicting_evidence)
            supports += len(thought.supporting_evidence)
        
        total_relations = contradictions + supports
        if total_relations == 0:
            return 0.7  # Neutral coherence
        
        return supports / total_relations
    
    def _are_contradictory(self, t1: Thought, t2: Thought) -> bool:
        """Check if two thoughts contradict each other."""
        # Simple keyword-based detection
        negations = ["not", "cannot", "won't", "shouldn't", "impossible"]
        
        t1_has_negation = any(neg in t1.content.lower() for neg in negations)
        t2_has_negation = any(neg in t2.content.lower() for neg in negations)
        
        # If one has negation and other doesn't, and they're about similar topics
        if t1_has_negation != t2_has_negation:
            # Check for word overlap (very simple similarity)
            words1 = set(t1.content.lower().split())
            words2 = set(t2.content.lower().split())
            overlap = len(words1 & words2)
            if overlap > 2:
                return True
        
        return False
    
    def _update_working_memory(self, thoughts: List[Thought]):
        """Update working memory with new thoughts."""
        with self._lock:
            self.working_memory.extend(thoughts[:5])  # Keep top 5
            # Prune old thoughts
            if len(self.working_memory) > self.max_working_memory:
                self.working_memory = self.working_memory[-self.max_working_memory:]
    
    def _record_history(self, result: Dict):
        """Record reasoning result in history."""
        with self._lock:
            self.reasoning_history.append(result)
            if len(self.reasoning_history) > self.max_history:
                self.reasoning_history = self.reasoning_history[-self.max_history:]
    
    def _thought_to_dict(self, thought: Thought) -> Dict:
        """Convert thought to dictionary."""
        return {
            "content": thought.content,
            "type": thought.thought_type,
            "confidence": thought.confidence,
            "source": thought.source_module
        }
    
    # =========== Event Handlers ===========
    
    def _on_emotion_change(self, message):
        """React to emotion changes."""
        emotion = message.payload.get("emotion", "neutral")
        intensity = message.payload.get("intensity", 0.5)
        
        # Adjust weights based on emotional state
        if emotion in ["excited", "curious"]:
            self.weights["intuition"] = min(0.3, self.weights["intuition"] + 0.05)
        elif emotion in ["anxious", "frustrated"]:
            self.weights["logic"] = min(0.5, self.weights["logic"] + 0.05)
    
    def _on_memory_recall(self, message):
        """Handle memory recall events."""
        memories = message.payload.get("memories", [])
        for memory in memories[:3]:
            self.working_memory.append(
                Thought(
                    content=str(memory),
                    thought_type="memory",
                    confidence=0.6,
                    source_module="memory_recall"
                )
            )
    
    def _on_ethics_alert(self, message):
        """Handle ethics alerts."""
        # Boost ethics weight temporarily
        self.weights["ethics"] = min(0.4, self.weights["ethics"] + 0.1)
    
    # =========== Reflection API ===========
    
    def reflect(self) -> Dict[str, Any]:
        """
        Meta-cognitive reflection on recent reasoning.
        """
        reflection = {
            "timestamp": datetime.utcnow().isoformat(),
            "current_mode": self.current_mode.value,
            "working_memory_size": len(self.working_memory),
            "recent_reasoning_count": len(self.reasoning_history),
            "weight_distribution": self.weights.copy(),
            "insights": [],
            "recommendations": []
        }
        
        # Analyze recent history
        if self.reasoning_history:
            recent = self.reasoning_history[-10:]
            avg_confidence = sum(r.get("confidence", 0.5) for r in recent) / len(recent)
            
            if avg_confidence < 0.4:
                reflection["insights"].append("Recent reasoning has low confidence")
                reflection["recommendations"].append("Consider gathering more information")
            
            # Check for mode patterns
            modes = [r.get("mode", "analytical") for r in recent]
            if len(set(modes)) == 1:
                reflection["insights"].append(f"Operating in single mode: {modes[0]}")
                reflection["recommendations"].append("Consider trying different cognitive modes")
        
        # Working memory analysis
        if len(self.working_memory) > 40:
            reflection["insights"].append("Working memory is nearly full")
            reflection["recommendations"].append("Consider consolidating or clearing old thoughts")
        
        print(f"[Unimind] Reflection complete: {len(reflection['insights'])} insights")
        return reflection
    
    def clear_working_memory(self):
        """Clear working memory."""
        with self._lock:
            self.working_memory = []
        print("[Unimind] Working memory cleared.")
    
    def get_recent_thoughts(self, count: int = 10) -> List[Dict]:
        """Get recent thoughts from working memory."""
        with self._lock:
            return [self._thought_to_dict(t) for t in self.working_memory[-count:]]
