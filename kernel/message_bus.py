# kernel/message_bus.py
"""
Message Bus - Inter-module communication backbone

Enables decoupled, event-driven architecture where modules
can publish events and subscribe to topics without direct dependencies.
"""

from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
import queue
import uuid


class MessagePriority(Enum):
    CRITICAL = 0  # System-critical, processed immediately
    HIGH = 1      # Time-sensitive operations
    NORMAL = 2    # Standard operations
    LOW = 3       # Background tasks
    DEFERRED = 4  # Can wait indefinitely


@dataclass
class KernelMessage:
    """A message passed through the kernel message bus."""
    topic: str
    payload: Any
    source: str
    priority: MessagePriority = MessagePriority.NORMAL
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None  # For request-response patterns
    ttl_ms: Optional[int] = None  # Time-to-live in milliseconds
    
    def is_expired(self) -> bool:
        if self.ttl_ms is None:
            return False
        elapsed = (datetime.utcnow() - self.timestamp).total_seconds() * 1000
        return elapsed > self.ttl_ms


class MessageBus:
    """
    Central message bus for kernel inter-module communication.
    
    Features:
    - Topic-based publish/subscribe
    - Priority queuing
    - Async and sync message handling
    - Message correlation for request-response
    - Dead letter queue for failed messages
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._wildcard_subscribers: List[tuple] = []  # (pattern, callback)
        self._message_queue: queue.PriorityQueue = queue.PriorityQueue()
        self._response_waiters: Dict[str, threading.Event] = {}
        self._responses: Dict[str, Any] = {}
        self._dead_letters: List[KernelMessage] = []
        self._lock = threading.RLock()
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._message_history: List[KernelMessage] = []
        self._max_history = 1000
        
        print("[MessageBus] Initialized.")
    
    def start(self):
        """Start the message processing loop."""
        self._running = True
        self._worker_thread = threading.Thread(target=self._process_loop, daemon=True)
        self._worker_thread.start()
        print("[MessageBus] Started message processing.")
    
    def stop(self):
        """Stop the message processing loop."""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=2.0)
        print("[MessageBus] Stopped.")
    
    def subscribe(self, topic: str, callback: Callable[[KernelMessage], Any]):
        """Subscribe to a specific topic."""
        with self._lock:
            if topic not in self._subscribers:
                self._subscribers[topic] = []
            self._subscribers[topic].append(callback)
            print(f"[MessageBus] Subscribed to topic: {topic}")
    
    def subscribe_pattern(self, pattern: str, callback: Callable[[KernelMessage], Any]):
        """Subscribe to topics matching a wildcard pattern (e.g., 'memory.*')."""
        with self._lock:
            self._wildcard_subscribers.append((pattern, callback))
            print(f"[MessageBus] Subscribed to pattern: {pattern}")
    
    def unsubscribe(self, topic: str, callback: Callable):
        """Remove a subscription."""
        with self._lock:
            if topic in self._subscribers:
                self._subscribers[topic] = [cb for cb in self._subscribers[topic] if cb != callback]
    
    def publish(self, message: KernelMessage) -> str:
        """Publish a message to the bus. Returns the message ID."""
        if message.is_expired():
            self._dead_letters.append(message)
            return message.message_id
            
        # Priority queue uses (priority_value, timestamp, message) for ordering
        self._message_queue.put((
            message.priority.value,
            message.timestamp.timestamp(),
            message
        ))
        
        # Track history
        with self._lock:
            self._message_history.append(message)
            if len(self._message_history) > self._max_history:
                self._message_history = self._message_history[-self._max_history:]
        
        return message.message_id
    
    def publish_sync(self, topic: str, payload: Any, source: str, 
                     priority: MessagePriority = MessagePriority.NORMAL) -> str:
        """Convenience method for synchronous publishing."""
        message = KernelMessage(topic=topic, payload=payload, source=source, priority=priority)
        return self.publish(message)
    
    def request(self, message: KernelMessage, timeout_ms: int = 5000) -> Optional[Any]:
        """
        Send a request and wait for a response (request-response pattern).
        Returns the response payload or None on timeout.
        """
        correlation_id = message.message_id
        event = threading.Event()
        
        with self._lock:
            self._response_waiters[correlation_id] = event
        
        self.publish(message)
        
        # Wait for response
        if event.wait(timeout=timeout_ms / 1000):
            with self._lock:
                response = self._responses.pop(correlation_id, None)
                self._response_waiters.pop(correlation_id, None)
            return response
        
        # Timeout
        with self._lock:
            self._response_waiters.pop(correlation_id, None)
        return None
    
    def respond(self, correlation_id: str, payload: Any):
        """Send a response to a request."""
        with self._lock:
            if correlation_id in self._response_waiters:
                self._responses[correlation_id] = payload
                self._response_waiters[correlation_id].set()
    
    def _process_loop(self):
        """Main message processing loop."""
        while self._running:
            try:
                # Block for up to 100ms waiting for messages
                priority, timestamp, message = self._message_queue.get(timeout=0.1)
                self._dispatch(message)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[MessageBus] Processing error: {e}")
    
    def _dispatch(self, message: KernelMessage):
        """Dispatch a message to all matching subscribers."""
        if message.is_expired():
            self._dead_letters.append(message)
            return
        
        handlers = []
        
        with self._lock:
            # Direct topic subscribers
            if message.topic in self._subscribers:
                handlers.extend(self._subscribers[message.topic])
            
            # Wildcard pattern matching
            for pattern, callback in self._wildcard_subscribers:
                if self._matches_pattern(pattern, message.topic):
                    handlers.append(callback)
        
        # Execute handlers
        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                print(f"[MessageBus] Handler error for {message.topic}: {e}")
                self._dead_letters.append(message)
    
    def _matches_pattern(self, pattern: str, topic: str) -> bool:
        """Check if topic matches a wildcard pattern."""
        if pattern == "*":
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return topic.startswith(prefix + ".") or topic == prefix
        if pattern.endswith(".**"):
            prefix = pattern[:-3]
            return topic.startswith(prefix)
        return pattern == topic
    
    def get_dead_letters(self) -> List[KernelMessage]:
        """Retrieve failed/expired messages for inspection."""
        return list(self._dead_letters)
    
    def get_history(self, topic: Optional[str] = None, limit: int = 100) -> List[KernelMessage]:
        """Get recent message history, optionally filtered by topic."""
        with self._lock:
            if topic:
                filtered = [m for m in self._message_history if m.topic == topic]
            else:
                filtered = self._message_history
            return filtered[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistics."""
        with self._lock:
            return {
                "total_subscribers": sum(len(subs) for subs in self._subscribers.values()),
                "topics": list(self._subscribers.keys()),
                "queue_size": self._message_queue.qsize(),
                "dead_letters": len(self._dead_letters),
                "history_size": len(self._message_history),
                "running": self._running
            }
