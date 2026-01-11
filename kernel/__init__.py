# kernel/__init__.py
"""
ThothOS Kernel - The Central Nervous System

The kernel orchestrates all subsystems and provides:
- Message bus for inter-module communication
- Lifecycle management for all components
- Priority-based task scheduling
- Unified state access
- Event propagation
"""

from kernel.message_bus import MessageBus
from kernel.scheduler import KernelScheduler
from kernel.registry import ModuleRegistry
from kernel.kernel_core import ThothKernel

__all__ = ["ThothKernel", "MessageBus", "KernelScheduler", "ModuleRegistry"]
