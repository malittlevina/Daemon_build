# world_engine/rules/causality.py
"""
Causality Engine - Symbolic cause-and-effect processing.

The causality engine tracks and processes chains of cause and effect,
enabling:
- Understanding WHY things happened
- Predicting consequences
- Narrative coherence
- Blame/credit attribution
"""

from typing import Dict, Any, Optional, List, Set, Tuple, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime
import uuid
import weakref

if TYPE_CHECKING:
    from world_engine.world_core import WorldEngine
    from world_engine.entities.entity import Entity


class CauseType(Enum):
    """Types of causal events."""
    PHYSICAL = auto()       # Physical interaction (collision, force)
    ENVIRONMENTAL = auto()  # Environmental effect (gravity, weather)
    AGENT = auto()          # Caused by an agent/NPC
    PLAYER = auto()         # Caused by player action
    SYSTEM = auto()         # System/rule generated
    NARRATIVE = auto()      # Narrative/story driven
    UNKNOWN = auto()        # Unknown or emergent


class EffectType(Enum):
    """Types of effects."""
    MOTION = auto()         # Position/velocity change
    STATE_CHANGE = auto()   # Property change
    CREATION = auto()       # Entity spawned
    DESTRUCTION = auto()    # Entity destroyed
    DAMAGE = auto()         # Health/integrity reduction
    TRIGGER = auto()        # Event triggered
    RELATIONSHIP = auto()   # Relationship change


@dataclass
class CausalEvent:
    """
    A single causal event in the chain.
    
    Represents something that happened, why it happened,
    and what resulted from it.
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = 0.0
    
    # What happened
    event_type: str = ""
    description: str = ""
    
    # Who/what was involved
    subject_id: Optional[str] = None  # Primary entity
    object_id: Optional[str] = None   # Secondary entity (if any)
    
    # Cause classification
    cause_type: CauseType = CauseType.UNKNOWN
    effect_type: EffectType = EffectType.STATE_CHANGE
    
    # The cause of this event
    cause_id: Optional[str] = None  # ID of the causing event
    
    # Effects spawned by this event
    effect_ids: List[str] = field(default_factory=list)
    
    # Properties before and after
    state_before: Dict[str, Any] = field(default_factory=dict)
    state_after: Dict[str, Any] = field(default_factory=dict)
    
    # Narrative weight (importance to story)
    narrative_weight: float = 1.0
    
    # Tags for filtering
    tags: Set[str] = field(default_factory=set)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CausalChain:
    """
    A chain of causally connected events.
    
    Represents a sequence of cause-and-effect from
    an initial trigger to final outcomes.
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "chain"
    
    # Root cause
    root_event_id: str = ""
    
    # All events in this chain
    event_ids: List[str] = field(default_factory=list)
    
    # Chain metadata
    start_time: float = 0.0
    end_time: Optional[float] = None
    is_complete: bool = False
    
    # Narrative properties
    narrative_arc: str = ""  # rising_action, climax, falling_action, etc.
    importance: float = 1.0
    
    # Involved entities
    entity_ids: Set[str] = field(default_factory=set)


