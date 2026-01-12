# lam/__init__.py
"""
LAM - Language Action Model
===========================
Plans and executes actions based on language understanding.
"""

from .lam_planner import plan_next_action
from .symbolic_state import update_state_with_input, symbolic_state

__all__ = [
    'plan_next_action',
    'update_state_with_input',
    'symbolic_state',
]
