# kernel/syscall_interface.py
"""
Syscall Interface - Standard interface for subsystem calls.

The syscall interface provides:
- Standardized API for subsystem operations
- Permission checking
- Call logging and auditing
- Cross-module operations
"""

import threading
import time
from typing import Dict, Any, Optional, List, Callable, Tuple, Set
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime
import traceback


class SyscallCategory(Enum):
    """Categories of system calls."""
    PROCESS = auto()      # Process management
    MEMORY = auto()       # Memory operations
    IO = auto()           # Input/output
    NETWORK = auto()      # Network operations
    SCHEDULE = auto()     # Scheduling
    REGISTRY = auto()     # Registry operations
    MESSAGE = auto()      # Messaging
    SENSOR = auto()       # Sensor access
    STORAGE = auto()      # Storage operations
    SECURITY = auto()     # Security operations


class SyscallResult(Enum):
    """Result codes for syscalls."""
    SUCCESS = 0
    ERROR = 1
    PERMISSION_DENIED = 2
    NOT_FOUND = 3
    INVALID_ARGS = 4
    TIMEOUT = 5
    NOT_IMPLEMENTED = 6


@dataclass
class SyscallInfo:
    """Information about a registered syscall."""
    name: str
    category: SyscallCategory
    handler: Callable
    description: str = ""
    requires_permission: Optional[str] = None
    arg_spec: Dict[str, type] = field(default_factory=dict)
    return_type: type = None
    deprecated: bool = False
    registered_at: datetime = field(default_factory=datetime.now)


@dataclass
class SyscallLogEntry:
    """Log entry for a syscall invocation."""
    id: str
    syscall: str
    caller: str
    args: tuple
    kwargs: Dict[str, Any]
    result: SyscallResult
    return_value: Any
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None


