# kernel/interrupt_handler.py
"""
Interrupt Handler - Async event and signal handling.

The interrupt handler provides:
- Hardware-like interrupt system for the symbolic OS
- Priority-based interrupt handling
- Interrupt chaining and nesting
- Async event processing
- Signal routing
"""

import threading
import queue
import time
from typing import Dict, Any, Optional, List, Callable, Set
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class InterruptType(Enum):
    """Types of interrupts in the system."""
    TIMER = auto()          # Timer interrupts
    IO = auto()             # I/O completion
    SENSOR = auto()         # Sensor input
    USER = auto()           # User input
    SYSTEM = auto()         # System events
    ERROR = auto()          # Error conditions
    SIGNAL = auto()         # Control signals
    IPC = auto()            # Inter-process communication
    CUSTOM = auto()         # Custom interrupts


class InterruptPriority(Enum):
    """Interrupt priority levels."""
    NMI = 0         # Non-maskable (always handled)
    CRITICAL = 1    # Critical system interrupts
    HIGH = 2        # High priority
    NORMAL = 3      # Normal priority
    LOW = 4         # Low priority
    DEFERRED = 5    # Deferred handling


@dataclass
class Interrupt:
    """An interrupt in the system."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: InterruptType = InterruptType.SYSTEM
    priority: InterruptPriority = InterruptPriority.NORMAL
    source: str = "kernel"
    vector: int = 0  # Interrupt vector number
    data: Any = None
    timestamp: float = field(default_factory=time.time)
    handled: bool = False
    deferred: bool = False
    chain_next: Optional['Interrupt'] = None


@dataclass
class InterruptHandler:
    """A registered interrupt handler."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    vector: int = 0
    handler: Callable[[Interrupt], bool] = None
    priority: InterruptPriority = InterruptPriority.NORMAL
    owner: str = "kernel"
    enabled: bool = True
    call_count: int = 0
    mask: Set[int] = field(default_factory=set)  # Vectors to mask during handling


