# storyrealms/world_rules.py
"""
Story Realms World Rules System

Defines and enforces the laws, physics, magic systems, and constraints
that govern a Story Realm. AI-native design for symbolic rule processing.
"""

import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum


class RuleCategory(Enum):
    PHYSICS = "physics"           # Physical laws (gravity, collision)
    MAGIC = "magic"               # Magic system rules
    SOCIAL = "social"             # Social interactions, reputation
    ECONOMIC = "economic"         # Trade, currency, resources
    TEMPORAL = "temporal"         # Time-based rules (day/night, seasons)
    METAPHYSICAL = "metaphysical" # Death, resurrection, souls
    CONSTRAINT = "constraint"     # Hard limits and boundaries


class RulePriority(Enum):
    FUNDAMENTAL = 1     # Core laws that cannot be broken
    HIGH = 2            # Important rules with rare exceptions
    NORMAL = 3          # Standard rules
    LOW = 4             # Suggestions/soft rules
    OVERRIDE = 0        # Special rules that override others


@dataclass
class Rule:
    """
    A single rule governing the world.
    
    Rules can be:
    - Passive: Always in effect (e.g., gravity)
    - Triggered: Activated by conditions (e.g., magic spell effects)
    - Constraint: Prevent certain states (e.g., can't have negative health)
    """
    id: str
    name: str
    category: RuleCategory
    priority: RulePriority = RulePriority.NORMAL
    
    # Rule definition
    description: str = ""
    condition: Dict = field(default_factory=dict)  # When this rule applies
    effect: Dict = field(default_factory=dict)     # What the rule does
    
    # Rule metadata
    enabled: bool = True
    exceptions: List[Dict] = field(default_factory=list)  # Cases where rule doesn't apply
    
    # For triggered rules
    trigger_type: str = "passive"  # passive, on_event, on_action, periodic
    trigger_data: Dict = field(default_factory=dict)
    
    # Tracking
    times_enforced: int = 0
    last_enforced: Optional[float] = None
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data["category"] = self.category.value
        data["priority"] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Rule':
        data["category"] = RuleCategory(data["category"])
        data["priority"] = RulePriority(data["priority"])
        return cls(**data)