class CausalityEngine:
    """
    Tracks and processes causal relationships in the world.
    
    The causality engine:
    - Records events and their causes
    - Builds causal chains
    - Enables "why did this happen?" queries
    - Predicts consequences of actions
    - Supports narrative analysis
    """
    
    def __init__(self, world: 'WorldEngine'):
        """Initialize the causality engine."""
        self.world = world
        
        # Event storage
        self._events: Dict[str, CausalEvent] = {}
        self._chains: Dict[str, CausalChain] = {}
        
        # Indexes
        self._events_by_entity: Dict[str, List[str]] = {}
        self._events_by_type: Dict[str, List[str]] = {}
        self._active_chains: Set[str] = set()
        
        # Pending effects (effects waiting to be processed)
        self._pending_effects: List[CausalEvent] = []
        
        # Prediction models
        self._consequence_predictors: Dict[str, Callable] = {}
        
        # History limits
        self._max_events = 10000
        self._max_chain_length = 100
        
        print("[CausalityEngine] Initialized")
    
    # =========================================================================
    # Event recording
    # =========================================================================
    
    def record_event(
        self,
        event_type: str,
        subject_id: str,
        cause_type: CauseType = CauseType.UNKNOWN,
        effect_type: EffectType = EffectType.STATE_CHANGE,
        object_id: str = None,
        cause_id: str = None,
        description: str = "",
        state_before: Dict[str, Any] = None,
        state_after: Dict[str, Any] = None,
        narrative_weight: float = 1.0,
        tags: Set[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Record a causal event."""
        event = CausalEvent(
            timestamp=self.world.time_manager.current_time,
            event_type=event_type,
            description=description,
            subject_id=subject_id,
            object_id=object_id,
            cause_type=cause_type,
            effect_type=effect_type,
            cause_id=cause_id,
            state_before=state_before or {},
            state_after=state_after or {},
            narrative_weight=narrative_weight,
            tags=tags or set(),
            metadata=metadata or {}
        )
        
        self._store_event(event)
        
        # Link to cause
        if cause_id and cause_id in self._events:
            self._events[cause_id].effect_ids.append(event.id)
            
            # Find or create chain
            self._add_to_chain(event, cause_id)
        else:
            # This is a root cause - start new chain
            self._start_chain(event)
        
        return event.id
    
    def record_collision(
        self,
        entity1_id: str,
        entity2_id: str,
        impact_force: float,
        cause_id: str = None
    ) -> str:
        """Record a collision event."""
        return self.record_event(
            event_type="collision",
            subject_id=entity1_id,
            object_id=entity2_id,
            cause_type=CauseType.PHYSICAL,
            effect_type=EffectType.MOTION,
            cause_id=cause_id,
            description=f"Collision with force {impact_force:.1f}",
            metadata={"impact_force": impact_force}
        )
    
    def record_destruction(
        self,
        entity_id: str,
        cause_id: str = None,
        cause_type: CauseType = CauseType.UNKNOWN
    ) -> str:
        """Record an entity destruction."""
        return self.record_event(
            event_type="destruction",
            subject_id=entity_id,
            cause_type=cause_type,
            effect_type=EffectType.DESTRUCTION,
            cause_id=cause_id,
            description="Entity destroyed",
            narrative_weight=2.0  # Destructions are narratively significant
        )
    
    def record_state_change(
        self,
        entity_id: str,
        property_name: str,
        old_value: Any,
        new_value: Any,
        cause_id: str = None,
        cause_type: CauseType = CauseType.SYSTEM
    ) -> str:
        """Record a state change."""
        return self.record_event(
            event_type="state_change",
            subject_id=entity_id,
            cause_type=cause_type,
            effect_type=EffectType.STATE_CHANGE,
            cause_id=cause_id,
            description=f"{property_name}: {old_value} -> {new_value}",
            state_before={property_name: old_value},
            state_after={property_name: new_value}
        )
    
    def record_agent_action(
        self,
        agent_id: str,
        action: str,
        target_id: str = None,
        is_player: bool = False
    ) -> str:
        """Record an agent's action."""
        return self.record_event(
            event_type=f"action.{action}",
            subject_id=agent_id,
            object_id=target_id,
            cause_type=CauseType.PLAYER if is_player else CauseType.AGENT,
            effect_type=EffectType.TRIGGER,
            description=f"Agent performed: {action}",
            narrative_weight=1.5 if is_player else 1.0
        )
    
    def _store_event(self, event: CausalEvent):
        """Store an event and update indexes."""
        self._events[event.id] = event
        
        # Index by entity
        if event.subject_id:
            if event.subject_id not in self._events_by_entity:
                self._events_by_entity[event.subject_id] = []
            self._events_by_entity[event.subject_id].append(event.id)
        
        # Index by type
        if event.event_type not in self._events_by_type:
            self._events_by_type[event.event_type] = []
        self._events_by_type[event.event_type].append(event.id)
        
        # Trim if too many events
        if len(self._events) > self._max_events:
            self._trim_old_events()
    
    def _trim_old_events(self):
        """Remove oldest events to stay under limit."""
        sorted_events = sorted(
            self._events.values(),
            key=lambda e: e.timestamp
        )
        
        to_remove = sorted_events[:len(sorted_events) - self._max_events]
        for event in to_remove:
            self._remove_event(event.id)
    
    def _remove_event(self, event_id: str):
        """Remove an event from storage."""
        if event_id not in self._events:
            return
        
        event = self._events[event_id]
        
        # Remove from indexes
        if event.subject_id and event.subject_id in self._events_by_entity:
            self._events_by_entity[event.subject_id].remove(event_id)
        
        if event.event_type in self._events_by_type:
            self._events_by_type[event.event_type].remove(event_id)
        
        del self._events[event_id]
    
    # =========================================================================
    # Causal chains
    # =========================================================================
    
    def _start_chain(self, root_event: CausalEvent):
        """Start a new causal chain from a root event."""
        chain = CausalChain(
            name=f"chain_{root_event.event_type}",
            root_event_id=root_event.id,
            event_ids=[root_event.id],
            start_time=root_event.timestamp
        )
        
        if root_event.subject_id:
            chain.entity_ids.add(root_event.subject_id)
        
        self._chains[chain.id] = chain
        self._active_chains.add(chain.id)
        
        # Store chain reference in event
        root_event.metadata["chain_id"] = chain.id
    
    def _add_to_chain(self, event: CausalEvent, cause_id: str):
        """Add an event to an existing chain."""
        cause_event = self._events.get(cause_id)
        if not cause_event:
            return
        
        chain_id = cause_event.metadata.get("chain_id")
        if not chain_id or chain_id not in self._chains:
            return
        
        chain = self._chains[chain_id]
        
        # Check chain length limit
        if len(chain.event_ids) >= self._max_chain_length:
            self._complete_chain(chain_id)
            return
        
        chain.event_ids.append(event.id)
        event.metadata["chain_id"] = chain_id
        
        if event.subject_id:
            chain.entity_ids.add(event.subject_id)
        if event.object_id:
            chain.entity_ids.add(event.object_id)
    
    def _complete_chain(self, chain_id: str):
        """Mark a chain as complete."""
        if chain_id not in self._chains:
            return
        
        chain = self._chains[chain_id]
        chain.is_complete = True
        chain.end_time = self.world.time_manager.current_time
        self._active_chains.discard(chain_id)
    
    # =========================================================================
    # Queries
    # =========================================================================
    
    def get_event(self, event_id: str) -> Optional[CausalEvent]:
        """Get an event by ID."""
        return self._events.get(event_id)
    
    def get_events_for_entity(self, entity_id: str) -> List[CausalEvent]:
        """Get all events involving an entity."""
        event_ids = self._events_by_entity.get(entity_id, [])
        return [self._events[eid] for eid in event_ids if eid in self._events]
    
    def get_events_by_type(self, event_type: str) -> List[CausalEvent]:
        """Get all events of a type."""
        event_ids = self._events_by_type.get(event_type, [])
        return [self._events[eid] for eid in event_ids if eid in self._events]
    
    def get_cause_chain(self, event_id: str) -> List[CausalEvent]:
        """
        Get the chain of causes leading to an event.
        
        Walks backward from effect to root cause.
        """
        chain = []
        current_id = event_id
        visited = set()
        
        while current_id and current_id not in visited:
            visited.add(current_id)
            event = self._events.get(current_id)
            if not event:
                break
            
            chain.append(event)
            current_id = event.cause_id
        
        return list(reversed(chain))  # Root cause first
    
    def get_effect_tree(self, event_id: str, max_depth: int = 10) -> Dict[str, Any]:
        """
        Get the tree of effects from an event.
        
        Walks forward from cause to all effects.
        """
        def build_tree(eid: str, depth: int) -> Dict[str, Any]:
            if depth >= max_depth:
                return {"id": eid, "truncated": True}
            
            event = self._events.get(eid)
            if not event:
                return {"id": eid, "missing": True}
            
            return {
                "id": event.id,
                "type": event.event_type,
                "timestamp": event.timestamp,
                "description": event.description,
                "effects": [
                    build_tree(effect_id, depth + 1)
                    for effect_id in event.effect_ids
                ]
            }
        
        return build_tree(event_id, 0)
    
    def why(self, entity_id: str, property_name: str = None) -> str:
        """
        Answer "why is this entity in this state?"
        
        Returns a natural language explanation.
        """
        events = self.get_events_for_entity(entity_id)
        if not events:
            return "No causal history found."
        
        # Filter by property if specified
        if property_name:
            events = [
                e for e in events
                if property_name in e.state_after or property_name in e.state_before
            ]
        
        if not events:
            return f"No events affecting {property_name} found."
        
        # Get most recent relevant event
        recent = sorted(events, key=lambda e: e.timestamp)[-1]
        
        # Build explanation
        chain = self.get_cause_chain(recent.id)
        
        explanations = []
        for event in chain:
            cause_desc = event.cause_type.name.lower()
            explanations.append(f"[{cause_desc}] {event.description}")
        
        return " → ".join(explanations)
    
    # =========================================================================
    # Prediction
    # =========================================================================
    
    def register_predictor(self, event_type: str, predictor: Callable):
        """Register a consequence predictor for an event type."""
        self._consequence_predictors[event_type] = predictor
    
    def predict_consequences(self, event_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Predict likely consequences of an event.
        
        Uses registered predictors and historical patterns.
        """
        predictions = []
        
        # Use registered predictor if available
        if event_type in self._consequence_predictors:
            pred = self._consequence_predictors[event_type](context)
            if pred:
                predictions.extend(pred)
        
        # Pattern-based prediction from history
        historical = self.get_events_by_type(event_type)
        if historical:
            # Count common effect types
            effect_counts: Dict[str, int] = {}
            for event in historical:
                for effect_id in event.effect_ids:
                    effect = self._events.get(effect_id)
                    if effect:
                        effect_counts[effect.event_type] = effect_counts.get(effect.event_type, 0) + 1
            
            # Predict most common effects
            for effect_type, count in sorted(effect_counts.items(), key=lambda x: -x[1])[:3]:
                probability = count / len(historical)
                predictions.append({
                    "type": effect_type,
                    "probability": probability,
                    "source": "historical_pattern"
                })
        
        return predictions
    
    # =========================================================================
    # Processing
    # =========================================================================
    
    def process(self, dt: float):
        """Process pending causal effects."""
        # Process any pending effects
        while self._pending_effects:
            effect = self._pending_effects.pop(0)
            self._store_event(effect)
        
        # Check for stale active chains
        current_time = self.world.time_manager.current_time
        for chain_id in list(self._active_chains):
            chain = self._chains.get(chain_id)
            if chain and chain.event_ids:
                last_event = self._events.get(chain.event_ids[-1])
                if last_event:
                    # Complete chains that haven't had activity for 60 seconds
                    if current_time - last_event.timestamp > 60:
                        self._complete_chain(chain_id)
    
    # =========================================================================
    # Statistics
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get causality engine statistics."""
        return {
            "total_events": len(self._events),
            "total_chains": len(self._chains),
            "active_chains": len(self._active_chains),
            "events_by_type": {
                t: len(ids) for t, ids in self._events_by_type.items()
            },
            "predictors": len(self._consequence_predictors)
        }
    
    def get_narrative_summary(self, limit: int = 10) -> List[str]:
        """Get a summary of the most narratively significant events."""
        events = sorted(
            self._events.values(),
            key=lambda e: e.narrative_weight * (1 / max(1, self.world.time_manager.current_time - e.timestamp)),
            reverse=True
        )[:limit]
        
        return [e.description for e in events]