class InterruptController:
    """
    Interrupt controller for the kernel.
    
    Features:
    - Vector-based interrupt routing
    - Priority handling
    - Interrupt masking
    - Deferred interrupt processing
    - Interrupt statistics
    """
    
    # Standard interrupt vectors
    VECTOR_TIMER = 0
    VECTOR_KEYBOARD = 1
    VECTOR_MOUSE = 2
    VECTOR_NETWORK = 3
    VECTOR_DISK = 4
    VECTOR_AUDIO = 5
    VECTOR_VIDEO = 6
    VECTOR_SENSOR = 7
    VECTOR_IPC = 8
    VECTOR_SYSCALL = 9
    VECTOR_ERROR = 10
    VECTOR_SIGNAL = 11
    
    # Custom vectors start at 32
    VECTOR_CUSTOM_BASE = 32
    
    def __init__(self, kernel):
        """Initialize the interrupt controller."""
        self.kernel = kernel
        
        # Interrupt queue (priority queue)
        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        
        # Deferred interrupt queue
        self._deferred: List[Interrupt] = []
        
        # Handler table: vector -> list of handlers
        self._handlers: Dict[int, List[InterruptHandler]] = {}
        
        # Global interrupt mask
        self._masked_vectors: Set[int] = set()
        
        # Interrupt enable flag
        self._interrupts_enabled = True
        
        # Lock for handler table
        self._lock = threading.RLock()
        
        # Processing thread
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        # Custom vector counter
        self._next_custom_vector = self.VECTOR_CUSTOM_BASE
        
        # Statistics
        self._stats = {
            "interrupts_raised": 0,
            "interrupts_handled": 0,
            "interrupts_masked": 0,
            "interrupts_deferred": 0,
            "handler_errors": 0
        }
        
        print("[InterruptHandler] Initialized")
    
    # =========================================================================
    # Handler registration
    # =========================================================================
    
    def register_handler(
        self,
        vector: int,
        handler: Callable[[Interrupt], bool],
        priority: InterruptPriority = InterruptPriority.NORMAL,
        owner: str = "kernel",
        mask: Set[int] = None
    ) -> str:
        """
        Register an interrupt handler.
        
        Args:
            vector: Interrupt vector number
            handler: Handler function (returns True if handled)
            priority: Handler priority
            owner: Owning module
            mask: Vectors to mask during handling
        
        Returns:
            Handler ID
        """
        handler_info = InterruptHandler(
            vector=vector,
            handler=handler,
            priority=priority,
            owner=owner,
            mask=mask or set()
        )
        
        with self._lock:
            if vector not in self._handlers:
                self._handlers[vector] = []
            
            # Insert by priority
            handlers = self._handlers[vector]
            insert_idx = 0
            for i, h in enumerate(handlers):
                if h.priority.value > priority.value:
                    insert_idx = i + 1
            handlers.insert(insert_idx, handler_info)
        
        return handler_info.id
    
    def unregister_handler(self, handler_id: str) -> bool:
        """Unregister an interrupt handler."""
        with self._lock:
            for vector, handlers in self._handlers.items():
                for i, h in enumerate(handlers):
                    if h.id == handler_id:
                        handlers.pop(i)
                        return True
        return False
    
    def unregister_all(self, owner: str) -> int:
        """Unregister all handlers for an owner."""
        count = 0
        with self._lock:
            for handlers in self._handlers.values():
                for i in range(len(handlers) - 1, -1, -1):
                    if handlers[i].owner == owner:
                        handlers.pop(i)
                        count += 1
        return count
    
    def allocate_vector(self) -> int:
        """Allocate a custom interrupt vector."""
        with self._lock:
            vector = self._next_custom_vector
            self._next_custom_vector += 1
            return vector
    
    # =========================================================================
    # Interrupt raising
    # =========================================================================
    
    def raise_interrupt(
        self,
        vector: int,
        data: Any = None,
        source: str = "kernel",
        priority: InterruptPriority = None,
        interrupt_type: InterruptType = InterruptType.SYSTEM
    ) -> str:
        """
        Raise an interrupt.
        
        Args:
            vector: Interrupt vector
            data: Interrupt data
            source: Source module
            priority: Override priority
            interrupt_type: Type of interrupt
        
        Returns:
            Interrupt ID
        """
        irq = Interrupt(
            type=interrupt_type,
            priority=priority or InterruptPriority.NORMAL,
            source=source,
            vector=vector,
            data=data
        )
        
        self._stats["interrupts_raised"] += 1
        
        # Check if masked
        if vector in self._masked_vectors and irq.priority != InterruptPriority.NMI:
            self._stats["interrupts_masked"] += 1
            return irq.id
        
        # Check if interrupts disabled
        if not self._interrupts_enabled and irq.priority != InterruptPriority.NMI:
            self._deferred.append(irq)
            self._stats["interrupts_deferred"] += 1
            return irq.id
        
        # Queue the interrupt
        # Priority queue sorts by (priority_value, timestamp)
        self._queue.put((irq.priority.value, irq.timestamp, irq))
        
        return irq.id
    
    def raise_timer(self, data: Any = None) -> str:
        """Raise a timer interrupt."""
        return self.raise_interrupt(
            self.VECTOR_TIMER,
            data,
            interrupt_type=InterruptType.TIMER
        )
    
    def raise_error(self, error: Exception, source: str = "kernel") -> str:
        """Raise an error interrupt."""
        return self.raise_interrupt(
            self.VECTOR_ERROR,
            {"error": str(error), "type": type(error).__name__},
            source=source,
            priority=InterruptPriority.HIGH,
            interrupt_type=InterruptType.ERROR
        )
    
    def raise_signal(self, signal_type: str, data: Any = None) -> str:
        """Raise a signal interrupt."""
        return self.raise_interrupt(
            self.VECTOR_SIGNAL,
            {"signal": signal_type, "data": data},
            interrupt_type=InterruptType.SIGNAL,
            priority=InterruptPriority.HIGH
        )
    
    # =========================================================================
    # Interrupt processing
    # =========================================================================
    
    def process_pending(self, max_count: int = 100) -> int:
        """Process pending interrupts."""
        processed = 0
        
        while processed < max_count:
            try:
                priority_value, timestamp, irq = self._queue.get_nowait()
            except queue.Empty:
                break
            
            self._handle_interrupt(irq)
            processed += 1
        
        return processed
    
    def _handle_interrupt(self, irq: Interrupt):
        """Handle a single interrupt."""
        handlers = self._handlers.get(irq.vector, [])
        
        if not handlers:
            # No handlers registered
            return
        
        # Get active mask
        active_mask = set(self._masked_vectors)
        
        for handler_info in handlers:
            if not handler_info.enabled:
                continue
            
            # Apply handler mask
            for v in handler_info.mask:
                self._masked_vectors.add(v)
            
            try:
                # Call handler
                handled = handler_info.handler(irq)
                handler_info.call_count += 1
                
                if handled:
                    irq.handled = True
                    self._stats["interrupts_handled"] += 1
                    break  # Stop chain if handled
                    
            except Exception as e:
                self._stats["handler_errors"] += 1
                print(f"[InterruptHandler] Handler error: {e}")
            
            finally:
                # Restore mask
                self._masked_vectors = active_mask
        
        # Handle chained interrupt
        if irq.chain_next:
            self._handle_interrupt(irq.chain_next)
    
    # =========================================================================
    # Interrupt control
    # =========================================================================
    
    def enable(self):
        """Enable interrupts globally."""
        self._interrupts_enabled = True
        
        # Process deferred interrupts
        for irq in self._deferred:
            self._queue.put((irq.priority.value, irq.timestamp, irq))
        self._deferred.clear()
    
    def disable(self):
        """Disable interrupts globally (except NMI)."""
        self._interrupts_enabled = False
    
    def mask(self, vector: int):
        """Mask a specific interrupt vector."""
        self._masked_vectors.add(vector)
    
    def unmask(self, vector: int):
        """Unmask a specific interrupt vector."""
        self._masked_vectors.discard(vector)
    
    def is_masked(self, vector: int) -> bool:
        """Check if a vector is masked."""
        return vector in self._masked_vectors
    
    # =========================================================================
    # Background processing
    # =========================================================================
    
    def start(self):
        """Start background interrupt processing."""
        if self._running:
            return
        
        self._running = True
        print("[InterruptHandler] Started")
    
    def stop(self):
        """Stop background interrupt processing."""
        self._running = False
        print("[InterruptHandler] Stopped")
    
    # =========================================================================
    # Utilities
    # =========================================================================
    
    def pending_count(self) -> int:
        """Get count of pending interrupts."""
        return self._queue.qsize()
    
    def get_handlers(self, vector: int = None) -> Dict[int, List[InterruptHandler]]:
        """Get registered handlers."""
        if vector is not None:
            return {vector: self._handlers.get(vector, [])}
        return dict(self._handlers)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get interrupt statistics."""
        return {
            **self._stats,
            "pending": self.pending_count(),
            "deferred": len(self._deferred),
            "masked_vectors": list(self._masked_vectors),
            "interrupts_enabled": self._interrupts_enabled,
            "registered_handlers": sum(
                len(handlers) for handlers in self._handlers.values()
            )
        }
    
    def clear_stats(self):
        """Clear statistics."""
        for key in self._stats:
            self._stats[key] = 0


# Alias for the module's main class
InterruptHandler = InterruptController