class WorldRules:
    """
    Manages and enforces rules within a Story Realm.
    
    Provides:
    - Rule definition and storage
    - Rule enforcement during world ticks
    - Magic system framework
    - Economic rules
    - Day/night and temporal cycles
    - Custom rule creation for unique realms
    """
    
    def __init__(self, world_engine, rules_module: str = "default"):
        self.world_engine = world_engine
        self.rules_module = rules_module
        self.rules: Dict[str, Rule] = {}
        
        # Category indices
        self.category_index: Dict[RuleCategory, List[str]] = {}
        
        # Rule handlers for different effect types
        self.effect_handlers: Dict[str, Callable] = {}
        
        # World constants (can be modified by rules)
        self.constants = {
            "gravity": 9.8,
            "time_scale": 1.0,
            "day_length": 24.0,  # World hours per day
            "max_health": 100,
            "max_energy": 100,
            "death_permanent": False,
            "magic_enabled": True,
            "currency_name": "gold"
        }
        
        # Current world state affected by rules
        self.world_state = {
            "time_of_day": 12.0,  # 0-24 hours
            "season": "spring",
            "weather": "clear",
            "day_count": 1
        }
        
        # Load default rules
        self._load_default_rules()
        
        # Register built-in effect handlers
        self._register_default_handlers()
        
        print(f"[WorldRules] Initialized with module: {rules_module}")
    
    # ─────────────────────────────────────────────────────────────────
    # RULE MANAGEMENT
    # ─────────────────────────────────────────────────────────────────
    
    def add_rule(self, rule: Rule) -> bool:
        """Add a rule to the world."""
        self.rules[rule.id] = rule
        
        # Index by category
        if rule.category not in self.category_index:
            self.category_index[rule.category] = []
        self.category_index[rule.category].append(rule.id)
        
        print(f"[WorldRules] Added rule: {rule.name} ({rule.category.value})")
        return True
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule from the world."""
        if rule_id not in self.rules:
            return False
        
        rule = self.rules.pop(rule_id)
        
        if rule.category in self.category_index:
            self.category_index[rule.category] = [
                rid for rid in self.category_index[rule.category] if rid != rule_id
            ]
        
        print(f"[WorldRules] Removed rule: {rule.name}")
        return True
    
    def enable_rule(self, rule_id: str, enabled: bool = True):
        """Enable or disable a rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = enabled
    
    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get a rule by ID."""
        return self.rules.get(rule_id)
    
    def get_rules_by_category(self, category: RuleCategory) -> List[Rule]:
        """Get all rules in a category."""
        rule_ids = self.category_index.get(category, [])
        return [self.rules[rid] for rid in rule_ids if rid in self.rules]
    
    def update_rules(self, updates: Dict):
        """Update rules from a payload."""
        if "constants" in updates:
            self.constants.update(updates["constants"])
        
        if "add_rules" in updates:
            for rule_data in updates["add_rules"]:
                rule = Rule.from_dict(rule_data)
                self.add_rule(rule)
        
        if "remove_rules" in updates:
            for rule_id in updates["remove_rules"]:
                self.remove_rule(rule_id)
        
        if "enable_rules" in updates:
            for rule_id in updates["enable_rules"]:
                self.enable_rule(rule_id, True)
        
        if "disable_rules" in updates:
            for rule_id in updates["disable_rules"]:
                self.enable_rule(rule_id, False)
    
    # ─────────────────────────────────────────────────────────────────
    # RULE ENFORCEMENT
    # ─────────────────────────────────────────────────────────────────
    
    def enforce_all(self):
        """Enforce all passive rules (called during world tick)."""
        # Sort rules by priority
        sorted_rules = sorted(
            [r for r in self.rules.values() if r.enabled],
            key=lambda r: r.priority.value
        )
        
        for rule in sorted_rules:
            if rule.trigger_type == "passive":
                self._enforce_rule(rule)
            elif rule.trigger_type == "periodic":
                # Check if enough time has passed
                interval = rule.trigger_data.get("interval", 1.0)
                if rule.last_enforced is None or \
                   (time.time() - rule.last_enforced) >= interval:
                    self._enforce_rule(rule)
    
    def enforce_on_event(self, event_type: str, event_data: Dict):
        """Enforce rules triggered by a specific event."""
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            if rule.trigger_type == "on_event":
                if rule.trigger_data.get("event_type") == event_type:
                    if self._check_condition(rule.condition, event_data):
                        self._enforce_rule(rule, event_data)
    
    def enforce_on_action(self, action_type: str, actor_id: str, target_id: str = None):
        """Enforce rules triggered by an action."""
        action_data = {
            "action_type": action_type,
            "actor_id": actor_id,
            "target_id": target_id
        }
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            if rule.trigger_type == "on_action":
                if rule.trigger_data.get("action_type") == action_type:
                    if self._check_condition(rule.condition, action_data):
                        self._enforce_rule(rule, action_data)
    
    def _enforce_rule(self, rule: Rule, context: Dict = None):
        """Execute a single rule's effect."""
        context = context or {}
        
        # Check for exceptions
        for exception in rule.exceptions:
            if self._check_condition(exception, context):
                return  # Exception applies, skip enforcement
        
        # Execute effect
        effect_type = rule.effect.get("type", "custom")
        handler = self.effect_handlers.get(effect_type)
        
        if handler:
            try:
                handler(rule, context)
                rule.times_enforced += 1
                rule.last_enforced = time.time()
            except Exception as e:
                print(f"[WorldRules] Error enforcing {rule.name}: {e}")
        else:
            # Custom effect - emit event for external handling
            self.world_engine._emit_event("rule_effect", {
                "rule_id": rule.id,
                "effect": rule.effect,
                "context": context
            })
    
    def _check_condition(self, condition: Dict, context: Dict) -> bool:
        """Check if a condition is met."""
        if not condition:
            return True
        
        cond_type = condition.get("type", "always")
        
        if cond_type == "always":
            return True
        
        elif cond_type == "never":
            return False
        
        elif cond_type == "time_of_day":
            min_hour = condition.get("min", 0)
            max_hour = condition.get("max", 24)
            return min_hour <= self.world_state["time_of_day"] <= max_hour
        
        elif cond_type == "entity_attribute":
            entity_id = condition.get("entity_id") or context.get("actor_id")
            attr_name = condition.get("attribute")
            expected = condition.get("value")
            operator = condition.get("operator", "eq")
            
            if self.world_engine._entity_manager:
                entity = self.world_engine._entity_manager.get(entity_id)
                if entity:
                    actual = entity.attributes.get(attr_name)
                    return self._compare(actual, expected, operator)
            return False
        
        elif cond_type == "world_state":
            key = condition.get("key")
            expected = condition.get("value")
            operator = condition.get("operator", "eq")
            actual = self.world_state.get(key)
            return self._compare(actual, expected, operator)
        
        elif cond_type == "and":
            return all(self._check_condition(c, context) for c in condition.get("conditions", []))
        
        elif cond_type == "or":
            return any(self._check_condition(c, context) for c in condition.get("conditions", []))
        
        elif cond_type == "not":
            return not self._check_condition(condition.get("condition", {}), context)
        
        return True
    
    def _compare(self, actual, expected, operator: str) -> bool:
        """Compare values using an operator."""
        if operator == "eq":
            return actual == expected
        elif operator == "ne":
            return actual != expected
        elif operator == "gt":
            return actual > expected
        elif operator == "lt":
            return actual < expected
        elif operator == "gte":
            return actual >= expected
        elif operator == "lte":
            return actual <= expected
        elif operator == "in":
            return actual in expected
        elif operator == "contains":
            return expected in actual
        return False
    
    # ─────────────────────────────────────────────────────────────────
    # EFFECT HANDLERS
    # ─────────────────────────────────────────────────────────────────
    
    def register_effect_handler(self, effect_type: str, handler: Callable):
        """Register a custom effect handler."""
        self.effect_handlers[effect_type] = handler
    
    def _register_default_handlers(self):
        """Register built-in effect handlers."""
        self.effect_handlers.update({
            "modify_entity": self._handle_modify_entity,
            "modify_world_state": self._handle_modify_world_state,
            "spawn_entity": self._handle_spawn_entity,
            "despawn_entity": self._handle_despawn_entity,
            "emit_event": self._handle_emit_event,
            "apply_damage": self._handle_apply_damage,
            "heal": self._handle_heal,
            "time_advance": self._handle_time_advance,
            "weather_change": self._handle_weather_change
        })
    
    def _handle_modify_entity(self, rule: Rule, context: Dict):
        """Modify an entity's attributes."""
        entity_id = rule.effect.get("entity_id") or context.get("target_id")
        modifications = rule.effect.get("modifications", {})
        
        if self.world_engine._entity_manager:
            entity = self.world_engine._entity_manager.get(entity_id)
            if entity:
                entity.attributes.update(modifications)
    
    def _handle_modify_world_state(self, rule: Rule, context: Dict):
        """Modify world state values."""
        modifications = rule.effect.get("modifications", {})
        self.world_state.update(modifications)
    
    def _handle_spawn_entity(self, rule: Rule, context: Dict):
        """Spawn an entity as a rule effect."""
        params = rule.effect.get("params", {})
        if self.world_engine._entity_manager:
            self.world_engine._entity_manager.spawn(**params)
    
    def _handle_despawn_entity(self, rule: Rule, context: Dict):
        """Despawn an entity as a rule effect."""
        entity_id = rule.effect.get("entity_id") or context.get("target_id")
        if self.world_engine._entity_manager and entity_id:
            self.world_engine._entity_manager.despawn(entity_id, reason=rule.name)
    
    def _handle_emit_event(self, rule: Rule, context: Dict):
        """Emit a world event."""
        event_type = rule.effect.get("event_type", "rule_triggered")
        event_data = rule.effect.get("event_data", {})
        event_data["rule_id"] = rule.id
        self.world_engine._emit_event(event_type, event_data)
    
    def _handle_apply_damage(self, rule: Rule, context: Dict):
        """Apply damage to an entity."""
        entity_id = rule.effect.get("entity_id") or context.get("target_id")
        amount = rule.effect.get("amount", 10)
        damage_type = rule.effect.get("damage_type", "physical")
        
        if self.world_engine._entity_manager:
            entity = self.world_engine._entity_manager.get(entity_id)
            if entity:
                health_comp = entity.get_component("health")
                if health_comp:
                    current = health_comp.data.get("current", 100)
                    health_comp.data["current"] = max(0, current - amount)
                    
                    if health_comp.data["current"] <= 0:
                        self.world_engine._emit_event("entity_death", {
                            "entity_id": entity_id,
                            "cause": damage_type
                        })
    
    def _handle_heal(self, rule: Rule, context: Dict):
        """Heal an entity."""
        entity_id = rule.effect.get("entity_id") or context.get("target_id")
        amount = rule.effect.get("amount", 10)
        
        if self.world_engine._entity_manager:
            entity = self.world_engine._entity_manager.get(entity_id)
            if entity:
                health_comp = entity.get_component("health")
                if health_comp:
                    current = health_comp.data.get("current", 100)
                    max_health = health_comp.data.get("max", self.constants["max_health"])
                    health_comp.data["current"] = min(max_health, current + amount)
    
    def _handle_time_advance(self, rule: Rule, context: Dict):
        """Advance world time."""
        hours = rule.effect.get("hours", 1.0)
        self.world_state["time_of_day"] = (self.world_state["time_of_day"] + hours) % self.constants["day_length"]
        
        # Check for day change
        if self.world_state["time_of_day"] < hours:
            self.world_state["day_count"] += 1
            self.world_engine._emit_event("new_day", {"day": self.world_state["day_count"]})
    
    def _handle_weather_change(self, rule: Rule, context: Dict):
        """Change the weather."""
        new_weather = rule.effect.get("weather", "clear")
        old_weather = self.world_state["weather"]
        self.world_state["weather"] = new_weather
        
        self.world_engine._emit_event("weather_changed", {
            "from": old_weather,
            "to": new_weather
        })
    
    # ─────────────────────────────────────────────────────────────────
    # DEFAULT RULES
    # ─────────────────────────────────────────────────────────────────
    
    def _load_default_rules(self):
        """Load the default rule set."""
        default_rules = [
            # Time progression
            Rule(
                id="time_cycle",
                name="Day/Night Cycle",
                category=RuleCategory.TEMPORAL,
                priority=RulePriority.FUNDAMENTAL,
                description="Time advances with each world tick",
                trigger_type="periodic",
                trigger_data={"interval": 1.0},
                effect={"type": "time_advance", "hours": 0.1}
            ),
            
            # Health regeneration
            Rule(
                id="natural_regen",
                name="Natural Health Regeneration",
                category=RuleCategory.PHYSICS,
                priority=RulePriority.NORMAL,
                description="Entities slowly regenerate health when not in combat",
                trigger_type="passive",
                condition={"type": "always"},
                effect={"type": "custom", "action": "regen_all_health"}
            ),
            
            # Death handling
            Rule(
                id="death_handling",
                name="Death Processing",
                category=RuleCategory.METAPHYSICAL,
                priority=RulePriority.HIGH,
                description="Handle entity death based on world settings",
                trigger_type="on_event",
                trigger_data={"event_type": "entity_death"},
                effect={"type": "custom", "action": "process_death"}
            ),
            
            # Night dangers
            Rule(
                id="night_danger",
                name="Night Dangers",
                category=RuleCategory.TEMPORAL,
                priority=RulePriority.NORMAL,
                description="Hostile creatures more active at night",
                trigger_type="passive",
                condition={"type": "time_of_day", "min": 20, "max": 24},
                effect={"type": "emit_event", "event_type": "night_active", "event_data": {"danger_level": "high"}}
            ),
            
            # Magic availability
            Rule(
                id="magic_system",
                name="Magic System Active",
                category=RuleCategory.MAGIC,
                priority=RulePriority.HIGH,
                description="Magic is available in this realm",
                trigger_type="passive",
                condition={"type": "always"},
                effect={"type": "modify_world_state", "modifications": {"magic_available": True}}
            )
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
    
    # ─────────────────────────────────────────────────────────────────
    # MAGIC SYSTEM FRAMEWORK
    # ─────────────────────────────────────────────────────────────────
    
    def define_magic_system(self, system_config: Dict):
        """
        Define a magic system for the realm.
        
        Config can include:
        - schools: List of magic schools (fire, ice, etc.)
        - mana_enabled: Whether mana is required
        - spell_types: Categories of spells
        - casting_rules: Requirements for casting
        """
        self.constants["magic_system"] = system_config
        
        # Create rules for each school
        schools = system_config.get("schools", [])
        for school in schools:
            school_rule = Rule(
                id=f"magic_school_{school['name']}",
                name=f"{school['name'].title()} Magic",
                category=RuleCategory.MAGIC,
                description=school.get("description", f"Rules for {school['name']} magic"),
                effect={"type": "custom", "school": school}
            )
            self.add_rule(school_rule)
    
    def can_cast_spell(self, caster_id: str, spell_id: str) -> Dict:
        """Check if an entity can cast a specific spell."""
        result = {"can_cast": True, "reasons": []}
        
        if not self.constants.get("magic_enabled", True):
            result["can_cast"] = False
            result["reasons"].append("Magic is disabled in this realm")
            return result
        
        # Check caster has enough mana
        if self.world_engine._entity_manager:
            caster = self.world_engine._entity_manager.get(caster_id)
            if caster:
                mana_comp = caster.get_component("mana")
                if mana_comp:
                    current_mana = mana_comp.data.get("current", 0)
                    # Future: Look up spell cost from spell registry
                    spell_cost = 10  # Placeholder
                    if current_mana < spell_cost:
                        result["can_cast"] = False
                        result["reasons"].append("Insufficient mana")
        
        return result
    
    # ─────────────────────────────────────────────────────────────────
    # ECONOMIC SYSTEM FRAMEWORK
    # ─────────────────────────────────────────────────────────────────
    
    def define_economy(self, economy_config: Dict):
        """
        Define the economic system for the realm.
        
        Config can include:
        - currency: Name and properties of currency
        - trading_rules: Rules for trade interactions
        - price_modifiers: Factors affecting prices
        """
        self.constants["economy"] = economy_config
        self.constants["currency_name"] = economy_config.get("currency", {}).get("name", "gold")
    
    def calculate_price(self, base_price: float, context: Dict = None) -> float:
        """Calculate the final price considering modifiers."""
        context = context or {}
        price = base_price
        
        # Apply modifiers from economy config
        economy = self.constants.get("economy", {})
        modifiers = economy.get("price_modifiers", [])
        
        for modifier in modifiers:
            mod_type = modifier.get("type")
            if mod_type == "time_of_day":
                # Night prices might be higher
                if self.world_state["time_of_day"] > 20:
                    price *= modifier.get("multiplier", 1.2)
            elif mod_type == "weather":
                if self.world_state["weather"] == modifier.get("weather"):
                    price *= modifier.get("multiplier", 1.0)
            elif mod_type == "reputation":
                # Better reputation = better prices
                rep = context.get("reputation", 0)
                price *= (1.0 - rep * 0.01)  # 1% discount per reputation point
        
        return round(price, 2)
    
    # ─────────────────────────────────────────────────────────────────
    # SERIALIZATION
    # ─────────────────────────────────────────────────────────────────
    
    def export_rules(self) -> Dict:
        """Export all rules for persistence."""
        return {
            "rules": [rule.to_dict() for rule in self.rules.values()],
            "constants": self.constants,
            "world_state": self.world_state
        }
    
    def import_rules(self, data: Dict):
        """Import rules from persisted data."""
        self.rules.clear()
        self.category_index.clear()
        
        for rule_data in data.get("rules", []):
            rule = Rule.from_dict(rule_data)
            self.add_rule(rule)
        
        self.constants.update(data.get("constants", {}))
        self.world_state.update(data.get("world_state", {}))
        
        print(f"[WorldRules] Imported {len(self.rules)} rules")
