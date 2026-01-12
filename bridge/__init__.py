# bridge/__init__.py
"""
Bridge - External System Connections
====================================
Bridges for connecting to external systems like ThothOS.
These connections are OPTIONAL - the daemon operates independently.
"""

from .thoth_bridge import ThothBridge
from .realm_interface import RealmInterface
from .memory_tree_interface import MemoryTreeInterface

__all__ = [
    'ThothBridge',
    'RealmInterface',
    'MemoryTreeInterface',
]
