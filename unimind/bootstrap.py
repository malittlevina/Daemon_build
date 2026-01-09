from __future__ import annotations

from typing import Any, Optional

from unimind.core import Unimind
from unimind.subsystems import EmotionSubsystem, EthicsSubsystem, LamSubsystem, MemorySubsystem


def attach_default_subsystems(
    unimind: Unimind,
    *,
    emotion_engine: Optional[Any] = None,
    memory_logger: Optional[Any] = None,
    ethical_core: Optional[Any] = None,
    lam_state_module: Optional[Any] = None,
    lam_planner_module: Optional[Any] = None,
) -> Unimind:
    """
    Attach canonical subsystems to Unimind.

    This keeps wiring out of `main.py` and ensures that Unimind stays contextually
    aware of connected subsystems as the OS grows.
    """

    if emotion_engine is not None:
        unimind.attach(EmotionSubsystem(emotion_engine))
    if memory_logger is not None:
        unimind.attach(MemorySubsystem(memory_logger))
    if ethical_core is not None:
        unimind.attach(EthicsSubsystem(ethical_core))
    if lam_state_module is not None and lam_planner_module is not None:
        unimind.attach(LamSubsystem(lam_state_module, lam_planner_module))
    return unimind

