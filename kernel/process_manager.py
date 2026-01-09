# kernel/process_manager.py
"""
Process Manager - Module lifecycle and process management.

The process manager handles:
- Module initialization and teardown
- Process state transitions
- Thread management for modules
- Dependency-ordered startup/shutdown
"""

import threading
import time
from typing import Dict, Any, Optional, List, Callable
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime
import traceback


class ProcessState(Enum):
    """Process lifecycle states."""
    CREATED = auto()
    STARTING = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPING = auto()
    STOPPED = auto()
    CRASHED = auto()
    ZOMBIE = auto()


class ProcessPriority(Enum):
    """Process priority levels."""
    REALTIME = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    IDLE = 4


@dataclass
class ProcessInfo:
    """Information about a managed process."""
    pid: int
    name: str
    state: ProcessState = ProcessState.CREATED
    priority: ProcessPriority = ProcessPriority.NORMAL
    thread: Optional[threading.Thread] = None
    target: Optional[Callable] = None
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    restart_count: int = 0
    max_restarts: int = 3
    auto_restart: bool = False
    last_error: Optional[str] = None
    cpu_time: float = 0.0
    parent_pid: Optional[int] = None
    children: List[int] = field(default_factory=list)


class ProcessManager:
    """
    Manages module/process lifecycle in the kernel.
    
    Features:
    - Process creation and destruction
    - State machine for process lifecycle
    - Thread management
    - Auto-restart for crashed processes
    - Dependency-aware startup ordering
    """
    
    def __init__(self, kernel):
        """Initialize the process manager."""
        self.kernel = kernel
        self._processes: Dict[int, ProcessInfo] = {}
        self._pid_counter = 0
        self._lock = threading.RLock()
        self._shutdown_event = threading.Event()
        
        # Process groups
        self._groups: Dict[str, List[int]] = {
            "kernel": [],
            "daemon": [],
            "user": [],
            "background": []
        }
        
        print("[ProcessManager] Initialized")
    
    def _next_pid(self) -> int:
        """Generate the next process ID."""
        with self._lock:
            self._pid_counter += 1
            return self._pid_counter
    
    # =========================================================================
    # Process creation
    # =========================================================================
    
    def spawn(
        self,
        name: str,
        target: Callable,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        priority: ProcessPriority = ProcessPriority.NORMAL,
        group: str = "daemon",
        auto_restart: bool = False,
        max_restarts: int = 3,
        parent_pid: Optional[int] = None
    ) -> int:
        """
        Spawn a new process.
        
        Args:
            name: Process name
            target: Callable to run in the process
            args: Positional arguments for target
            kwargs: Keyword arguments for target
            priority: Process priority
            group: Process group name
            auto_restart: Whether to restart on crash
            max_restarts: Maximum restart attempts
            parent_pid: Parent process ID
        
        Returns:
            The new process ID
        """
        pid = self._next_pid()
        
        info = ProcessInfo(
            pid=pid,
            name=name,
            target=target,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            auto_restart=auto_restart,
            max_restarts=max_restarts,
            parent_pid=parent_pid
        )
        
        with self._lock:
            self._processes[pid] = info
            
            if group in self._groups:
                self._groups[group].append(pid)
            
            if parent_pid and parent_pid in self._processes:
                self._processes[parent_pid].children.append(pid)
        
        print(f"[ProcessManager] Spawned process '{name}' (PID: {pid})")
        self.kernel.message_bus.emit("process.spawned", {"pid": pid, "name": name})
        
        return pid
    
    def spawn_and_start(
        self,
        name: str,
        target: Callable,
        **kwargs
    ) -> int:
        """Spawn a process and immediately start it."""
        pid = self.spawn(name, target, **kwargs)
        self.start(pid)
        return pid
    
    # =========================================================================
    # Process lifecycle
    # =========================================================================
    
    def start(self, pid: int) -> bool:
        """Start a process."""
        with self._lock:
            if pid not in self._processes:
                return False
            
            info = self._processes[pid]
            
            if info.state not in (ProcessState.CREATED, ProcessState.STOPPED, ProcessState.CRASHED):
                return False
            
            info.state = ProcessState.STARTING
            
            # Create wrapper to handle exceptions
            def wrapped_target():
                try:
                    info.target(*info.args, **info.kwargs)
                except Exception as e:
                    info.last_error = traceback.format_exc()
                    self._handle_crash(pid)
                finally:
                    if info.state != ProcessState.CRASHED:
                        info.state = ProcessState.STOPPED
                        info.stopped_at = datetime.now()
            
            # Create and start thread
            thread = threading.Thread(
                target=wrapped_target,
                name=f"Process-{pid}-{info.name}",
                daemon=True
            )
            
            info.thread = thread
            info.started_at = datetime.now()
            thread.start()
            info.state = ProcessState.RUNNING
        
        print(f"[ProcessManager] Started process '{info.name}' (PID: {pid})")
        self.kernel.message_bus.emit("process.started", {"pid": pid, "name": info.name})
        
        return True
    
    def stop(self, pid: int, timeout: float = 5.0) -> bool:
        """Stop a process gracefully."""
        with self._lock:
            if pid not in self._processes:
                return False
            
            info = self._processes[pid]
            
            if info.state != ProcessState.RUNNING:
                return False
            
            info.state = ProcessState.STOPPING
        
        # Wait for thread to finish
        if info.thread and info.thread.is_alive():
            info.thread.join(timeout=timeout)
            
            if info.thread.is_alive():
                print(f"[ProcessManager] Warning: Process {pid} did not stop cleanly")
                info.state = ProcessState.ZOMBIE
            else:
                info.state = ProcessState.STOPPED
                info.stopped_at = datetime.now()
        
        print(f"[ProcessManager] Stopped process '{info.name}' (PID: {pid})")
        self.kernel.message_bus.emit("process.stopped", {"pid": pid, "name": info.name})
        
        return True
    
    def kill(self, pid: int) -> bool:
        """Forcefully terminate a process."""
        with self._lock:
            if pid not in self._processes:
                return False
            
            info = self._processes[pid]
            info.state = ProcessState.STOPPED
            info.stopped_at = datetime.now()
            
            # Kill children first
            for child_pid in info.children:
                self.kill(child_pid)
        
        print(f"[ProcessManager] Killed process '{info.name}' (PID: {pid})")
        self.kernel.message_bus.emit("process.killed", {"pid": pid, "name": info.name})
        
        return True
    
    def pause(self, pid: int) -> bool:
        """Pause a running process."""
        with self._lock:
            if pid not in self._processes:
                return False
            
            info = self._processes[pid]
            if info.state == ProcessState.RUNNING:
                info.state = ProcessState.PAUSED
                return True
        return False
    
    def resume(self, pid: int) -> bool:
        """Resume a paused process."""
        with self._lock:
            if pid not in self._processes:
                return False
            
            info = self._processes[pid]
            if info.state == ProcessState.PAUSED:
                info.state = ProcessState.RUNNING
                return True
        return False
    
    def restart(self, pid: int) -> bool:
        """Restart a process."""
        with self._lock:
            if pid not in self._processes:
                return False
            
            info = self._processes[pid]
            
            # Stop if running
            if info.state == ProcessState.RUNNING:
                self.stop(pid)
            
            # Increment restart counter
            info.restart_count += 1
            info.state = ProcessState.CREATED
        
        return self.start(pid)
    
    def _handle_crash(self, pid: int):
        """Handle a crashed process."""
        with self._lock:
            if pid not in self._processes:
                return
            
            info = self._processes[pid]
            info.state = ProcessState.CRASHED
            
            print(f"[ProcessManager] Process '{info.name}' (PID: {pid}) crashed")
            self.kernel.message_bus.emit("process.crashed", {
                "pid": pid,
                "name": info.name,
                "error": info.last_error
            })
            
            # Auto-restart if enabled
            if info.auto_restart and info.restart_count < info.max_restarts:
                print(f"[ProcessManager] Auto-restarting process {pid}")
                threading.Timer(1.0, lambda: self.restart(pid)).start()
    
    # =========================================================================
    # Process queries
    # =========================================================================
    
    def get_process(self, pid: int) -> Optional[ProcessInfo]:
        """Get process information by PID."""
        return self._processes.get(pid)
    
    def get_by_name(self, name: str) -> List[ProcessInfo]:
        """Get all processes with a given name."""
        return [p for p in self._processes.values() if p.name == name]
    
    def get_by_state(self, state: ProcessState) -> List[ProcessInfo]:
        """Get all processes in a given state."""
        return [p for p in self._processes.values() if p.state == state]
    
    def get_running(self) -> List[ProcessInfo]:
        """Get all running processes."""
        return self.get_by_state(ProcessState.RUNNING)
    
    def get_by_group(self, group: str) -> List[ProcessInfo]:
        """Get all processes in a group."""
        pids = self._groups.get(group, [])
        return [self._processes[pid] for pid in pids if pid in self._processes]
    
    def get_children(self, pid: int) -> List[ProcessInfo]:
        """Get child processes of a parent."""
        if pid not in self._processes:
            return []
        
        info = self._processes[pid]
        return [self._processes[cpid] for cpid in info.children if cpid in self._processes]
    
    def list_all(self) -> List[ProcessInfo]:
        """List all processes."""
        return list(self._processes.values())
    
    def count(self) -> int:
        """Get total process count."""
        return len(self._processes)
    
    # =========================================================================
    # Group management
    # =========================================================================
    
    def create_group(self, name: str) -> bool:
        """Create a new process group."""
        if name in self._groups:
            return False
        self._groups[name] = []
        return True
    
    def stop_group(self, group: str, timeout: float = 5.0) -> int:
        """Stop all processes in a group."""
        pids = self._groups.get(group, [])
        stopped = 0
        for pid in pids:
            if self.stop(pid, timeout):
                stopped += 1
        return stopped
    
    # =========================================================================
    # Cleanup
    # =========================================================================
    
    def stop_all(self, timeout: float = 5.0):
        """Stop all managed processes."""
        # Stop in reverse priority order (lowest first)
        by_priority = sorted(
            self._processes.items(),
            key=lambda x: x[1].priority.value,
            reverse=True
        )
        
        for pid, info in by_priority:
            if info.state == ProcessState.RUNNING:
                self.stop(pid, timeout)
        
        print("[ProcessManager] All processes stopped")
    
    def cleanup_zombies(self) -> int:
        """Clean up zombie processes."""
        zombies = self.get_by_state(ProcessState.ZOMBIE)
        for info in zombies:
            del self._processes[info.pid]
        return len(zombies)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get process manager statistics."""
        state_counts = {}
        for info in self._processes.values():
            state_name = info.state.name
            state_counts[state_name] = state_counts.get(state_name, 0) + 1
        
        return {
            "total_processes": len(self._processes),
            "pid_counter": self._pid_counter,
            "groups": {name: len(pids) for name, pids in self._groups.items()},
            "by_state": state_counts
        }
