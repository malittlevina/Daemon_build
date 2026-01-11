# unimind/cortex.py
# Advanced Unimind Cortex - The unified cognitive orchestration system

import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import json
import os

from unimind.neural_bus import NeuralBus, NeuralSignal, SignalType, Priority, get_neural_bus


class CognitiveState(Enum):
    """Overall cognitive states."""
    IDLE = "idle"                   # Low activity, waiting
    PROCESSING = "processing"       # Active processing
    FOCUSED = "focused"             # Deep focus on task
    LEARNING = "learning"           # Learning mode
    REFLECTING = "reflecting"       # Self-reflection
    DREAMING = "dreaming"           # Memory consolidation (offline)
    ALERT = "alert"                 # High arousal, threat detection


class ConsciousnessLevel(Enum):
    """Levels of consciousness/awareness."""
    UNCONSCIOUS = 0                 # Background processes only
    SUBCONSCIOUS = 1                # Preconscious processing
    AWARE = 2                       # Basic awareness
    CONSCIOUS = 3                   # Full conscious processing
    META_AWARE = 4                  # Self-aware, metacognition


@dataclass
class ThoughtUnit:
    """Represents a unit of thought/processing."""
    thought_id: str
    content: Any
    source_region: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    salience: float = 0.5           # How important/attention-grabbing
    valence: float = 0.0            # Emotional valence (-1 to 1)
    confidence: float = 0.5         # Confidence in this thought
    associations: List[str] = field(default_factory=list)  # Related thought IDs
    
    def to_dict(self) -> Dict:
        return {
            "thought_id": self.thought_id,
            "content": str(self.content)[:200],
            "source": self.source_region,
            "salience": self.salience,
            "valence": self.valence,
            "confidence": self.confidence
        }


@dataclass
class Goal:
    """Represents an active goal."""
    goal_id: str
    description: str
    priority: float = 0.5
    progress: float = 0.0
    subgoals: List[str] = field(default_factory=list)
    deadline: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "goal_id": self.goal_id,
            "description": self.description,
            "priority": self.priority,
            "progress": self.progress,
            "subgoals": self.subgoals
        }


class WorkingMemory:
    """
    Central working memory system.
    
    Implements Baddeley's model:
    - Central Executive: Attention control
    - Phonological Loop: Verbal/text processing
    - Visuospatial Sketchpad: Spatial/visual processing
    - Episodic Buffer: Integration with long-term memory
    """
    
    def __init__(self, capacity: int = 7):
        self.capacity = capacity  # Miller's magic number
        
        # Central Executive
        self.attention_focus: Optional[str] = None
        self.current_goal: Optional[Goal] = None
        
        # Phonological Loop (verbal/text)
        self.phonological_loop: deque = deque(maxlen=capacity)
        
        # Visuospatial Sketchpad
        self.visuospatial_pad: deque = deque(maxlen=capacity)
        
        # Episodic Buffer
        self.episodic_buffer: deque = deque(maxlen=capacity * 2)
        
        # All items with decay
        self.items: Dict[str, ThoughtUnit] = {}
        self.decay_rate = 0.1
        
    def store(self, thought: ThoughtUnit, buffer_type: str = "episodic"):
        """Store a thought in working memory."""
        self.items[thought.thought_id] = thought
        
        if buffer_type == "phonological":
            self.phonological_loop.append(thought.thought_id)
        elif buffer_type == "visuospatial":
            self.visuospatial_pad.append(thought.thought_id)
        else:
            self.episodic_buffer.append(thought.thought_id)
            
        # Enforce capacity
        self._enforce_capacity()
        
    def _enforce_capacity(self):
        """Remove oldest items if over capacity."""
        all_ids = set(self.phonological_loop) | set(self.visuospatial_pad) | set(self.episodic_buffer)
        
        # Remove items no longer in any buffer
        to_remove = [tid for tid in self.items if tid not in all_ids]
        for tid in to_remove:
            del self.items[tid]
            
    def retrieve(self, thought_id: str) -> Optional[ThoughtUnit]:
        """Retrieve a thought from working memory."""
        return self.items.get(thought_id)
    
    def get_contents(self) -> List[ThoughtUnit]:
        """Get all current working memory contents."""
        return list(self.items.values())
    
    def set_focus(self, focus: str):
        """Set attention focus."""
        self.attention_focus = focus
        
    def set_goal(self, goal: Goal):
        """Set current goal."""
        self.current_goal = goal
        
    def clear(self):
        """Clear working memory."""
        self.items.clear()
        self.phonological_loop.clear()
        self.visuospatial_pad.clear()
        self.episodic_buffer.clear()
        
    def apply_decay(self):
        """Apply decay to items, removing weak ones."""
        to_remove = []
        for tid, thought in self.items.items():
            thought.salience *= (1 - self.decay_rate)
            if thought.salience < 0.1:
                to_remove.append(tid)
                
        for tid in to_remove:
            del self.items[tid]
            
    def get_status(self) -> Dict:
        """Get working memory status."""
        return {
            "total_items": len(self.items),
            "phonological_count": len(self.phonological_loop),
            "visuospatial_count": len(self.visuospatial_pad),
            "episodic_count": len(self.episodic_buffer),
            "attention_focus": self.attention_focus,
            "current_goal": self.current_goal.to_dict() if self.current_goal else None,
            "capacity": self.capacity
        }


