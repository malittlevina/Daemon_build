# kernel/kernel_registry.py
"""
Kernel Registry - Central registry of all active modules and services.

The registry provides:
- Module discovery and registration
- Service location and dependency resolution
- Component lifecycle tracking
- Symbolic namespace management
"""

import threading
from typing import Dict, Any, Optional, List, Type, Callable
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime


class ModuleType(Enum):
    """Types of registrable modules."""
    CORE = auto()          # Core kernel subsystems
    ENGINE = auto()        # Processing engines (NLU, Emotion, etc.)
    SENSOR = auto()        # Input sensors (vision, audio, etc.)
    BRIDGE = auto()        # External bridges and interfaces
    STORAGE = auto()       # Storage and memory systems
    EXECUTOR = auto()      # Code and action executors
    RITUAL = auto()        # Ritual and scroll processors
    UTILITY = auto()       # Utility modules


class ModuleState(Enum):
    """Module lifecycle states."""
    REGISTERED = auto()
    INITIALIZING = auto()
    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPING = auto()
    STOPPED = auto()
    ERROR = auto()


@dataclass
class ModuleInfo:
    """Information about a registered module."""
    name: str
    module_type: ModuleType
    instance: Any
    state: ModuleState = ModuleState.REGISTERED
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    registered_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class KernelRegistry:
    """
    Central registry for all daemon modules and services.
    
    Provides:
    - Module registration and discovery
    - Service location
    - Dependency injection support
    - Symbolic namespace for daemon components
    """
    
    def __init__(self, kernel):
        """Initialize the registry."""
        self.kernel = kernel
        self._modules: Dict[str, ModuleInfo] = {}
        self._services: Dict[str, Callable] = {}
        self._namespaces: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        
        # Built-in namespaces
        self._namespaces["kernel"] = {}
        self._namespaces["modules"] = {}
        self._namespaces["services"] = {}
        
        print("[KernelRegistry] Initialized")
    
    # =========================================================================
    # Module registration
    # =========================================================================
    
    def register_module(
        self,
        name: str,
        instance: Any,
        module_type: ModuleType = ModuleType.UTILITY,
        version: str = "1.0.0",
        dependencies: List[str] = None,
        provides: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Register a module with the kernel.
        
        Args:
            name: Unique module name
            instance: The module instance
            module_type: Type classification
            version: Module version
            dependencies: List of required module names
            provides: List of capabilities this module provides
            metadata: Additional metadata
        
        Returns:
            True if registration successful
        """
        with self._lock:
            if name in self._modules:
                print(f"[KernelRegistry] Module '{name}' already registered")
                return False
            
            # Check dependencies
            missing_deps = self._check_dependencies(dependencies or [])
            if missing_deps:
                print(f"[KernelRegistry] Missing dependencies for '{name}': {missing_deps}")
                # Register anyway but mark as not ready
            
            info = ModuleInfo(
                name=name,
                module_type=module_type,
                instance=instance,
                version=version,
                dependencies=dependencies or [],
                provides=provides or [],
                metadata=metadata or {}
            )
            
            self._modules[name] = info
            self._namespaces["modules"][name] = instance
            
            # Auto-register provided services
            for service in (provides or []):
                self._services[service] = lambda i=instance: i
            
            print(f"[KernelRegistry] Registered module '{name}' ({module_type.name})")
            
            # Emit registration event
            self.kernel.message_bus.emit("module.registered", {
                "name": name,
                "type": module_type.name
            })
            
            return True
    
    def unregister_module(self, name: str) -> bool:
        """Unregister a module from the kernel."""
        with self._lock:
            if name not in self._modules:
                return False
            
            info = self._modules[name]
            
            # Remove provided services
            for service in info.provides:
                self._services.pop(service, None)
            
            del self._modules[name]
            self._namespaces["modules"].pop(name, None)
            
            print(f"[KernelRegistry] Unregistered module '{name}'")
            
            self.kernel.message_bus.emit("module.unregistered", {"name": name})
            
            return True
    
    def _check_dependencies(self, dependencies: List[str]) -> List[str]:
        """Check which dependencies are missing."""
        return [dep for dep in dependencies if dep not in self._modules]
    
    # =========================================================================
    # Module lookup
    # =========================================================================
    
    def get_module(self, name: str) -> Optional[Any]:
        """Get a module instance by name."""
        info = self._modules.get(name)
        return info.instance if info else None
    
    def get_module_info(self, name: str) -> Optional[ModuleInfo]:
        """Get module information by name."""
        return self._modules.get(name)
    
    def get_modules_by_type(self, module_type: ModuleType) -> List[ModuleInfo]:
        """Get all modules of a specific type."""
        return [
            info for info in self._modules.values()
            if info.module_type == module_type
        ]
    
    def get_all_modules(self) -> Dict[str, ModuleInfo]:
        """Get all registered modules."""
        return dict(self._modules)
    
    def has_module(self, name: str) -> bool:
        """Check if a module is registered."""
        return name in self._modules
    
    # =========================================================================
    # Service location
    # =========================================================================
    
    def register_service(self, name: str, provider: Callable) -> bool:
        """Register a service provider."""
        with self._lock:
            if name in self._services:
                print(f"[KernelRegistry] Service '{name}' already registered")
                return False
            
            self._services[name] = provider
            self._namespaces["services"][name] = provider
            print(f"[KernelRegistry] Registered service '{name}'")
            return True
    
    def get_service(self, name: str) -> Optional[Any]:
        """Get a service by name."""
        provider = self._services.get(name)
        if provider:
            return provider()
        return None
    
    def locate_capability(self, capability: str) -> List[Any]:
        """Find all modules that provide a capability."""
        return [
            info.instance for info in self._modules.values()
            if capability in info.provides
        ]
    
    # =========================================================================
    # Module state management
    # =========================================================================
    
    def set_module_state(self, name: str, state: ModuleState):
        """Update a module's state."""
        with self._lock:
            if name in self._modules:
                self._modules[name].state = state
                self.kernel.message_bus.emit("module.state_changed", {
                    "name": name,
                    "state": state.name
                })
    
    def get_modules_by_state(self, state: ModuleState) -> List[ModuleInfo]:
        """Get all modules in a specific state."""
        return [info for info in self._modules.values() if info.state == state]
    
    # =========================================================================
    # Namespace management
    # =========================================================================
    
    def create_namespace(self, name: str) -> bool:
        """Create a new namespace."""
        with self._lock:
            if name in self._namespaces:
                return False
            self._namespaces[name] = {}
            return True
    
    def set_in_namespace(self, namespace: str, key: str, value: Any):
        """Set a value in a namespace."""
        with self._lock:
            if namespace not in self._namespaces:
                self._namespaces[namespace] = {}
            self._namespaces[namespace][key] = value
    
    def get_from_namespace(self, namespace: str, key: str) -> Optional[Any]:
        """Get a value from a namespace."""
        ns = self._namespaces.get(namespace, {})
        return ns.get(key)
    
    def resolve_path(self, path: str) -> Optional[Any]:
        """
        Resolve a symbolic path like 'modules.unimind' or 'services.nlu'.
        """
        parts = path.split(".")
        if len(parts) < 2:
            return None
        
        namespace = parts[0]
        if namespace not in self._namespaces:
            return None
        
        current = self._namespaces[namespace]
        for part in parts[1:]:
            if isinstance(current, dict):
                current = current.get(part)
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return None
            
            if current is None:
                return None
        
        return current
    
    # =========================================================================
    # Statistics
    # =========================================================================
    
    def count(self) -> int:
        """Get total number of registered modules."""
        return len(self._modules)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        type_counts = {}
        state_counts = {}
        
        for info in self._modules.values():
            type_name = info.module_type.name
            state_name = info.state.name
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
            state_counts[state_name] = state_counts.get(state_name, 0) + 1
        
        return {
            "total_modules": len(self._modules),
            "total_services": len(self._services),
            "namespaces": list(self._namespaces.keys()),
            "by_type": type_counts,
            "by_state": state_counts
        }
