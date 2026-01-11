# kernel/kernel_core.py
"""
ThothKernel - The Central Orchestrator

This is the heart of ThothOS, coordinating all subsystems through:
- Unified state management
- Inter-module communication
- Resource orchestration
- Self-monitoring and healing
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import threading
import time

from kernel.message_bus import MessageBus, KernelMessage, MessagePriority
from kernel.scheduler import KernelScheduler, TaskPriority
from kernel.registry import ModuleRegistry, ModuleState


class KernelState(Enum):
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    DEGRADED = "degraded"  # Some modules failed
    PAUSED = "paused"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"


class ThothKernel:
    """
    The central kernel of ThothOS.
    
    Responsibilities:
    - Bootstrap and manage all subsystem modules
    - Provide unified state access
    - Route messages between modules
    - Schedule and coordinate tasks
    - Monitor system health
    - Enable self-reflection and optimization
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern - only one kernel instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: Dict[str, Any] = None):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self._initialized = True
        self.config = config or {}
        self.state = KernelState.INITIALIZING
        self.boot_time: Optional[datetime] = None
        
        # Core subsystems
        self.message_bus = MessageBus()
        self.scheduler = KernelScheduler(max_workers=self.config.get('max_workers', 4))
        self.registry = ModuleRegistry()
        
        # Global state accessible to all modules
        self._global_state: Dict[str, Any] = {
            "context": {},       # Current conversation/task context
            "memory": {},        # Short-term working memory
            "flags": {},         # System flags
            "metrics": {},       # Performance metrics
            "user_profile": {},  # User preferences and history
        }
        self._state_lock = threading.RLock()
        
        # Internal message subscriptions
        self._setup_internal_subscriptions()
        
        print("[ThothKernel] Core initialized.")
    
    def _setup_internal_subscriptions(self):
        """Subscribe to system-level messages."""
        self.message_bus.subscribe("kernel.shutdown", self._handle_shutdown)
        self.message_bus.subscribe("kernel.pause", self._handle_pause)
        self.message_bus.subscribe("kernel.resume", self._handle_resume)
        self.message_bus.subscribe("kernel.health_check", self._handle_health_check)
        self.message_bus.subscribe_pattern("error.*", self._handle_error)
        self.message_bus.subscribe_pattern("state.*", self._handle_state_update)
    
    def boot(self) -> bool:
        """
        Boot the kernel and all registered modules.
        
        Returns:
            True if boot successful
        """
        print("[ThothKernel] Booting...")
        self.boot_time = datetime.utcnow()
        
        try:
            # Start core services
            self.message_bus.start()
            self.scheduler.start()
            
            # Initialize all registered modules
            init_results = self.registry.initialize_all(self)
            failed_modules = [name for name, success in init_results.items() if not success]
            
            if failed_modules:
                print(f"[ThothKernel] Warning: Failed to initialize modules: {failed_modules}")
                self.state = KernelState.DEGRADED
            else:
                self.state = KernelState.READY
            
            # Start all modules
            start_results = self.registry.start_all()
            
            # Schedule health monitoring
            self.scheduler.schedule(
                self._run_health_check,
                name="kernel_health_monitor",
                priority=TaskPriority.LOW,
                interval_seconds=60,  # Check every minute
                source_module="kernel"
            )
            
            self.state = KernelState.RUNNING
            
            # Broadcast boot complete
            self.message_bus.publish_sync(
                "kernel.booted",
                {"boot_time": self.boot_time.isoformat(), "state": self.state.value},
                "kernel"
            )
            
            print(f"[ThothKernel] Boot complete. State: {self.state.value}")
            return True
            
        except Exception as e:
            print(f"[ThothKernel] Boot failed: {e}")
            self.state = KernelState.DEGRADED
            return False
    
    def shutdown(self):
        """Gracefully shutdown the kernel."""
        print("[ThothKernel] Initiating shutdown...")
        self.state = KernelState.SHUTTING_DOWN
        
        # Broadcast shutdown signal
        self.message_bus.publish_sync(
            "kernel.shutting_down",
            {"timestamp": datetime.utcnow().isoformat()},
            "kernel",
            priority=MessagePriority.CRITICAL
        )
        
        # Stop all modules
        self.registry.stop_all()
        
        # Stop core services
        self.scheduler.stop()
        self.message_bus.stop()
        
        self.state = KernelState.STOPPED
        print("[ThothKernel] Shutdown complete.")
    
    # =========== State Management ===========
    
    def get_state(self, path: str = None) -> Any:
        """
        Get global state or a specific path.
        
        Args:
            path: Dot-separated path (e.g., 'context.current_task')
            
        Returns:
            State value or entire state dict
        """
        with self._state_lock:
            if path is None:
                return dict(self._global_state)
            
            parts = path.split('.')
            value = self._global_state
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            return value
    
    def set_state(self, path: str, value: Any, broadcast: bool = True):
        """
        Set a value in global state.
        
        Args:
            path: Dot-separated path
            value: Value to set
            broadcast: Whether to broadcast state change
        """
        with self._state_lock:
            parts = path.split('.')
            target = self._global_state
            
            for part in parts[:-1]:
                if part not in target:
                    target[part] = {}
                target = target[part]
            
            target[parts[-1]] = value
        
        if broadcast:
            self.message_bus.publish_sync(
                f"state.{path}",
                {"path": path, "value": value},
                "kernel"
            )
    
    def update_state(self, updates: Dict[str, Any], broadcast: bool = True):
        """Update multiple state values at once."""
        for path, value in updates.items():
            self.set_state(path, value, broadcast=False)
        
        if broadcast:
            self.message_bus.publish_sync(
                "state.bulk_update",
                {"updates": updates},
                "kernel"
            )
    
    # =========== Module Access ===========
    
    def register_module(self, module: Any, name: str = None) -> bool:
        """Register a module with the kernel."""
        return self.registry.register(module, name)
    
    def get_module(self, name: str) -> Optional[Any]:
        """Get a registered module by name."""
        return self.registry.get(name)
    
    def invoke_module(self, module_name: str, method: str, *args, **kwargs) -> Any:
        """
        Invoke a method on a registered module.
        
        This provides a unified way to call module methods with
        automatic error handling and logging.
        """
        module = self.registry.get(module_name)
        if not module:
            raise ValueError(f"Module not found: {module_name}")
        
        if not hasattr(module, method):
            raise AttributeError(f"Module '{module_name}' has no method '{method}'")
        
        try:
            return getattr(module, method)(*args, **kwargs)
        except Exception as e:
            self.message_bus.publish_sync(
                f"error.{module_name}",
                {"method": method, "error": str(e)},
                "kernel",
                priority=MessagePriority.HIGH
            )
            raise
    
    # =========== Task Scheduling ===========
    
    def schedule_task(
        self,
        callback: Callable,
        name: str = "task",
        priority: TaskPriority = TaskPriority.NORMAL,
        delay_seconds: float = 0,
        interval_seconds: float = None,
        source_module: str = None,
        **kwargs
    ) -> str:
        """Schedule a task through the kernel scheduler."""
        return self.scheduler.schedule(
            callback,
            name=name,
            priority=priority,
            delay_seconds=delay_seconds,
            interval_seconds=interval_seconds,
            source_module=source_module,
            kwargs=kwargs
        )
    
    # =========== Message Passing ===========
    
    def publish(self, topic: str, payload: Any, source: str = "unknown",
                priority: MessagePriority = MessagePriority.NORMAL) -> str:
        """Publish a message to the kernel message bus."""
        return self.message_bus.publish_sync(topic, payload, source, priority)
    
    def subscribe(self, topic: str, callback: Callable):
        """Subscribe to a message topic."""
        self.message_bus.subscribe(topic, callback)
    
    def request(self, topic: str, payload: Any, timeout_ms: int = 5000) -> Optional[Any]:
        """Send a request and wait for response."""
        message = KernelMessage(topic=topic, payload=payload, source="kernel")
        return self.message_bus.request(message, timeout_ms)
    
    # =========== Health & Monitoring ===========
    
    def _run_health_check(self):
        """Periodic health check of all modules."""
        health = self.registry.health_check_all()
        
        # Update metrics
        healthy_count = sum(1 for h in health.values() if h.get('status') == 'healthy')
        total_count = len(health)
        
        self.set_state('metrics.health', {
            'healthy_modules': healthy_count,
            'total_modules': total_count,
            'last_check': datetime.utcnow().isoformat()
        }, broadcast=False)
        
        # Check for degraded state
        if healthy_count < total_count:
            if self.state == KernelState.RUNNING:
                self.state = KernelState.DEGRADED
                self.message_bus.publish_sync(
                    "kernel.degraded",
                    {"unhealthy_count": total_count - healthy_count},
                    "kernel",
                    priority=MessagePriority.HIGH
                )
        elif self.state == KernelState.DEGRADED:
            self.state = KernelState.RUNNING
            self.message_bus.publish_sync("kernel.recovered", {}, "kernel")
        
        return health
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive kernel status."""
        uptime = None
        if self.boot_time:
            uptime = (datetime.utcnow() - self.boot_time).total_seconds()
        
        return {
            "state": self.state.value,
            "boot_time": self.boot_time.isoformat() if self.boot_time else None,
            "uptime_seconds": uptime,
            "modules": {
                name: {
                    "state": info.state.value,
                    "error_count": info.error_count
                }
                for name, info in self.registry.get_all_info().items()
            },
            "message_bus": self.message_bus.get_stats(),
            "scheduler": self.scheduler.get_stats(),
            "global_state_keys": list(self._global_state.keys())
        }
    
    # =========== Internal Handlers ===========
    
    def _handle_shutdown(self, message: KernelMessage):
        """Handle shutdown request."""
        self.shutdown()
    
    def _handle_pause(self, message: KernelMessage):
        """Handle pause request."""
        if self.state == KernelState.RUNNING:
            self.state = KernelState.PAUSED
            print("[ThothKernel] Paused.")
    
    def _handle_resume(self, message: KernelMessage):
        """Handle resume request."""
        if self.state == KernelState.PAUSED:
            self.state = KernelState.RUNNING
            print("[ThothKernel] Resumed.")
    
    def _handle_health_check(self, message: KernelMessage):
        """Handle health check request."""
        health = self._run_health_check()
        self.message_bus.respond(message.message_id, health)
    
    def _handle_error(self, message: KernelMessage):
        """Handle error events from modules."""
        # Log errors for later analysis
        errors = self.get_state('metrics.errors') or []
        errors.append({
            "topic": message.topic,
            "payload": message.payload,
            "timestamp": message.timestamp.isoformat(),
            "source": message.source
        })
        # Keep last 100 errors
        self.set_state('metrics.errors', errors[-100:], broadcast=False)
    
    def _handle_state_update(self, message: KernelMessage):
        """Handle state update broadcasts."""
        # Could trigger reactions to state changes
        pass
    
    # =========== Reflection API ===========
    
    def reflect(self) -> Dict[str, Any]:
        """
        Trigger a system-wide reflection.
        
        This asks all modules to report their state and 
        generates a summary for self-analysis.
        """
        reflection = {
            "timestamp": datetime.utcnow().isoformat(),
            "kernel_state": self.state.value,
            "modules": {},
            "insights": [],
            "recommendations": []
        }
        
        # Gather module reflections
        for name in self.registry.list_modules():
            module = self.registry.get(name)
            if hasattr(module, 'reflect'):
                try:
                    reflection["modules"][name] = module.reflect()
                except Exception as e:
                    reflection["modules"][name] = {"error": str(e)}
        
        # Analyze patterns
        error_count = len(self.get_state('metrics.errors') or [])
        if error_count > 10:
            reflection["insights"].append(f"High error count detected: {error_count}")
            reflection["recommendations"].append("Consider reviewing error logs for patterns")
        
        # Check message bus health
        bus_stats = self.message_bus.get_stats()
        if bus_stats['dead_letters'] > 5:
            reflection["insights"].append(f"Dead letters accumulating: {bus_stats['dead_letters']}")
            reflection["recommendations"].append("Review failed message handlers")
        
        return reflection


# Convenience function to get the kernel instance
def get_kernel() -> ThothKernel:
    """Get the singleton kernel instance."""
    return ThothKernel()
