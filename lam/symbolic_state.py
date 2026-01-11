# lam/symbolic_state.py
"""
Symbolic State - A structured representation of the system's current state

This module maintains a symbolic world model that enables:
- Context tracking across interactions
- State-based behavior triggers
- Goal and intention representation
- Constraint management
"""

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
import copy


class StateChangeType(Enum):
    """Types of state changes."""
    SET = "set"
    UPDATE = "update"
    DELETE = "delete"
    PUSH = "push"      # Add to list
    POP = "pop"        # Remove from list
    INCREMENT = "increment"
    DECREMENT = "decrement"


@dataclass
class StateChange:
    """Represents a change to the symbolic state."""
    path: str
    change_type: StateChangeType
    old_value: Any
    new_value: Any
    source: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


class SymbolicState:
    """
    Maintains the symbolic state of the system.
    
    The state is organized into domains:
    - context: Current conversation/task context
    - goals: Active goals and intentions
    - flags: Boolean state flags
    - history: Recent interaction history
    - entities: Known entities (users, objects, etc.)
    - constraints: Active constraints and rules
    """
    
    def __init__(self):
        self._state: Dict[str, Any] = {
            "context": {
                "mode": "idle",
                "current_task": None,
                "conversation_id": None,
                "last_interaction": None
            },
            "goals": {
                "active": [],
                "completed": [],
                "pending": []
            },
            "flags": {
                "is_learning": False,
                "has_active_task": False,
                "requires_attention": False,
                "in_reflection_mode": False
            },
            "history": [],
            "entities": {},
            "constraints": [],
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "version": 1
            }
        }
        
        self._lock = threading.RLock()
        self._change_history: List[StateChange] = []
        self._max_history = 100
        self._watchers: Dict[str, List[callable]] = {}
        self._kernel = None
        
        print("[SymbolicState] Initialized.")
    
    def set_kernel(self, kernel):
        """Connect to kernel for event publishing."""
        self._kernel = kernel
    
    def get(self, path: str = None) -> Any:
        """
        Get a value from state by dot-path.
        
        Examples:
            get("context.mode")
            get("flags.is_learning")
        """
        with self._lock:
            if path is None:
                return copy.deepcopy(self._state)
            
            parts = path.split('.')
            value = self._state
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                elif isinstance(value, list):
                    try:
                        idx = int(part)
                        value = value[idx]
                    except (ValueError, IndexError):
                        return None
                else:
                    return None
            return copy.deepcopy(value)
    
    def set(
        self,
        path: str,
        value: Any,
        source: str = "unknown"
    ) -> bool:
        """
        Set a value at the given path.
        
        Creates intermediate dicts if needed.
        """
        with self._lock:
            parts = path.split('.')
            target = self._state
            
            for part in parts[:-1]:
                if part not in target:
                    target[part] = {}
                target = target[part]
            
            key = parts[-1]
            old_value = target.get(key)
            target[key] = value
            
            self._record_change(path, StateChangeType.SET, old_value, value, source)
            self._notify_watchers(path, value, old_value)
            
            return True
    
    def update(self, path: str, updates: Dict[str, Any], source: str = "unknown") -> bool:
        """Update a dict at path with new values."""
        with self._lock:
            current = self.get(path)
            if not isinstance(current, dict):
                return False
            
            old_value = copy.deepcopy(current)
            current.update(updates)
            self.set(path, current, source)
            
            return True
    
    def push(self, path: str, value: Any, source: str = "unknown") -> bool:
        """Append a value to a list at path."""
        with self._lock:
            current = self.get(path)
            if current is None:
                current = []
            elif not isinstance(current, list):
                return False
            
            current.append(value)
            self.set(path, current, source)
            
            self._record_change(path, StateChangeType.PUSH, None, value, source)
            return True
    
    def pop(self, path: str, source: str = "unknown") -> Any:
        """Remove and return the last item from a list."""
        with self._lock:
            current = self.get(path)
            if not isinstance(current, list) or not current:
                return None
            
            value = current.pop()
            self.set(path, current, source)
            
            self._record_change(path, StateChangeType.POP, value, None, source)
            return value
    
    def delete(self, path: str, source: str = "unknown") -> bool:
        """Delete a value at path."""
        with self._lock:
            parts = path.split('.')
            target = self._state
            
            for part in parts[:-1]:
                if part not in target:
                    return False
                target = target[part]
            
            key = parts[-1]
            if key in target:
                old_value = target[key]
                del target[key]
                self._record_change(path, StateChangeType.DELETE, old_value, None, source)
                return True
            return False
    
    def increment(self, path: str, amount: int = 1, source: str = "unknown") -> int:
        """Increment a numeric value."""
        with self._lock:
            current = self.get(path) or 0
            new_value = current + amount
            self.set(path, new_value, source)
            self._record_change(path, StateChangeType.INCREMENT, current, new_value, source)
            return new_value
    
    def watch(self, path: str, callback: callable):
        """Register a watcher for changes at a path."""
        with self._lock:
            if path not in self._watchers:
                self._watchers[path] = []
            self._watchers[path].append(callback)
    
    def unwatch(self, path: str, callback: callable = None):
        """Remove a watcher."""
        with self._lock:
            if path in self._watchers:
                if callback:
                    self._watchers[path] = [w for w in self._watchers[path] if w != callback]
                else:
                    del self._watchers[path]
    
    def _notify_watchers(self, path: str, new_value: Any, old_value: Any):
        """Notify watchers of state change."""
        # Check for exact path watchers
        if path in self._watchers:
            for callback in self._watchers[path]:
                try:
                    callback(path, new_value, old_value)
                except Exception as e:
                    print(f"[SymbolicState] Watcher error: {e}")
        
        # Check for parent path watchers
        parts = path.split('.')
        for i in range(len(parts) - 1):
            parent_path = '.'.join(parts[:i+1])
            if parent_path in self._watchers:
                for callback in self._watchers[parent_path]:
                    try:
                        callback(path, new_value, old_value)
                    except Exception as e:
                        print(f"[SymbolicState] Parent watcher error: {e}")
        
        # Publish to kernel if connected
        if self._kernel:
            self._kernel.publish(
                f"state.changed.{path.replace('.', '_')}",
                {"path": path, "new_value": new_value, "old_value": old_value},
                "symbolic_state"
            )
    
    def _record_change(
        self,
        path: str,
        change_type: StateChangeType,
        old_value: Any,
        new_value: Any,
        source: str
    ):
        """Record a state change in history."""
        change = StateChange(
            path=path,
            change_type=change_type,
            old_value=old_value,
            new_value=new_value,
            source=source
        )
        
        with self._lock:
            self._change_history.append(change)
            if len(self._change_history) > self._max_history:
                self._change_history = self._change_history[-self._max_history:]
    
    def get_changes(self, since: datetime = None, path: str = None) -> List[StateChange]:
        """Get recent state changes."""
        with self._lock:
            changes = self._change_history
            if since:
                changes = [c for c in changes if c.timestamp >= since]
            if path:
                changes = [c for c in changes if c.path.startswith(path)]
            return list(changes)
    
    def snapshot(self) -> Dict[str, Any]:
        """Get a complete snapshot of current state."""
        with self._lock:
            return {
                "state": copy.deepcopy(self._state),
                "timestamp": datetime.utcnow().isoformat(),
                "version": self._state.get("metadata", {}).get("version", 1)
            }
    
    def restore(self, snapshot: Dict[str, Any]) -> bool:
        """Restore state from a snapshot."""
        with self._lock:
            if "state" in snapshot:
                self._state = copy.deepcopy(snapshot["state"])
                self._state["metadata"]["version"] = snapshot.get("version", 1) + 1
                print("[SymbolicState] State restored from snapshot.")
                return True
            return False


