# kernel/__init__.py
"""
ThothOS Kernel - The symbolic operating system core.

The kernel provides:
- Process/module lifecycle management
- Inter-module message passing
- Task scheduling and priority queuing
- Symbolic memory management
- System call interface for subsystems
- Interrupt and signal handling
- Boot loading for daemon modules
"""

from kernel.kernel_core import Kernel
from kernel.kernel_registry import KernelRegistry
from kernel.message_bus import MessageBus
from kernel.process_manager import ProcessManager
from kernel.scheduler import Scheduler
from kernel.memory_manager import MemoryManager
from kernel.syscall_interface import SyscallInterface
from kernel.interrupt_handler import InterruptHandler
from kernel.boot_loader import BootLoader

__all__ = [
    "Kernel",
    "KernelRegistry",
    "MessageBus",
    "ProcessManager",
    "Scheduler",
    "MemoryManager",
    "SyscallInterface",
    "InterruptHandler",
    "BootLoader"
]

__version__ = "1.0.0"
