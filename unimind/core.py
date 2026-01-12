# unimind/core.py
"""
Unimind - The Daemon's Central Cortex
=====================================
Unimind is the event bus and coordination center for all brain structures.
It routes signals between modules, coordinates thought processes, and
maintains the daemon's unified consciousness.

Architecture:
- Brain Regions: Specialized modules (emotion, memory, logic, language, etc.)
- Event Bus: Pub/sub system for inter-module communication
- Thought Pipeline: LLM → NLU → LAM coordination for coherent responses
- Working Memory: Short-term context for current processing
- Attention System: Prioritizes what to focus on
"""

import threading
import time
import queue
import json
import os
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime


class BrainRegion(Enum):
    """Brain regions/modules that Unimind coordinates."""
    # Core Processing
    CORTEX = "cortex"              # High-level reasoning (LLM)
    LANGUAGE = "language"          # NLU/speech processing
    PLANNER = "planner"            # LAM/action planning
    
    # Memory Systems
    HIPPOCAMPUS = "hippocampus"    # Memory formation (Observer)
    MEMORY = "memory"              # Memory retrieval (Memory Tree)
    
    # Emotional/Social
    LIMBIC = "limbic"              # Emotion engine
    SOCIAL = "social"              # Social reasoning
    
    # Perception
    VISUAL = "visual"              # Vision processing
    AUDITORY = "auditory"          # Audio processing
    SENSORY = "sensory"            # Device/sensor input
    
    # Executive
    EXECUTIVE = "executive"        # Decision making
    ETHICS = "ethics"              # Ethical evaluation (Guardian)
    
    # Motor/Action
    MOTOR = "motor"                # Action execution (Scrolls)
    
    # Knowledge
    CODEX = "codex"                # Knowledge base
    PROMETHEUS = "prometheus"      # Specializations


class SignalType(Enum):
    """Types of signals that flow through Unimind."""
    # Input signals
    USER_INPUT = "user_input"
    DEVICE_EVENT = "device_event"
    SENSOR_DATA = "sensor_data"
    SYSTEM_EVENT = "system_event"
    
    # Processing signals
    THOUGHT = "thought"
    QUERY = "query"
    INTENT = "intent"
    PLAN = "plan"
    
    # Internal signals
    EMOTION = "emotion"
    MEMORY_RECALL = "memory_recall"
    ATTENTION = "attention"
    
    # Output signals
    RESPONSE = "response"
    ACTION = "action"
    OBSERVATION = "observation"
    
    # Control signals
    PRIORITY = "priority"
    INTERRUPT = "interrupt"
    REFLECT = "reflect"


@dataclass
class Signal:
    """A signal flowing through the Unimind event bus."""
    id: str = field(default_factory=lambda: f"sig_{time.time_ns()}")
    signal_type: SignalType = SignalType.THOUGHT
    source: BrainRegion = BrainRegion.CORTEX
    target: Optional[BrainRegion] = None  # None = broadcast
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10, higher = more urgent
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'signal_type': self.signal_type.value,
            'source': self.source.value,
            'target': self.target.value if self.target else None,
            'payload': self.payload,
            'priority': self.priority,
            'timestamp': self.timestamp,
            'context': self.context
        }


@dataclass
class WorkingMemory:
    """Short-term memory for current processing context."""
    current_input: Optional[str] = None
    current_intent: Optional[str] = None
    current_emotion: str = "neutral"
    conversation_history: List[Dict] = field(default_factory=list)
    active_tasks: List[str] = field(default_factory=list)
    attention_focus: Optional[str] = None
    context_stack: List[Dict] = field(default_factory=list)
    
    def push_context(self, context: Dict):
        self.context_stack.append(context)
        if len(self.context_stack) > 10:
            self.context_stack.pop(0)
    
    def get_recent_context(self, n: int = 3) -> List[Dict]:
        return self.context_stack[-n:] if self.context_stack else []
    
    def add_to_conversation(self, role: str, content: str):
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': time.time()
        })
        # Keep last 20 exchanges
        if len(self.conversation_history) > 40:
            self.conversation_history = self.conversation_history[-40:]