# Global instance
_symbolic_state = SymbolicState()


def update_state_with_input(user_input: str, source: str = "user") -> Optional[str]:
    """
    Process user input and update symbolic state accordingly.
    
    This function parses the input for intent signals and updates
    the state to reflect the user's goals and context.
    """
    try:
        # Log input in history
        _symbolic_state.push("history", {
            "input": user_input,
            "timestamp": datetime.utcnow().isoformat(),
            "source": source
        }, source)
        
        _symbolic_state.set("context.last_interaction", datetime.utcnow().isoformat(), source)
        
        input_lower = user_input.lower()
        result = None
        
        # Parse intent from input
        if "learn" in input_lower or "study" in input_lower:
            _symbolic_state.set("context.mode", "learning", source)
            _symbolic_state.set("flags.is_learning", True, source)
            
            # Extract topic if present
            import re
            topic_match = re.search(r'(?:learn|study)\s+(?:about\s+)?(.+)', input_lower)
            if topic_match:
                topic = topic_match.group(1).strip()
                _symbolic_state.set("context.current_topic", topic, source)
                result = f"[SymbolicState] Learning mode activated for topic: {topic}"
            else:
                result = "[SymbolicState] Learning mode activated."
                
        elif "task" in input_lower or "run" in input_lower or "execute" in input_lower:
            _symbolic_state.set("context.mode", "task_execution", source)
            _symbolic_state.set("flags.has_active_task", True, source)
            result = "[SymbolicState] Task execution mode activated."
            
        elif "optimize" in input_lower or "improve" in input_lower:
            _symbolic_state.set("context.mode", "optimization", source)
            result = "[SymbolicState] Optimization mode activated."
            
        elif "reflect" in input_lower or "think about" in input_lower:
            _symbolic_state.set("context.mode", "reflection", source)
            _symbolic_state.set("flags.in_reflection_mode", True, source)
            result = "[SymbolicState] Reflection mode activated."
            
        elif "help" in input_lower or "what can" in input_lower:
            _symbolic_state.set("context.mode", "assistance", source)
            result = "[SymbolicState] Assistance mode activated."
            
        else:
            # Default: conversational mode
            if _symbolic_state.get("flags.is_learning"):
                pass  # Stay in learning mode
            elif _symbolic_state.get("flags.has_active_task"):
                pass  # Stay in task mode
            else:
                _symbolic_state.set("context.mode", "conversational", source)
        
        print(f"[SymbolicState] Updated - Mode: {_symbolic_state.get('context.mode')}")
        return result
        
    except Exception as e:
        print(f"[SymbolicState Error] Failed to update state: {e}")
        return None


def get_current_state() -> Dict[str, Any]:
    """Get the current symbolic state."""
    return _symbolic_state.get()


def get_context() -> Dict[str, Any]:
    """Get the current context."""
    return _symbolic_state.get("context")


def get_flags() -> Dict[str, bool]:
    """Get current state flags."""
    return _symbolic_state.get("flags")


def reset_flags(source: str = "system"):
    """Reset all flags to default values."""
    _symbolic_state.set("flags", {
        "is_learning": False,
        "has_active_task": False,
        "requires_attention": False,
        "in_reflection_mode": False
    }, source)


def set_goal(goal: str, priority: int = 1, source: str = "user"):
    """Add an active goal."""
    _symbolic_state.push("goals.active", {
        "description": goal,
        "priority": priority,
        "created_at": datetime.utcnow().isoformat()
    }, source)


def complete_goal(goal_description: str, source: str = "system"):
    """Mark a goal as completed."""
    active = _symbolic_state.get("goals.active") or []
    for i, goal in enumerate(active):
        if goal.get("description") == goal_description:
            active.pop(i)
            goal["completed_at"] = datetime.utcnow().isoformat()
            _symbolic_state.push("goals.completed", goal, source)
            _symbolic_state.set("goals.active", active, source)
            return True
    return False
