# world_engine/rules/rule_engine.py
"""
Rule Engine - Symbolic rule processing for the world.

The rule engine allows defining world behaviors through
declarative rules rather than hardcoded logic.

Rules are AI-native - they can be:
- Learned from observation
- Modified by narrative context
- Reasoned about symbolically
"""

from typing import Dict, Any, Optional, List, Callable, Set, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum, auto
import uuid

if TYPE_CHECKING:
    from world_engine.world_core import WorldEngine
    from world_engine.entities.entity import Entity


class RuleCategory(Enum):
    """Categories of rules."""
    PHYSICS = auto()        # Physical laws
    INTERACTION = auto()    # Object interactions
    BEHAVIOR = auto()       # Entity behaviors
    ENVIRONMENTAL = auto()  # Environmental effects
    NARRATIVE = auto()      # Story/narrative rules
    SOCIAL = auto()         # Social interactions
    MAGIC = auto()          # Fantasy/magical rules


class RulePriority(Enum):
    """Rule priority for conflict resolution."""
    ABSOLUTE = 0     # Cannot be overridden (narrative fate)
    CRITICAL = 1     # Very important
    HIGH = 2         # High priority
    NORMAL = 3       # Default
    LOW = 4          # Low priority
    AMBIENT = 5      # Background rules


@dataclass
class RuleCondition:
    """
    A condition that must be met for a rule to fire.
    
    Conditions can check:
    - Entity properties
    - Relationships between entities
    - World state
    - Time conditions
    """
    
    condition_type: str = "always"  # always, has_tag, property, proximity, time, custom
    
    # For tag conditions
    tag: str = ""
    
    # For property conditions
    property_name: str = ""
    operator: str = "=="  # ==, !=, <, >, <=, >=, contains
    value: Any = None
    
    # For proximity conditions
    target_tag: str = ""
    distance: float = 5.0
    
    # For time conditions
    time_start: float = 0.0
    time_end: float = 24.0
    
    # For custom conditions
    predicate: Optional[Callable[['Entity', 'WorldEngine'], bool]] = None
    
    def evaluate(self, entity: 'Entity', world: 'WorldEngine') -> bool:
        """Evaluate the condition for an entity."""
        if self.condition_type == "always":
            return True
        
        elif self.condition_type == "has_tag":
            return entity.has_tag(self.tag)
        
        elif self.condition_type == "property":
            prop_value = entity.get_property(self.property_name)
            return self._compare(prop_value, self.operator, self.value)
        
        elif self.condition_type == "proximity":
            nearby = world.query_sphere(entity.position, self.distance)
            return any(e.has_tag(self.target_tag) for e in nearby if e.id != entity.id)
        
        elif self.condition_type == "time":
            hour = world.time_manager.hour
            return self.time_start <= hour < self.time_end
        
        elif self.condition_type == "custom" and self.predicate:
            return self.predicate(entity, world)
        
        return False
    
    def _compare(self, a: Any, op: str, b: Any) -> bool:
        """Compare values with operator."""
        if op == "==":
            return a == b
        elif op == "!=":
            return a != b
        elif op == "<":
            return a < b
        elif op == ">":
            return a > b
        elif op == "<=":
            return a <= b
        elif op == ">=":
            return a >= b
        elif op == "contains":
            return b in a if a else False
        return False


@dataclass
class RuleAction:
    """
    An action performed when a rule fires.
    """
    
    action_type: str = "none"  # none, set_property, add_tag, remove_tag, apply_force, spawn, destroy, emit_event, custom
    
    # For property actions
    property_name: str = ""
    value: Any = None
    
    # For tag actions
    tag: str = ""
    
    # For force actions
    force: Tuple[float, float, float] = (0, 0, 0)
    
    # For spawn actions
    spawn_template: str = ""
    spawn_offset: Tuple[float, float, float] = (0, 0, 0)
    
    # For event actions
    event_name: str = ""
    event_data: Dict[str, Any] = field(default_factory=dict)
    
    # For custom actions
    action_func: Optional[Callable[['Entity', 'WorldEngine'], None]] = None
    
    def execute(self, entity: 'Entity', world: 'WorldEngine'):
        """Execute the action on an entity."""
        if self.action_type == "set_property":
            entity.set_property(self.property_name, self.value)
        
        elif self.action_type == "add_tag":
            entity.add_tag(self.tag)
        
        elif self.action_type == "remove_tag":
            entity.remove_tag(self.tag)
        
        elif self.action_type == "apply_force":
            if entity.has_component("physics"):
                body = entity.get_component("physics")
                body.apply_force(self.force)
        
        elif self.action_type == "destroy":
            entity.destroy()
        
        elif self.action_type == "emit_event":
            if world.kernel:
                world.kernel.message_bus.emit(self.event_name, {
                    "entity_id": entity.id,
                    **self.event_data
                })
        
        elif self.action_type == "custom" and self.action_func:
            self.action_func(entity, world)