class SyscallInterface:
    """
    System call interface for the kernel.
    
    Provides a standardized way for modules to:
    - Request kernel services
    - Access other module capabilities
    - Perform privileged operations
    """
    
    def __init__(self, kernel):
        """Initialize the syscall interface."""
        self.kernel = kernel
        self._syscalls: Dict[str, SyscallInfo] = {}
        self._permissions: Dict[str, Set] = {}  # caller -> set of permissions
        self._call_log: List[SyscallLogEntry] = []
        self._lock = threading.RLock()
        self._log_limit = 1000
        
        # Statistics
        self._stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "permission_denials": 0
        }
        
        # Register built-in syscalls
        self._register_builtins()
        
        print("[SyscallInterface] Initialized")
    
    def _register_builtins(self):
        """Register built-in system calls."""
        # Process syscalls
        self.register(
            "process.spawn",
            SyscallCategory.PROCESS,
            self._sys_process_spawn,
            "Spawn a new process"
        )
        self.register(
            "process.kill",
            SyscallCategory.PROCESS,
            self._sys_process_kill,
            "Kill a process"
        )
        self.register(
            "process.list",
            SyscallCategory.PROCESS,
            self._sys_process_list,
            "List all processes"
        )
        
        # Memory syscalls
        self.register(
            "memory.store",
            SyscallCategory.MEMORY,
            self._sys_memory_store,
            "Store value in memory"
        )
        self.register(
            "memory.get",
            SyscallCategory.MEMORY,
            self._sys_memory_get,
            "Get value from memory"
        )
        self.register(
            "memory.delete",
            SyscallCategory.MEMORY,
            self._sys_memory_delete,
            "Delete value from memory"
        )
        
        # Registry syscalls
        self.register(
            "registry.get_module",
            SyscallCategory.REGISTRY,
            self._sys_registry_get_module,
            "Get a registered module"
        )
        self.register(
            "registry.list_modules",
            SyscallCategory.REGISTRY,
            self._sys_registry_list_modules,
            "List all modules"
        )
        
        # Message syscalls
        self.register(
            "message.emit",
            SyscallCategory.MESSAGE,
            self._sys_message_emit,
            "Emit a message"
        )
        self.register(
            "message.subscribe",
            SyscallCategory.MESSAGE,
            self._sys_message_subscribe,
            "Subscribe to messages"
        )
        
        # Schedule syscalls
        self.register(
            "schedule.task",
            SyscallCategory.SCHEDULE,
            self._sys_schedule_task,
            "Schedule a task"
        )
        self.register(
            "schedule.cancel",
            SyscallCategory.SCHEDULE,
            self._sys_schedule_cancel,
            "Cancel a scheduled task"
        )
        
        # Kernel syscalls
        self.register(
            "kernel.status",
            SyscallCategory.PROCESS,
            self._sys_kernel_status,
            "Get kernel status"
        )
        self.register(
            "kernel.uptime",
            SyscallCategory.PROCESS,
            self._sys_kernel_uptime,
            "Get kernel uptime"
        )
    
    # =========================================================================
    # Syscall registration
    # =========================================================================
    
    def register(
        self,
        name: str,
        category: SyscallCategory,
        handler: Callable,
        description: str = "",
        requires_permission: str = None,
        arg_spec: Dict[str, type] = None,
        return_type: type = None
    ) -> bool:
        """Register a new syscall."""
        with self._lock:
            if name in self._syscalls:
                print(f"[SyscallInterface] Syscall '{name}' already registered")
                return False
            
            self._syscalls[name] = SyscallInfo(
                name=name,
                category=category,
                handler=handler,
                description=description,
                requires_permission=requires_permission,
                arg_spec=arg_spec or {},
                return_type=return_type
            )
            
            return True
    
    def unregister(self, name: str) -> bool:
        """Unregister a syscall."""
        with self._lock:
            if name in self._syscalls:
                del self._syscalls[name]
                return True
            return False
    
    # =========================================================================
    # Syscall invocation
    # =========================================================================
    
    def invoke(
        self,
        name: str,
        *args,
        caller: str = "anonymous",
        **kwargs
    ) -> Tuple[SyscallResult, Any]:
        """
        Invoke a system call.
        
        Args:
            name: Syscall name
            *args: Positional arguments
            caller: Calling module name
            **kwargs: Keyword arguments
        
        Returns:
            Tuple of (result_code, return_value)
        """
        start_time = time.time()
        
        # Find syscall
        info = self._syscalls.get(name)
        if not info:
            self._stats["failed_calls"] += 1
            return (SyscallResult.NOT_FOUND, None)
        
        # Check permission
        if info.requires_permission:
            if not self._check_permission(caller, info.requires_permission):
                self._stats["permission_denials"] += 1
                return (SyscallResult.PERMISSION_DENIED, None)
        
        # Execute
        try:
            result = info.handler(*args, **kwargs)
            result_code = SyscallResult.SUCCESS
            error = None
            self._stats["successful_calls"] += 1
        except TypeError as e:
            result = None
            result_code = SyscallResult.INVALID_ARGS
            error = str(e)
            self._stats["failed_calls"] += 1
        except Exception as e:
            result = None
            result_code = SyscallResult.ERROR
            error = traceback.format_exc()
            self._stats["failed_calls"] += 1
        
        duration = (time.time() - start_time) * 1000
        self._stats["total_calls"] += 1
        
        # Log call
        self._log_call(
            name, caller, args, kwargs,
            result_code, result, duration, error
        )
        
        return (result_code, result)
    
    def call(self, name: str, *args, **kwargs) -> Any:
        """
        Simple syscall invocation (returns value or raises).
        """
        result_code, value = self.invoke(name, *args, **kwargs)
        
        if result_code == SyscallResult.SUCCESS:
            return value
        elif result_code == SyscallResult.NOT_FOUND:
            raise KeyError(f"Syscall not found: {name}")
        elif result_code == SyscallResult.PERMISSION_DENIED:
            raise PermissionError(f"Permission denied for: {name}")
        elif result_code == SyscallResult.INVALID_ARGS:
            raise TypeError(f"Invalid arguments for: {name}")
        else:
            raise RuntimeError(f"Syscall failed: {name}")
    
    def _check_permission(self, caller: str, permission: str) -> bool:
        """Check if a caller has a permission."""
        if caller == "kernel":
            return True
        
        caller_perms = self._permissions.get(caller, set())
        return permission in caller_perms or "*" in caller_perms
    
    def grant_permission(self, caller: str, permission: str):
        """Grant a permission to a caller."""
        with self._lock:
            if caller not in self._permissions:
                self._permissions[caller] = set()
            self._permissions[caller].add(permission)
    
    def revoke_permission(self, caller: str, permission: str):
        """Revoke a permission from a caller."""
        with self._lock:
            if caller in self._permissions:
                self._permissions[caller].discard(permission)
    
    # =========================================================================
    # Logging
    # =========================================================================
    
    def _log_call(
        self,
        syscall: str,
        caller: str,
        args: tuple,
        kwargs: Dict,
        result: SyscallResult,
        return_value: Any,
        duration: float,
        error: Optional[str]
    ):
        """Log a syscall invocation."""
        import uuid
        
        entry = SyscallLogEntry(
            id=str(uuid.uuid4()),
            syscall=syscall,
            caller=caller,
            args=args,
            kwargs=kwargs,
            result=result,
            return_value=return_value,
            duration_ms=duration,
            error=error
        )
        
        with self._lock:
            self._call_log.append(entry)
            
            # Trim log if too large
            if len(self._call_log) > self._log_limit:
                self._call_log = self._call_log[-self._log_limit:]
    
    def get_call_log(self, limit: int = 100) -> List[SyscallLogEntry]:
        """Get recent syscall log entries."""
        return self._call_log[-limit:]
    
    # =========================================================================
    # Built-in syscall handlers
    # =========================================================================
    
    def _sys_process_spawn(self, name: str, target: Callable, **kwargs):
        """Spawn a process."""
        return self.kernel.process_manager.spawn(name, target, **kwargs)
    
    def _sys_process_kill(self, pid: int):
        """Kill a process."""
        return self.kernel.process_manager.kill(pid)
    
    def _sys_process_list(self):
        """List processes."""
        return [
            {"pid": p.pid, "name": p.name, "state": p.state.name}
            for p in self.kernel.process_manager.list_all()
        ]
    
    def _sys_memory_store(self, key: str, value: Any, **kwargs):
        """Store in memory."""
        return self.kernel.memory_manager.store(key, value, **kwargs)
    
    def _sys_memory_get(self, key: str, namespace: str = "global"):
        """Get from memory."""
        return self.kernel.memory_manager.get(key, namespace)
    
    def _sys_memory_delete(self, key: str, namespace: str = "global"):
        """Delete from memory."""
        return self.kernel.memory_manager.delete(key, namespace)
    
    def _sys_registry_get_module(self, name: str):
        """Get a module."""
        return self.kernel.registry.get_module(name)
    
    def _sys_registry_list_modules(self):
        """List modules."""
        return list(self.kernel.registry.get_all_modules().keys())
    
    def _sys_message_emit(self, topic: str, data: Any = None, **kwargs):
        """Emit a message."""
        return self.kernel.message_bus.emit(topic, data, **kwargs)
    
    def _sys_message_subscribe(self, pattern: str, handler: Callable, **kwargs):
        """Subscribe to messages."""
        return self.kernel.message_bus.subscribe(pattern, handler, **kwargs)
    
    def _sys_schedule_task(self, callback: Callable, **kwargs):
        """Schedule a task."""
        return self.kernel.scheduler.schedule(callback, **kwargs)
    
    def _sys_schedule_cancel(self, task_id: str):
        """Cancel a task."""
        return self.kernel.scheduler.cancel(task_id)
    
    def _sys_kernel_status(self):
        """Get kernel status."""
        return self.kernel.get_status()
    
    def _sys_kernel_uptime(self):
        """Get kernel uptime."""
        return self.kernel.get_uptime()
    
    # =========================================================================
    # Introspection
    # =========================================================================
    
    def list_syscalls(self, category: SyscallCategory = None) -> List[str]:
        """List available syscalls."""
        if category:
            return [
                name for name, info in self._syscalls.items()
                if info.category == category
            ]
        return list(self._syscalls.keys())
    
    def get_syscall_info(self, name: str) -> Optional[SyscallInfo]:
        """Get information about a syscall."""
        return self._syscalls.get(name)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get syscall statistics."""
        return {
            **self._stats,
            "registered_syscalls": len(self._syscalls),
            "log_entries": len(self._call_log)
        }
