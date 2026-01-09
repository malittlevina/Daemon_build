# world_engine/rules/__init__.py
"""
Rules and Causality system for the World Engine.

Provides:
- Symbolic rule definitions
- Cause-and-effect chains
- Affordances (what objects can do)
- Narrative rule modifiers
"""

from world_engine.rules.rule_engine import RuleEngine, Rule, RuleCondition
from world_engine.rules.causality import CausalityEngine, CausalEvent, CausalChain

__all__ = [
    "RuleEngine",
    "Rule",
    "RuleCondition",
    "CausalityEngine",
    "CausalEvent",
    "CausalChain"
]
