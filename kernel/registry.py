# kernel/registry.py
"""
Module Registry - Manages kernel module lifecycle

All subsystems register with the kernel through this registry,
enabling discovery, dependency injection, and health monitoring.
"""

from typing import Dict, Any, Optional, List, Type, Protocol, runtime_checkable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading


class ModuleState(Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPING = "stopping"
    STOPPED = "stopped"


@runtime_checkable
class KernelModule(Protocol):
    """Protocol that all kernel modules should implement."""
    
    @property
    def module_name(self) -> str:
        """Unique identifier for this module."""
        ...
    
    @property
    def dependencies(self) -> List[str]:
        """List of module names this module depends on."""
        ...
    
    def initialize(self, kernel: Any) -> bool:
        """Initialize the module with kernel reference. Returns success."""
        ...
    
    def start(self) -> bool:
        """Start the module's operations. Returns success."""
        ...
    
    def stop(self) -> bool:
        """Stop the module's operations. Returns success."""
        ...
    
    def health_check(self) -> Dict[str, Any]:
        """Return health status and metrics."""
        ...


@dataclass
class ModuleInfo:
    """Metadata about a registered module."""
    name: str
    instance: Any
    state: ModuleState = ModuleState.UNINITIALIZED
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_health_check: Optional[datetime] = None
    health_status: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    last_error: Optional[str] = None


class ModuleRegistry:
    """
    Central registry for all kernel modules.
    
    Responsibilities:
    - Module registration and discovery
    - Dependency resolution
    - Lifecycle management (init, start, stop)
    - Health monitoring
    """
    
    def __init__(self):
        self._modules: Dict[str, ModuleInfo] = {}
        self._lock = threading.RLock()
        self._initialization_order: List[str] = []
        print("[ModuleRegistry] Initialized.")
    
    def register(self, module: Any, name: Optional[str] = None) -> bool:
        """
        Register a module with the kernel.
        
        Args:
            module: The module instance to register
            name: Optional override for module name
            
        Returns:
            True if registration successful
        """
        module_name = name or getattr(module, 'module_name', type(module).__name__)
        
        with self._lock:
            if module_name in self._modules:
                print(f"[ModuleRegistry] Warning: Module '{module_name}' already registered. Replacing.")
            
            self._modules[module_name] = ModuleInfo(
                name=module_name,
                instance=module,
                state=ModuleState.UNINITIALIZED
            )
            print(f"[ModuleRegistry] Registered module: {module_name}")
            return True
    
    def unregister(self, name: str) -> bool:
        """Remove a module from the registry."""
        with self._lock:
            if name in self._modules:
                info = self._modules[name]
                if info.state in (ModuleState.RUNNING, ModuleState.READY):
                    print(f"[ModuleRegistry] Warning: Unregistering active module '{name}'")
                del self._modules[name]
                if name in self._initialization_order:
                    self._initialization_order.remove(name)
                print(f"[ModuleRegistry] Unregistered module: {name}")
                return True
            return False
    
    def get(self, name: str) -> Optional[Any]:
        """Get a module instance by name."""
        with self._lock:
            info = self._modules.get(name)
            return info.instance if info else None
    
    def get_info(self, name: str) -> Optional[ModuleInfo]:
        """Get module info by name."""
        with self._lock:
            return self._modules.get(name)
    
    def list_modules(self) -> List[str]:
        """Get list of all registered module names."""
        with self._lock:
            return list(self._modules.keys())
    
    def get_all_info(self) -> Dict[str, ModuleInfo]:
        """Get info for all modules."""
        with self._lock:
            return dict(self._modules)
    
    def resolve_dependencies(self) -> List[str]:
        """
        Resolve module dependencies and return initialization order.
        Uses topological sort to ensure dependencies are initialized first.
        """
        with self._lock:
            # Build dependency graph
            graph: Dict[str, List[str]] = {}
            for name, info in self._modules.items():
                deps = getattr(info.instance, 'dependencies', [])
                graph[name] = deps if isinstance(deps, list) else []
            
            # Topological sort
            visited = set()
            order = []
            
            def visit(name: str, path: set):
                if name in path:
                    raise ValueError(f"Circular dependency detected: {name}")
                if name in visited:
                    return
                
                path.add(name)
                for dep in graph.get(name, []):
                    if dep in graph:  # Only visit registered modules
                        visit(dep, path)
                path.remove(name)
                
                visited.add(name)
                order.append(name)
            
            for name in graph:
                visit(name, set())
            
            self._initialization_order = order
            return order
    
    def initialize_all(self, kernel: Any) -> Dict[str, bool]:
        """
        Initialize all modules in dependency order.
        
        Returns:
            Dict mapping module names to success status
        """
        results = {}
        order = self.resolve_dependencies()
        
        for name in order:
            with self._lock:
                info = self._modules.get(name)
                if not info:
                    continue
                
                info.state = ModuleState.INITIALIZING
            
            try:
                if hasattr(info.instance, 'initialize'):
                    success = info.instance.initialize(kernel)
                else:
                    success = True  # Module doesn't need initialization
                
                with self._lock:
                    info.state = ModuleState.READY if success else ModuleState.ERROR
                    if not success:
                        info.error_count += 1
                        info.last_error = "Initialization failed"
                
                results[name] = success
                print(f"[ModuleRegistry] Initialized '{name}': {'OK' if success else 'FAILED'}")
                
            except Exception as e:
                with self._lock:
                    info.state = ModuleState.ERROR
                    info.error_count += 1
                    info.last_error = str(e)
                results[name] = False
                print(f"[ModuleRegistry] Error initializing '{name}': {e}")
        
        return results
    
    def start_all(self) -> Dict[str, bool]:
        """Start all ready modules."""
        results = {}
        
        for name in self._initialization_order:
            with self._lock:
                info = self._modules.get(name)
                if not info or info.state != ModuleState.READY:
                    continue
            
            try:
                if hasattr(info.instance, 'start'):
                    success = info.instance.start()
                else:
                    success = True
                
                with self._lock:
                    info.state = ModuleState.RUNNING if success else ModuleState.ERROR
                
                results[name] = success
                
            except Exception as e:
                with self._lock:
                    info.state = ModuleState.ERROR
                    info.error_count += 1
                    info.last_error = str(e)
                results[name] = False
                print(f"[ModuleRegistry] Error starting '{name}': {e}")
        
        return results
    
    def stop_all(self) -> Dict[str, bool]:
        """Stop all running modules in reverse order."""
        results = {}
        
        # Stop in reverse initialization order
        for name in reversed(self._initialization_order):
            with self._lock:
                info = self._modules.get(name)
                if not info or info.state not in (ModuleState.RUNNING, ModuleState.READY):
                    continue
                info.state = ModuleState.STOPPING
            
            try:
                if hasattr(info.instance, 'stop'):
                    success = info.instance.stop()
                else:
                    success = True
                
                with self._lock:
                    info.state = ModuleState.STOPPED if success else ModuleState.ERROR
                results[name] = success
                
            except Exception as e:
                with self._lock:
                    info.state = ModuleState.ERROR
                results[name] = False
                print(f"[ModuleRegistry] Error stopping '{name}': {e}")
        
        return results
    
    def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Run health checks on all modules."""
        results = {}
        
        for name, info in self._modules.items():
            try:
                if hasattr(info.instance, 'health_check'):
                    health = info.instance.health_check()
                else:
                    health = {"status": "unknown", "message": "No health check implemented"}
                
                with self._lock:
                    info.last_health_check = datetime.utcnow()
                    info.health_status = health
                
                results[name] = health
                
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
        
        return results
    
    def set_state(self, name: str, state: ModuleState):
        """Manually set a module's state."""
        with self._lock:
            if name in self._modules:
                self._modules[name].state = state