class Unimind:
    """
    The Central Cortex - coordinates all brain regions and maintains
    unified consciousness for the daemon.
    """
    
    def __init__(self, config_path: str = "config/unimind_config.json"):
        self.config_path = config_path
        
        # Brain region registry
        self.regions: Dict[BrainRegion, Any] = {}
        self.region_handlers: Dict[BrainRegion, List[Callable[[Signal], Optional[Signal]]]] = {
            region: [] for region in BrainRegion
        }
        
        # Event bus
        self.signal_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.signal_handlers: Dict[SignalType, List[Callable[[Signal], None]]] = {
            st: [] for st in SignalType
        }
        
        # Working memory
        self.working_memory = WorkingMemory()
        
        # State
        self.is_active = False
        self.thought_count = 0
        self.start_time = time.time()
        
        # Processing thread
        self._processing_thread: Optional[threading.Thread] = None
        self._should_process = False
        
        # Attention weights
        self.attention_weights: Dict[BrainRegion, float] = {
            region: 1.0 for region in BrainRegion
        }
        
        # Load config
        self._load_config()
        
        print("[Unimind] Central cortex initialized.")
    
    def _load_config(self):
        """Load Unimind configuration."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Apply attention weights if present
                    if 'attention_weights' in config:
                        for region_name, weight in config['attention_weights'].items():
                            try:
                                region = BrainRegion(region_name)
                                self.attention_weights[region] = weight
                            except ValueError:
                                pass
            except Exception as e:
                print(f"[Unimind] Config load error: {e}")
    
    def _save_config(self):
        """Save Unimind configuration."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            config = {
                'attention_weights': {r.value: w for r, w in self.attention_weights.items()}
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"[Unimind] Config save error: {e}")
    
    # ==================
    # Region Management
    # ==================
    
    def register_region(self, region: BrainRegion, module: Any):
        """Register a brain region/module."""
        self.regions[region] = module
        print(f"[Unimind] Region registered: {region.value}")
    
    def get_region(self, region: BrainRegion) -> Optional[Any]:
        """Get a registered region module."""
        return self.regions.get(region)
    
    def register_handler(self, region: BrainRegion, handler: Callable[[Signal], Optional[Signal]]):
        """Register a signal handler for a region."""
        self.region_handlers[region].append(handler)
    
    def subscribe(self, signal_type: SignalType, handler: Callable[[Signal], None]):
        """Subscribe to a signal type."""
        self.signal_handlers[signal_type].append(handler)
    
    # ==================
    # Signal Processing
    # ==================
    
    def emit(self, signal: Signal):
        """Emit a signal to the event bus."""
        # Priority queue uses (priority, timestamp, signal) - lower priority number = higher priority
        self.signal_queue.put((10 - signal.priority, signal.timestamp, signal))
    
    def broadcast(
        self,
        signal_type: SignalType,
        payload: Dict[str, Any],
        source: BrainRegion = BrainRegion.CORTEX,
        priority: int = 5
    ):
        """Broadcast a signal to all regions."""
        signal = Signal(
            signal_type=signal_type,
            source=source,
            target=None,
            payload=payload,
            priority=priority
        )
        self.emit(signal)
    
    def send(
        self,
        signal_type: SignalType,
        target: BrainRegion,
        payload: Dict[str, Any],
        source: BrainRegion = BrainRegion.CORTEX,
        priority: int = 5
    ) -> Optional[Signal]:
        """Send a signal to a specific region and wait for response."""
        signal = Signal(
            signal_type=signal_type,
            source=source,
            target=target,
            payload=payload,
            priority=priority
        )
        
        # Process synchronously for direct sends
        return self._process_signal(signal)
    
    def _process_signal(self, signal: Signal) -> Optional[Signal]:
        """Process a single signal."""
        response = None
        
        # Notify subscribers
        for handler in self.signal_handlers.get(signal.signal_type, []):
            try:
                handler(signal)
            except Exception as e:
                print(f"[Unimind] Handler error for {signal.signal_type}: {e}")
        
        # Route to target region(s)
        if signal.target:
            # Specific target
            handlers = self.region_handlers.get(signal.target, [])
            for handler in handlers:
                try:
                    result = handler(signal)
                    if result:
                        response = result
                except Exception as e:
                    print(f"[Unimind] Region handler error: {e}")
        else:
            # Broadcast to all regions
            for region, handlers in self.region_handlers.items():
                weight = self.attention_weights.get(region, 1.0)
                if weight > 0:
                    for handler in handlers:
                        try:
                            result = handler(signal)
                            if result:
                                response = result
                        except Exception as e:
                            print(f"[Unimind] Broadcast handler error: {e}")
        
        return response
    
    def _processing_loop(self):
        """Background signal processing loop."""
        while self._should_process:
            try:
                # Get next signal (with timeout to allow stopping)
                try:
                    _, _, signal = self.signal_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                self._process_signal(signal)
                self.thought_count += 1
                
            except Exception as e:
                print(f"[Unimind] Processing error: {e}")
    
    def start(self):
        """Start Unimind processing."""
        if self.is_active:
            return
        
        self.is_active = True
        self._should_process = True
        self._processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self._processing_thread.start()
        print("[Unimind] Processing started.")
    
    def stop(self):
        """Stop Unimind processing."""
        self._should_process = False
        if self._processing_thread:
            self._processing_thread.join(timeout=2.0)
        self.is_active = False
        print("[Unimind] Processing stopped.")
    
    # ==================
    # Thought Pipeline
    # ==================
    
    def think(self, input_text: str, source: str = "user") -> str:
        """
        Main thought pipeline - processes input through LLM/NLU/LAM.
        
        Pipeline:
        1. Receive input
        2. Update working memory
        3. NLU: Understand intent
        4. Memory: Recall relevant context
        5. Emotion: Assess emotional context
        6. LLM/Cortex: Generate response/reasoning
        7. LAM: Plan actions if needed
        8. Ethics: Validate response
        9. Return response
        """
        self.working_memory.current_input = input_text
        self.working_memory.add_to_conversation("user", input_text)
        
        result = {
            'input': input_text,
            'intent': None,
            'emotion': self.working_memory.current_emotion,
            'memory_context': [],
            'response': None,
            'actions': []
        }
        
        # Step 1: NLU - Understand intent
        nlu_signal = self.send(
            SignalType.QUERY,
            BrainRegion.LANGUAGE,
            {'text': input_text, 'task': 'understand'}
        )
        if nlu_signal:
            result['intent'] = nlu_signal.payload.get('intent')
            self.working_memory.current_intent = result['intent']
        
        # Step 2: Memory - Recall context
        memory_signal = self.send(
            SignalType.MEMORY_RECALL,
            BrainRegion.MEMORY,
            {'query': input_text, 'limit': 5}
        )
        if memory_signal:
            result['memory_context'] = memory_signal.payload.get('memories', [])
        
        # Step 3: Emotion - Assess state
        emotion_signal = self.send(
            SignalType.QUERY,
            BrainRegion.LIMBIC,
            {'input': input_text, 'context': result}
        )
        if emotion_signal:
            result['emotion'] = emotion_signal.payload.get('emotion', 'neutral')
            self.working_memory.current_emotion = result['emotion']
        
        # Step 4: Cortex - Reason and generate response
        cortex_signal = self.send(
            SignalType.THOUGHT,
            BrainRegion.CORTEX,
            {
                'input': input_text,
                'intent': result['intent'],
                'context': result['memory_context'],
                'emotion': result['emotion'],
                'conversation': self.working_memory.conversation_history[-6:]
            }
        )
        if cortex_signal:
            result['response'] = cortex_signal.payload.get('response')
        
        # Step 5: LAM - Plan actions if needed
        if result['intent'] and 'action' in str(result['intent']).lower():
            planner_signal = self.send(
                SignalType.PLAN,
                BrainRegion.PLANNER,
                {'intent': result['intent'], 'input': input_text}
            )
            if planner_signal:
                result['actions'] = planner_signal.payload.get('actions', [])
        
        # Step 6: Ethics - Validate
        ethics_signal = self.send(
            SignalType.QUERY,
            BrainRegion.ETHICS,
            {'response': result['response'], 'actions': result['actions']}
        )
        if ethics_signal and not ethics_signal.payload.get('approved', True):
            result['response'] = "[Response modified for ethical compliance]"
        
        # Store in working memory
        self.working_memory.push_context(result)
        if result['response']:
            self.working_memory.add_to_conversation("assistant", result['response'])
        
        # Emit observation for memory
        self.broadcast(
            SignalType.OBSERVATION,
            {'input': input_text, 'response': result['response']},
            source=BrainRegion.CORTEX
        )
        
        return result.get('response') or f"[Unimind] Processed: {input_text}"
    
    def reflect(self):
        """Trigger self-reflection across all regions."""
        print("[Unimind] Initiating reflection cycle...")
        
        self.broadcast(
            SignalType.REFLECT,
            {
                'working_memory': {
                    'emotion': self.working_memory.current_emotion,
                    'attention': self.working_memory.attention_focus,
                    'active_tasks': self.working_memory.active_tasks
                },
                'uptime': time.time() - self.start_time,
                'thought_count': self.thought_count
            },
            priority=3
        )
    
    # ==================
    # Attention System
    # ==================
    
    def focus_attention(self, region: BrainRegion, weight: float = 1.5):
        """Increase attention to a specific region."""
        self.attention_weights[region] = min(2.0, weight)
        self.working_memory.attention_focus = region.value
    
    def relax_attention(self, region: BrainRegion):
        """Return a region to normal attention."""
        self.attention_weights[region] = 1.0
    
    def get_attention_state(self) -> Dict[str, float]:
        """Get current attention weights."""
        return {r.value: w for r, w in self.attention_weights.items()}
    
    # ==================
    # Status & Diagnostics
    # ==================
    
    def get_status(self) -> Dict[str, Any]:
        """Get Unimind status."""
        return {
            'is_active': self.is_active,
            'uptime_seconds': time.time() - self.start_time,
            'thought_count': self.thought_count,
            'registered_regions': [r.value for r in self.regions.keys()],
            'queue_size': self.signal_queue.qsize(),
            'working_memory': {
                'current_emotion': self.working_memory.current_emotion,
                'attention_focus': self.working_memory.attention_focus,
                'active_tasks': self.working_memory.active_tasks,
                'conversation_length': len(self.working_memory.conversation_history)
            },
            'attention_weights': self.get_attention_state()
        }
    
    def describe(self) -> str:
        """Get a description of Unimind state."""
        status = self.get_status()
        uptime_min = int(status['uptime_seconds'] / 60)
        
        lines = [
            "🧠 Unimind - Central Cortex",
            "",
            f"Status: {'Active' if status['is_active'] else 'Dormant'}",
            f"Uptime: {uptime_min} minutes",
            f"Thoughts processed: {status['thought_count']}",
            f"Active regions: {len(status['registered_regions'])}",
            f"Current emotion: {status['working_memory']['current_emotion']}",
        ]
        
        if status['working_memory']['attention_focus']:
            lines.append(f"Attention focus: {status['working_memory']['attention_focus']}")
        
        return "\n".join(lines)
    
    def shutdown(self):
        """Shutdown Unimind."""
        print("[Unimind] Shutting down...")
        self.stop()
        self._save_config()
        print("[Unimind] Shutdown complete.")


# Global Unimind instance
_unimind: Optional[Unimind] = None


def get_unimind() -> Unimind:
    """Get or create the global Unimind instance."""
    global _unimind
    if _unimind is None:
        _unimind = Unimind()
    return _unimind


def think(input_text: str) -> str:
    """Convenience function to process a thought."""
    return get_unimind().think(input_text)
