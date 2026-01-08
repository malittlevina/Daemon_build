"""
Kernel package for ThothOS daemon.

This layer provides OS-like coordination primitives (message bus, scheduler,
subsystem registry) so higher-level agent subsystems can interoperate through a
shared context instead of tight imports.
"""

from .kernel import Kernel

__all__ = ["Kernel"]