@dataclass
class Rule:
    """
    A symbolic rule that defines world behavior.
    
    Rules consist of:
    - Conditions: when should this rule apply
    - Actions: what happens when the rule fires
    - Metadata: priority, category, etc.
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "rule"
    description: str = ""
    
    # Classification
    category: RuleCategory = RuleCategory.PHYSICS
    priority: RulePriority = RulePriority.NORMAL
    
    # Conditions (all must be true)
    conditions: List[RuleCondition] = field(default_factory=list)
    
    # Actions (all executed when rule fires)
    actions: List[RuleAction] = field(default_factory=list)
    
    # Targeting
    target_tags: Set[str] = field(default_factory=set)  # Empty = all entities
    
    # Rate limiting
    cooldown: float = 0.0  # Seconds between firings
    max_fires_per_tick: int = 100
    
    # State
    enabled: bool = True
    
    # Tracking
    _last_fire_time: Dict[str, float] = field(default_factory=dict)
    _fires_this_tick: int = 0
    
    def can_fire(self, entity: 'Entity', world: 'WorldEngine') -> bool:
        """Check if rule can fire for an entity."""
        if not self.enabled:
            return False
        
        if self._fires_this_tick >= self.max_fires_per_tick:
            return False
        
        # Check cooldown
        if entity.id in self._last_fire_time:
            time_since = world.time_manager.current_time - self._last_fire_time[entity.id]
            if time_since < self.cooldown:
                return False
        
        # Check target tags
        if self.target_tags:
            if not entity.has_any_tag(list(self.target_tags)):
                return False
        
        # Check all conditions
        return all(cond.evaluate(entity, world) for cond in self.conditions)
    
    def fire(self, entity: 'Entity', world: 'WorldEngine'):
        """Fire the rule for an entity."""
        for action in self.actions:
            action.execute(entity, world)
        
        self._last_fire_time[entity.id] = world.time_manager.current_time
        self._fires_this_tick += 1
    
    def reset_tick(self):
        """Reset per-tick counters."""
        self._fires_this_tick = 0


class RuleEngine:
    """
    Processes symbolic rules for the world.
    
    The rule engine:
    - Evaluates rules each tick
    - Manages rule priorities and conflicts
    - Tracks rule statistics
    - Supports dynamic rule modification
    """
    
    def __init__(self, world: 'WorldEngine'):
        """Initialize the rule engine."""
        self.world = world
        
        # Rules organized by category
        self._rules: Dict[str, Rule] = {}
        self._rules_by_category: Dict[RuleCategory, List[str]] = {
            cat: [] for cat in RuleCategory
        }
        
        # Statistics
        self._stats = {
            "rules_evaluated": 0,
            "rules_fired": 0,
            "total_ticks": 0
        }
        
        print("[RuleEngine] Initialized")
    
    def add_rule(self, rule: Rule):
        """Add a rule to the engine."""
        self._rules[rule.id] = rule
        self._rules_by_category[rule.category].append(rule.id)
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule."""
        if rule_id not in self._rules:
            return False
        
        rule = self._rules[rule_id]
        self._rules_by_category[rule.category].remove(rule_id)
        del self._rules[rule_id]
        return True
    
    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)
    
    def get_rules_by_category(self, category: RuleCategory) -> List[Rule]:
        """Get all rules in a category."""
        return [
            self._rules[rid] for rid in self._rules_by_category[category]
            if rid in self._rules
        ]
    
    def evaluate(self, dt: float):
        """Evaluate all rules for all entities."""
        self._stats["total_ticks"] += 1
        
        # Reset per-tick counters
        for rule in self._rules.values():
            rule.reset_tick()
        
        # Get all entities
        entities = self.world.get_all_entities()
        
        # Sort rules by priority
        sorted_rules = sorted(
            self._rules.values(),
            key=lambda r: r.priority.value
        )
        
        # Evaluate rules
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            
            for entity in entities:
                self._stats["rules_evaluated"] += 1
                
                if rule.can_fire(entity, self.world):
                    rule.fire(entity, self.world)
                    self._stats["rules_fired"] += 1
                    
                    self.world.stats.rules_evaluated += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rule engine statistics."""
        return {
            **self._stats,
            "total_rules": len(self._rules),
            "enabled_rules": sum(1 for r in self._rules.values() if r.enabled)
        }


# Predefined rule builders

def create_proximity_rule(
    name: str,
    source_tag: str,
    target_tag: str,
    distance: float,
    action: RuleAction,
    cooldown: float = 1.0
) -> Rule:
    """Create a rule that fires when tagged entities are near each other."""
    return Rule(
        name=name,
        category=RuleCategory.INTERACTION,
        target_tags={source_tag},
        conditions=[
            RuleCondition(
                condition_type="proximity",
                target_tag=target_tag,
                distance=distance
            )
        ],
        actions=[action],
        cooldown=cooldown
    )


def create_time_rule(
    name: str,
    hour_start: int,
    hour_end: int,
    action: RuleAction,
    target_tags: Set[str] = None
) -> Rule:
    """Create a rule that fires during specific hours."""
    return Rule(
        name=name,
        category=RuleCategory.ENVIRONMENTAL,
        target_tags=target_tags or set(),
        conditions=[
            RuleCondition(
                condition_type="time",
                time_start=hour_start,
                time_end=hour_end
            )
        ],
        actions=[action],
        cooldown=60.0  # Once per minute
    )


def create_property_trigger(
    name: str,
    property_name: str,
    operator: str,
    value: Any,
    action: RuleAction
) -> Rule:
    """Create a rule that fires based on property values."""
    return Rule(
        name=name,
        category=RuleCategory.BEHAVIOR,
        conditions=[
            RuleCondition(
                condition_type="property",
                property_name=property_name,
                operator=operator,
                value=value
            )
        ],
        actions=[action]
    )