class UnimindCortex:
    """
    Advanced Unimind Cortex - The brain's orchestration center.
    
    This is the central cognitive system that:
    - Coordinates all brain regions via the neural bus
    - Maintains working memory and attention
    - Manages goals and executive function
    - Tracks consciousness and cognitive state
    - Provides unified processing cycles
    """
    
    def __init__(self, data_path: str = "data/unimind"):
        self.data_path = data_path
        os.makedirs(data_path, exist_ok=True)
        
        # Core systems
        self.neural_bus = get_neural_bus()
        self.working_memory = WorkingMemory()
        
        # State
        self.cognitive_state = CognitiveState.IDLE
        self.consciousness_level = ConsciousnessLevel.AWARE
        
        # Goals
        self.goals: Dict[str, Goal] = {}
        self.active_goal: Optional[str] = None
        
        # Self-model
        self.self_model = {
            "name": "Prometheus",
            "identity": "AI daemon of ThothOS",
            "capabilities": [],
            "current_task": None,
            "emotional_state": "neutral",
            "energy_level": 1.0
        }
        
        # Processing
        self.thought_stream: deque = deque(maxlen=100)
        self.cycle_count = 0
        self.last_cycle_time = 0.0
        
        # AI Model hooks
        self.ai_models: Dict[str, Any] = {}
        
        # Brain regions registry (actual modules)
        self.brain_regions: Dict[str, Any] = {}
        
        # Register cortex with neural bus
        self._register_with_bus()
        
        print("[UnimindCortex] Advanced cognitive system initialized.")
        
    def _register_with_bus(self):
        """Register cortex as central coordinator on neural bus."""
        self.neural_bus.register_region(
            region_id="cortex",
            name="Unimind Cortex",
            module_type="cortex",
            capabilities=["coordination", "attention", "executive", "consciousness"],
            handler=self._handle_signal
        )
        
    def _handle_signal(self, signal: NeuralSignal) -> Optional[NeuralSignal]:
        """Handle incoming signals to the cortex."""
        # Process based on signal type
        if signal.signal_type == SignalType.ATTENTION:
            self._process_attention(signal)
        elif signal.signal_type == SignalType.QUERY:
            return self._process_query(signal)
        elif signal.signal_type == SignalType.BROADCAST:
            self._process_broadcast(signal)
            
        # Create thought from signal
        thought = ThoughtUnit(
            thought_id=f"thought_{self.cycle_count}_{signal.signal_id[-6:]}",
            content=signal.payload,
            source_region=signal.source,
            salience=0.5 if signal.priority == Priority.NORMAL else 0.8
        )
        self.thought_stream.append(thought)
        
        return None
        
    def _process_attention(self, signal: NeuralSignal):
        """Process attention signal."""
        focus = signal.payload.get("focus")
        intensity = signal.payload.get("intensity", 1.0)
        
        self.working_memory.set_focus(focus)
        
        # Adjust arousal based on intensity
        self.neural_bus.set_arousal(min(1.0, self.neural_bus.global_arousal + intensity * 0.1))
        
    def _process_query(self, signal: NeuralSignal) -> Optional[NeuralSignal]:
        """Process query signal."""
        capability = signal.payload.get("capability")
        data = signal.payload.get("data", {})
        
        if capability == "working_memory":
            return NeuralSignal(
                signal_id=f"resp_{signal.signal_id}",
                signal_type=SignalType.RESPONSE,
                source="cortex",
                target=signal.source,
                payload={"working_memory": self.working_memory.get_status()}
            )
        elif capability == "goals":
            return NeuralSignal(
                signal_id=f"resp_{signal.signal_id}",
                signal_type=SignalType.RESPONSE,
                source="cortex",
                target=signal.source,
                payload={"goals": [g.to_dict() for g in self.goals.values()]}
            )
            
        return None
        
    def _process_broadcast(self, signal: NeuralSignal):
        """Process broadcast signal."""
        # Update self-model based on broadcasts
        if "arousal" in signal.payload:
            self.self_model["energy_level"] = signal.payload["arousal"]
        if "emotion" in signal.payload:
            self.self_model["emotional_state"] = signal.payload["emotion"]
            
    def register_brain_region(self, region_id: str, region_module: Any):
        """Register a brain region module."""
        self.brain_regions[region_id] = region_module
        
        # Extract capabilities if available
        if hasattr(region_module, 'capabilities'):
            self.self_model["capabilities"].extend(region_module.capabilities)
            
        print(f"[UnimindCortex] Registered brain region: {region_id}")
        
    def register_ai_model(self, model_id: str, model: Any, purpose: str):
        """
        Register an AI model for use in processing.
        
        Args:
            model_id: Unique identifier
            model: The model object (LLM, embedding model, etc.)
            purpose: What the model is for
        """
        self.ai_models[model_id] = {
            "model": model,
            "purpose": purpose,
            "registered_at": datetime.now().isoformat()
        }
        print(f"[UnimindCortex] Registered AI model: {model_id} ({purpose})")
        
    def set_goal(
        self,
        description: str,
        priority: float = 0.5,
        subgoals: List[str] = None
    ) -> Goal:
        """Set a new goal."""
        goal_id = f"goal_{int(time.time())}"
        
        goal = Goal(
            goal_id=goal_id,
            description=description,
            priority=priority,
            subgoals=subgoals or []
        )
        
        self.goals[goal_id] = goal
        
        # Set as active if highest priority
        if not self.active_goal or priority > self.goals.get(self.active_goal, Goal("", "", 0)).priority:
            self.active_goal = goal_id
            self.working_memory.set_goal(goal)
            
        # Broadcast goal
        self.neural_bus.emit_broadcast(
            source="cortex",
            payload={"new_goal": goal.to_dict()},
            priority="high"
        )
        
        print(f"[UnimindCortex] Set goal: {description}")
        return goal
        
    def update_goal_progress(self, goal_id: str, progress: float):
        """Update progress on a goal."""
        if goal_id in self.goals:
            self.goals[goal_id].progress = min(1.0, progress)
            
            if progress >= 1.0:
                print(f"[UnimindCortex] Goal completed: {self.goals[goal_id].description}")
                self._on_goal_complete(goal_id)
                
    def _on_goal_complete(self, goal_id: str):
        """Handle goal completion."""
        # Emit reward signal
        self.neural_bus.emit(
            source="cortex",
            signal_type="reward",
            payload={"goal_id": goal_id, "reward": 1.0},
            priority="high"
        )
        
        # Select next goal
        if self.active_goal == goal_id:
            del self.goals[goal_id]
            if self.goals:
                # Select highest priority remaining goal
                self.active_goal = max(self.goals.keys(), key=lambda g: self.goals[g].priority)
                self.working_memory.set_goal(self.goals[self.active_goal])
            else:
                self.active_goal = None
                
    def focus_attention(self, target: str, intensity: float = 1.0):
        """Direct attention to a target."""
        self.working_memory.set_focus(target)
        self.neural_bus.emit_attention("cortex", target, intensity)
        
    def set_cognitive_state(self, state: str):
        """Set the cognitive state."""
        self.cognitive_state = CognitiveState(state)
        
        # Adjust arousal based on state
        arousal_map = {
            CognitiveState.IDLE: 0.3,
            CognitiveState.PROCESSING: 0.5,
            CognitiveState.FOCUSED: 0.7,
            CognitiveState.LEARNING: 0.6,
            CognitiveState.REFLECTING: 0.4,
            CognitiveState.DREAMING: 0.2,
            CognitiveState.ALERT: 0.9
        }
        self.neural_bus.set_arousal(arousal_map.get(self.cognitive_state, 0.5))
        
    def run_cognitive_cycle(self) -> Dict[str, Any]:
        """
        Run one cognitive cycle - the fundamental processing loop.
        
        This is the "heartbeat" of the cognitive system.
        """
        cycle_start = time.time()
        self.cycle_count += 1
        
        result = {
            "cycle": self.cycle_count,
            "state": self.cognitive_state.value,
            "consciousness": self.consciousness_level.value,
            "actions": []
        }
        
        # 1. Process neural bus signals
        signals_processed = self.neural_bus.process_queue()
        result["signals_processed"] = signals_processed
        
        # 2. Apply working memory decay
        self.working_memory.apply_decay()
        
        # 3. Check goal progress
        if self.active_goal and self.active_goal in self.goals:
            result["active_goal"] = self.goals[self.active_goal].to_dict()
            
        # 4. State-specific processing
        if self.cognitive_state == CognitiveState.REFLECTING:
            self._run_reflection()
            result["actions"].append("reflection")
        elif self.cognitive_state == CognitiveState.LEARNING:
            self._run_learning()
            result["actions"].append("learning")
        elif self.cognitive_state == CognitiveState.DREAMING:
            self._run_consolidation()
            result["actions"].append("consolidation")
            
        # 5. Emit sync pulse
        self.neural_bus.emit_sync("cortex", {"cycle": self.cycle_count})
        
        # Record cycle time
        self.last_cycle_time = time.time() - cycle_start
        result["cycle_time_ms"] = self.last_cycle_time * 1000
        
        return result
        
    def _run_reflection(self):
        """Run self-reflection processing."""
        # Gather thoughts from stream
        recent_thoughts = list(self.thought_stream)[-10:]
        
        # Analyze for patterns (placeholder for AI model integration)
        patterns = []
        for thought in recent_thoughts:
            if thought.valence < -0.3:
                patterns.append(f"Negative thought from {thought.source_region}")
            elif thought.valence > 0.3:
                patterns.append(f"Positive thought from {thought.source_region}")
                
        if patterns:
            print(f"[UnimindCortex] Reflection found {len(patterns)} patterns")
            
    def _run_learning(self):
        """Run learning processing."""
        # Signal learning regions
        self.neural_bus.emit(
            source="cortex",
            signal_type="modulatory",
            payload={"mode": "learning", "enhance_plasticity": True},
            target=None,
            priority="normal"
        )
        
    def _run_consolidation(self):
        """Run memory consolidation (dreaming)."""
        # Signal hippocampus for replay
        self.neural_bus.emit(
            source="cortex",
            signal_type="modulatory",
            payload={"mode": "consolidation", "replay": True},
            target="hippocampus",
            priority="low"
        )
        
    def think(self, input_data: Any, context: Dict = None) -> Dict[str, Any]:
        """
        Main thinking entry point - process input through the cognitive system.
        
        Args:
            input_data: Input to process
            context: Additional context
            
        Returns:
            Thinking result
        """
        self.set_cognitive_state("processing")
        
        # Create thought from input
        thought = ThoughtUnit(
            thought_id=f"input_{int(time.time() * 1000)}",
            content=input_data,
            source_region="external",
            salience=0.8
        )
        
        # Store in working memory
        self.working_memory.store(thought)
        self.thought_stream.append(thought)
        
        # Broadcast to all regions
        self.neural_bus.emit_broadcast(
            source="cortex",
            payload={
                "type": "input",
                "content": input_data,
                "context": context or {},
                "thought_id": thought.thought_id
            },
            priority="high"
        )
        
        # Run cognitive cycle
        cycle_result = self.run_cognitive_cycle()
        
        # Gather responses from working memory
        wm_contents = self.working_memory.get_contents()
        
        result = {
            "input_thought": thought.to_dict(),
            "cycle": cycle_result,
            "working_memory_size": len(wm_contents),
            "cognitive_state": self.cognitive_state.value
        }
        
        return result
        
    def introspect(self) -> Dict[str, Any]:
        """
        Introspection - examine own cognitive state.
        
        Returns detailed self-analysis.
        """
        self.set_cognitive_state("reflecting")
        
        # Run reflection cycle
        self.run_cognitive_cycle()
        
        return {
            "self_model": self.self_model,
            "cognitive_state": self.cognitive_state.value,
            "consciousness_level": self.consciousness_level.name,
            "working_memory": self.working_memory.get_status(),
            "goals": [g.to_dict() for g in self.goals.values()],
            "active_goal": self.active_goal,
            "thought_stream_length": len(self.thought_stream),
            "recent_thoughts": [t.to_dict() for t in list(self.thought_stream)[-5:]],
            "brain_regions": list(self.brain_regions.keys()),
            "ai_models": list(self.ai_models.keys()),
            "neural_bus": self.neural_bus.get_bus_status(),
            "cycle_count": self.cycle_count,
            "last_cycle_time_ms": self.last_cycle_time * 1000
        }
        
    def get_status(self) -> Dict[str, Any]:
        """Get cortex status summary."""
        return {
            "state": self.cognitive_state.value,
            "consciousness": self.consciousness_level.name,
            "goals_count": len(self.goals),
            "active_goal": self.active_goal,
            "working_memory_items": len(self.working_memory.items),
            "cycle_count": self.cycle_count,
            "brain_regions": len(self.brain_regions),
            "ai_models": len(self.ai_models)
        }


# Global cortex instance
_cortex: Optional[UnimindCortex] = None


def get_cortex() -> UnimindCortex:
    """Get or create the global cortex instance."""
    global _cortex
    if _cortex is None:
        _cortex = UnimindCortex()
    return _cortex
