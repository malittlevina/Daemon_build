# kernel/kernel_core.py
"""
ThothOS Kernel Core - The central nervous system of the daemon.

The Kernel orchestrates all subsystems, manages the main execution loop,
and provides the foundational infrastructure for the symbolic OS.
"""

import threading
import time
import signal
import os
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from enum import Enum, auto


class KernelState(Enum):
    """Kernel operational states."""
    INITIALIZING = auto()
    BOOTING = auto()
    RUNNING = auto()
    PAUSED = auto()
    SHUTTING_DOWN = auto()
    HALTED = auto()


class KernelPriority(Enum):
    """Priority levels for kernel operations."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class Kernel:
    """
    ThothOS Kernel - The symbolic operating system core.
    
    Responsibilities:
    - Bootstrap all subsystems in correct order
    - Manage the main execution loop
    - Coordinate inter-module communication
    - Handle system-wide events and signals
    - Provide resource allocation and scheduling
    """
    
    _instance: Optional['Kernel'] = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern - only one kernel instance allowed."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: str = "config/daemon_config.json"):
        """Initialize the kernel with configuration."""
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self._initialized = True
        self.config_path = config_path
        self.state = KernelState.INITIALIZING
        self.boot_time: Optional[datetime] = None
        self.uptime_start: Optional[float] = None
        
        # Core kernel subsystems (lazy loaded)
        self._registry = None
        self._message_bus = None
        self._process_manager = None
        self._scheduler = None
        self._memory_manager = None
        self._syscall = None
        self._interrupt_handler = None
        
        # Kernel threads
        self._threads: Dict[str, threading.Thread] = {}
        self._shutdown_event = threading.Event()
        
        # Hooks for extension
        self._boot_hooks: list = []
        self._shutdown_hooks: list = []
        self._tick_hooks: list = []
        
        # Kernel tick rate (Hz)
        self.tick_rate = 10  # 10 ticks per second
        self._tick_count = 0
        
        print("[Kernel] Core initialized in INITIALIZING state")
    
    @classmethod
    def get_instance(cls) -> 'Kernel':
        """Get the singleton kernel instance."""
        if cls._instance is None:
            cls._instance = Kernel()
        return cls._instance
    
    # =========================================================================
    # Lazy-loaded subsystem accessors
    # =========================================================================
    
    @property
    def registry(self):
        """Get the kernel registry (lazy loaded)."""
        if self._registry is None:
            from kernel.kernel_registry import KernelRegistry
            self._registry = KernelRegistry(self)
        return self._registry
    
    @property
    def message_bus(self):
        """Get the message bus (lazy loaded)."""
        if self._message_bus is None:
            from kernel.message_bus import MessageBus
            self._message_bus = MessageBus(self)
        return self._message_bus
    
    @property
    def process_manager(self):
        """Get the process manager (lazy loaded)."""
        if self._process_manager is None:
            from kernel.process_manager import ProcessManager
            self._process_manager = ProcessManager(self)
        return self._process_manager
    
    @property
    def scheduler(self):
        """Get the scheduler (lazy loaded)."""
        if self._scheduler is None:
            from kernel.scheduler import Scheduler
            self._scheduler = Scheduler(self)
        return self._scheduler
    
    @property
    def memory_manager(self):
        """Get the memory manager (lazy loaded)."""
        if self._memory_manager is None:
            from kernel.memory_manager import MemoryManager
            self._memory_manager = MemoryManager(self)
        return self._memory_manager
    
    @property
    def syscall(self):
        """Get the syscall interface (lazy loaded)."""
        if self._syscall is None:
            from kernel.syscall_interface import SyscallInterface
            self._syscall = SyscallInterface(self)
        return self._syscall
    
    @property
    def interrupt_handler(self):
        """Get the interrupt handler (lazy loaded)."""
        if self._interrupt_handler is None:
            from kernel.interrupt_handler import InterruptHandler
            self._interrupt_handler = InterruptHandler(self)
        return self._interrupt_handler
    
    # =========================================================================
    # Boot sequence
    # =========================================================================
    
    def boot(self) -> bool:
        """
        Boot the kernel and all subsystems.
        
        Boot sequence:
        1. Load configuration
        2. Initialize kernel subsystems
        3. Register signal handlers
        4. Start scheduler
        5. Load daemon modules
        6. Execute boot hooks
        7. Enter running state
        """
        self.state = KernelState.BOOTING
        self.boot_time = datetime.now()
        self.uptime_start = time.time()
        
        print(f"[Kernel] Boot sequence started at {self.boot_time.isoformat()}")
        
        try:
            # Step 1: Load configuration
            self._load_config()
            print("[Kernel] Configuration loaded")
            
            # Step 2: Initialize core subsystems
            _ = self.registry
            _ = self.message_bus
            _ = self.process_manager
            _ = self.scheduler
            _ = self.memory_manager
            _ = self.syscall
            _ = self.interrupt_handler
            print("[Kernel] Core subsystems initialized")
            
            # Step 3: Register signal handlers
            self._register_signal_handlers()
            print("[Kernel] Signal handlers registered")
            
            # Step 4: Start the scheduler
            self.scheduler.start()
            print("[Kernel] Scheduler started")
            
            # Step 5: Start interrupt handler
            self.interrupt_handler.start()
            print("[Kernel] Interrupt handler started")
            
            # Step 6: Execute boot hooks
            for hook in self._boot_hooks:
                try:
                    hook(self)
                except Exception as e:
                    print(f"[Kernel] Boot hook error: {e}")
            
            # Step 7: Enter running state
            self.state = KernelState.RUNNING
            print("[Kernel] Boot complete - entering RUNNING state")
            
            return True
            
        except Exception as e:
            print(f"[Kernel] Boot failed: {e}")
            self.state = KernelState.HALTED
            return False
    
    def _load_config(self):
        """Load kernel configuration from file."""
        import json
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "auto_optimization": True,
                "modules_to_load": []
            }
    
    def _register_signal_handlers(self):
        """Register OS signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            print(f"\n[Kernel] Received signal {signum}, initiating shutdown...")
            self.shutdown()
        
        # Only register if we're in the main thread
        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
    
    # =========================================================================
    # Main loop
    # =========================================================================
    
    def run(self, blocking: bool = True):
        """
        Run the kernel main loop.
        
        Args:
            blocking: If True, blocks until shutdown. If False, runs in thread.
        """
        if self.state != KernelState.RUNNING:
            if not self.boot():
                raise RuntimeError("Kernel boot failed")
        
        if blocking:
            self._main_loop()
        else:
            thread = threading.Thread(target=self._main_loop, name="KernelMainLoop")
            thread.daemon = True
            thread.start()
            self._threads["main_loop"] = thread
    
    def _main_loop(self):
        """The kernel's main execution loop."""
        tick_interval = 1.0 / self.tick_rate
        
        while self.state == KernelState.RUNNING:
            tick_start = time.time()
            
            try:
                # Process scheduled tasks
                self.scheduler.tick()
                
                # Process message queue
                self.message_bus.process_queue()
                
                # Process interrupts
                self.interrupt_handler.process_pending()
                
                # Execute tick hooks
                for hook in self._tick_hooks:
                    try:
                        hook(self, self._tick_count)
                    except Exception as e:
                        print(f"[Kernel] Tick hook error: {e}")
                
                self._tick_count += 1
                
            except Exception as e:
                print(f"[Kernel] Main loop error: {e}")
            
            # Sleep for remaining tick time
            elapsed = time.time() - tick_start
            sleep_time = max(0, tick_interval - elapsed)
            if sleep_time > 0:
                self._shutdown_event.wait(timeout=sleep_time)
        
        print("[Kernel] Main loop exited")
    
    # =========================================================================
    # Shutdown sequence
    # =========================================================================
    
    def shutdown(self, force: bool = False):
        """
        Gracefully shutdown the kernel.
        
        Args:
            force: If True, skip graceful shutdown procedures.
        """
        if self.state in (KernelState.SHUTTING_DOWN, KernelState.HALTED):
            return
        
        self.state = KernelState.SHUTTING_DOWN
        print("[Kernel] Initiating shutdown sequence...")
        
        # Signal all threads to stop
        self._shutdown_event.set()
        
        if not force:
            # Execute shutdown hooks
            for hook in reversed(self._shutdown_hooks):
                try:
                    hook(self)
                except Exception as e:
                    print(f"[Kernel] Shutdown hook error: {e}")
            
            # Stop subsystems in reverse order
            if self._interrupt_handler:
                self._interrupt_handler.stop()
            if self._scheduler:
                self._scheduler.stop()
            
            # Stop all registered processes
            if self._process_manager:
                self._process_manager.stop_all()
        
        # Wait for threads to finish
        for name, thread in self._threads.items():
            if thread.is_alive():
                thread.join(timeout=2.0)
                if thread.is_alive():
                    print(f"[Kernel] Warning: Thread {name} did not stop cleanly")
        
        uptime = time.time() - self.uptime_start if self.uptime_start else 0
        print(f"[Kernel] Shutdown complete. Uptime: {uptime:.2f}s")
        self.state = KernelState.HALTED
    
    # =========================================================================
    # Hook registration
    # =========================================================================
    
    def register_boot_hook(self, hook: Callable[['Kernel'], None]):
        """Register a hook to be called during boot."""
        self._boot_hooks.append(hook)
    
    def register_shutdown_hook(self, hook: Callable[['Kernel'], None]):
        """Register a hook to be called during shutdown."""
        self._shutdown_hooks.append(hook)
    
    def register_tick_hook(self, hook: Callable[['Kernel', int], None]):
        """Register a hook to be called on each kernel tick."""
        self._tick_hooks.append(hook)
    
    # =========================================================================
    # State and info
    # =========================================================================
    
    def pause(self):
        """Pause kernel execution."""
        if self.state == KernelState.RUNNING:
            self.state = KernelState.PAUSED
            print("[Kernel] Paused")
    
    def resume(self):
        """Resume kernel execution."""
        if self.state == KernelState.PAUSED:
            self.state = KernelState.RUNNING
            print("[Kernel] Resumed")
    
    def get_uptime(self) -> float:
        """Get kernel uptime in seconds."""
        if self.uptime_start:
            return time.time() - self.uptime_start
        return 0.0
    
    def get_status(self) -> Dict[str, Any]:
        """Get current kernel status."""
        return {
            "state": self.state.name,
            "uptime": self.get_uptime(),
            "boot_time": self.boot_time.isoformat() if self.boot_time else None,
            "tick_count": self._tick_count,
            "tick_rate": self.tick_rate,
            "active_processes": self.process_manager.count() if self._process_manager else 0,
            "scheduled_tasks": self.scheduler.pending_count() if self._scheduler else 0,
            "message_queue_size": self.message_bus.queue_size() if self._message_bus else 0
        }
    
    def emit(self, event: str, data: Any = None, priority: KernelPriority = KernelPriority.NORMAL):
        """Emit an event through the message bus."""
        self.message_bus.emit(event, data, priority)
    
    def syscall_invoke(self, call_name: str, *args, **kwargs) -> Any:
        """Invoke a system call."""
        return self.syscall.invoke(call_name, *args, **kwargs)
