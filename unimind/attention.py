# unimind/attention.py
"""
Attention Mechanism - Focus management for cognitive processing

Manages what the system attends to:
- Selective attention (focus on relevant)
- Divided attention (parallel processing)
- Sustained attention (maintain focus)
- Attention switching (context changes)
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import math


class AttentionMode(Enum):
    """Modes of attention."""
    FOCUSED = "focused"       # Single task, deep processing
    DIVIDED = "divided"       # Multiple streams, shallow
    SCANNING = "scanning"     # Quick overview, broad
    SUSTAINED = "sustained"   # Long-term engagement
    ALERTING = "alerting"    # Monitoring for triggers


@dataclass
class AttentionTarget:
    """Something that can receive attention."""
    target_id: str
    content: str
    salience: float = 0.5        # How attention-grabbing (0-1)
    relevance: float = 0.5       # How relevant to current goal (0-1)
    priority: int = 1            # Explicit priority (1=highest)
    attended_at: Optional[datetime] = None
    attention_duration: float = 0.0  # Seconds of attention received
    decay_rate: float = 0.1      # How quickly salience decays
    
    def get_attention_weight(self) -> float:
        """Calculate current attention weight."""
        # Time-based decay
        if self.attended_at:
            elapsed = (datetime.utcnow() - self.attended_at).total_seconds()
            time_factor = math.exp(-self.decay_rate * elapsed / 60)
        else:
            time_factor = 1.0
        
        # Combine factors
        weight = (self.salience * 0.4 + self.relevance * 0.4 + (1 / self.priority) * 0.2) * time_factor
        return min(1.0, weight)


@dataclass
class AttentionState:
    """Current state of the attention system."""
    mode: AttentionMode = AttentionMode.FOCUSED
    focus_target: Optional[str] = None
    active_targets: Set[str] = field(default_factory=set)
    capacity_used: float = 0.0
    max_capacity: float = 1.0
    last_switch: datetime = field(default_factory=datetime.utcnow)
    interrupts_blocked: bool = False


class AttentionManager:
    """
    Manages attention allocation across cognitive processes.
    
    Based on cognitive psychology attention models:
    - Limited capacity resource
    - Selective filtering
    - Automatic vs controlled processing
    - Vigilance and arousal
    """
    
    def __init__(self, capacity: float = 1.0):
        self._state = AttentionState(max_capacity=capacity)
        self._targets: Dict[str, AttentionTarget] = {}
        self._attention_history: List[Dict] = []
        self._lock = threading.RLock()
        
        # Attention filters (what to ignore)
        self._filters: List[str] = []
        
        # Vigilance targets (always monitor)
        self._vigilance_targets: Set[str] = set()
        
        # Salience boosters (patterns that grab attention)
        self._salience_patterns = {
            "urgent": 0.3,
            "error": 0.25,
            "important": 0.2,
            "warning": 0.2,
            "critical": 0.35,
            "help": 0.15
        }
    
    def add_target(
        self,
        target_id: str,
        content: str,
        salience: float = 0.5,
        relevance: float = 0.5,
        priority: int = 1
    ) -> bool:
        """Add a potential attention target."""
        with self._lock:
            # Check filters
            if any(f in content.lower() for f in self._filters):
                return False
            
            # Apply salience boosters
            boosted_salience = salience
            for pattern, boost in self._salience_patterns.items():
                if pattern in content.lower():
                    boosted_salience = min(1.0, boosted_salience + boost)
            
            self._targets[target_id] = AttentionTarget(
                target_id=target_id,
                content=content,
                salience=boosted_salience,
                relevance=relevance,
                priority=priority
            )
            
            return True
    
    def remove_target(self, target_id: str):
        """Remove an attention target."""
        with self._lock:
            self._targets.pop(target_id, None)
            self._state.active_targets.discard(target_id)
            if self._state.focus_target == target_id:
                self._state.focus_target = None
    
    def attend(self, target_id: str) -> bool:
        """Direct attention to a specific target."""
        with self._lock:
            target = self._targets.get(target_id)
            if not target:
                return False
            
            # Check capacity
            weight = target.get_attention_weight()
            if self._state.capacity_used + weight > self._state.max_capacity:
                # Need to release something first
                self._release_lowest_priority()
            
            target.attended_at = datetime.utcnow()
            self._state.active_targets.add(target_id)
            self._state.capacity_used += weight
            
            if self._state.mode == AttentionMode.FOCUSED:
                self._state.focus_target = target_id
            
            self._record_attention(target_id, "attend")
            return True
    
    def release(self, target_id: str):
        """Release attention from a target."""
        with self._lock:
            target = self._targets.get(target_id)
            if target and target_id in self._state.active_targets:
                weight = target.get_attention_weight()
                self._state.capacity_used = max(0, self._state.capacity_used - weight)
                self._state.active_targets.discard(target_id)
                
                if self._state.focus_target == target_id:
                    self._state.focus_target = None
                
                # Record attention duration
                if target.attended_at:
                    target.attention_duration += (datetime.utcnow() - target.attended_at).total_seconds()
                
                self._record_attention(target_id, "release")
    
    def switch_focus(self, new_target_id: str) -> bool:
        """Switch focused attention to a new target."""
        with self._lock:
            if self._state.interrupts_blocked:
                return False
            
            # Release current focus
            if self._state.focus_target:
                self.release(self._state.focus_target)
            
            # Attend to new target
            success = self.attend(new_target_id)
            
            if success:
                self._state.last_switch = datetime.utcnow()
                self._record_attention(new_target_id, "switch")
            
            return success
    
    def set_mode(self, mode: AttentionMode):
        """Set attention mode."""
        with self._lock:
            old_mode = self._state.mode
            self._state.mode = mode
            
            # Adjust behavior based on mode
            if mode == AttentionMode.FOCUSED:
                # Release all but focus target
                to_release = [t for t in self._state.active_targets 
                             if t != self._state.focus_target]
                for tid in to_release:
                    self.release(tid)
            
            elif mode == AttentionMode.SCANNING:
                # Broaden attention, reduce depth
                self._state.max_capacity *= 1.5
                for target in self._targets.values():
                    target.decay_rate *= 2  # Faster decay in scanning
    
    def get_recommendations(self) -> List[Tuple[str, float, str]]:
        """Get attention recommendations based on current state."""
        recommendations = []
        
        with self._lock:
            # Sort targets by attention weight
            sorted_targets = sorted(
                self._targets.values(),
                key=lambda t: t.get_attention_weight(),
                reverse=True
            )
            
            # Recommend top targets not currently attended
            for target in sorted_targets[:5]:
                if target.target_id not in self._state.active_targets:
                    recommendations.append((
                        target.target_id,
                        target.get_attention_weight(),
                        target.content[:50] + "..." if len(target.content) > 50 else target.content
                    ))
        
        return recommendations
    
    def check_vigilance(self) -> List[str]:
        """Check vigilance targets for activation."""
        activated = []
        
        with self._lock:
            for vid in self._vigilance_targets:
                target = self._targets.get(vid)
                if target and target.salience > 0.7:
                    activated.append(vid)
        
        return activated
    
    def _release_lowest_priority(self):
        """Release the lowest priority attended target."""
        if not self._state.active_targets:
            return
        
        lowest = None
        lowest_weight = float('inf')
        
        for tid in self._state.active_targets:
            target = self._targets.get(tid)
            if target:
                weight = target.get_attention_weight()
                if weight < lowest_weight:
                    lowest = tid
                    lowest_weight = weight
        
        if lowest:
            self.release(lowest)
    
    def _record_attention(self, target_id: str, action: str):
        """Record attention action for analysis."""
        self._attention_history.append({
            "target": target_id,
            "action": action,
            "mode": self._state.mode.value,
            "capacity_used": self._state.capacity_used,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        if len(self._attention_history) > 500:
            self._attention_history = self._attention_history[-500:]
    
    def add_filter(self, pattern: str):
        """Add a pattern to filter out."""
        self._filters.append(pattern.lower())
    
    def add_vigilance_target(self, target_id: str):
        """Add a target to vigilance monitoring."""
        self._vigilance_targets.add(target_id)
    
    def block_interrupts(self, duration_seconds: float = 30):
        """Temporarily block attention interrupts."""
        self._state.interrupts_blocked = True
        
        def unblock():
            import time
            time.sleep(duration_seconds)
            self._state.interrupts_blocked = False
        
        threading.Thread(target=unblock, daemon=True).start()
    
    def get_state(self) -> Dict[str, Any]:
        """Get current attention state."""
        with self._lock:
            return {
                "mode": self._state.mode.value,
                "focus_target": self._state.focus_target,
                "active_targets": list(self._state.active_targets),
                "capacity_used": self._state.capacity_used,
                "max_capacity": self._state.max_capacity,
                "interrupts_blocked": self._state.interrupts_blocked,
                "target_count": len(self._targets)
            }
    
    def get_attention_summary(self) -> Dict[str, Any]:
        """Get summary of attention allocation."""
        with self._lock:
            total_attention_time = sum(
                t.attention_duration for t in self._targets.values()
            )
            
            most_attended = sorted(
                self._targets.values(),
                key=lambda t: t.attention_duration,
                reverse=True
            )[:5]
            
            return {
                "total_attention_time_seconds": total_attention_time,
                "switch_count": len([h for h in self._attention_history if h["action"] == "switch"]),
                "most_attended": [
                    {"id": t.target_id, "duration": t.attention_duration}
                    for t in most_attended
                ]
            }
