# kernel/message_bus.py
"""
Message Bus - Inter-module communication and event system.

The message bus provides:
- Publish/subscribe event system
- Point-to-point messaging
- Request/response patterns
- Priority-based message queuing
- Topic-based routing
"""

import threading
import queue
import time
from typing import Dict, Any, Optional, List, Callable, Set
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class MessagePriority(Enum):
    """Message priority levels."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BULK = 4


class MessageType(Enum):
    """Types of messages in the system."""
    EVENT = auto()      # Fire-and-forget events
    REQUEST = auto()    # Request expecting response
    RESPONSE = auto()   # Response to a request
    BROADCAST = auto()  # System-wide broadcast
    SIGNAL = auto()     # Control signals


@dataclass(order=True)
class Message:
    """A message in the bus."""
    priority: int
    timestamp: float = field(compare=False)
    id: str = field(compare=False, default_factory=lambda: str(uuid.uuid4()))
    topic: str = field(compare=False, default="")
    type: MessageType = field(compare=False, default=MessageType.EVENT)
    source: str = field(compare=False, default="kernel")
    target: Optional[str] = field(compare=False, default=None)
    data: Any = field(compare=False, default=None)
    reply_to: Optional[str] = field(compare=False, default=None)
    ttl: Optional[float] = field(compare=False, default=None)
    metadata: Dict[str, Any] = field(compare=False, default_factory=dict)


@dataclass
class Subscription:
    """A subscription to a topic pattern."""
    id: str
    pattern: str
    handler: Callable[[Message], None]
    subscriber: str
    created_at: datetime = field(default_factory=datetime.now)
    filter_fn: Optional[Callable[[Message], bool]] = None
    once: bool = False


class MessageBus:
    """
    Central message bus for inter-module communication.
    
    Features:
    - Topic-based pub/sub
    - Pattern matching for topics (wildcards)
    - Priority queue for messages
    - Async message processing
    - Request/response correlation
    """
    
    def __init__(self, kernel):
        """Initialize the message bus."""
        self.kernel = kernel
        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        self._subscriptions: Dict[str, List[Subscription]] = {}
        self._pending_requests: Dict[str, threading.Event] = {}
        self._responses: Dict[str, Message] = {}
        self._lock = threading.RLock()
        self._running = False
        self._processor_thread: Optional[threading.Thread] = None
        
        # Statistics
        self._stats = {
            "messages_sent": 0,
            "messages_processed": 0,
            "messages_dropped": 0,
            "subscriptions_total": 0
        }
        
        # Wildcard cache for performance
        self._pattern_cache: Dict[str, List[str]] = {}
        
        print("[MessageBus] Initialized")
    
    # =========================================================================
    # Publishing
    # =========================================================================
    
    def emit(
        self,
        topic: str,
        data: Any = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        source: str = "kernel",
        target: Optional[str] = None,
        ttl: Optional[float] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Emit an event to the bus.
        
        Args:
            topic: Event topic (e.g., "module.started", "scroll.triggered")
            data: Event data payload
            priority: Message priority
            source: Source module name
            target: Optional specific target
            ttl: Time-to-live in seconds
            metadata: Additional metadata
        
        Returns:
            Message ID
        """
        msg = Message(
            priority=priority.value,
            timestamp=time.time(),
            topic=topic,
            type=MessageType.EVENT,
            source=source,
            target=target,
            data=data,
            ttl=ttl,
            metadata=metadata or {}
        )
        
        self._queue.put(msg)
        self._stats["messages_sent"] += 1
        
        return msg.id
    
    def broadcast(
        self,
        topic: str,
        data: Any = None,
        source: str = "kernel"
    ) -> str:
        """Broadcast a message to all subscribers."""
        msg = Message(
            priority=MessagePriority.HIGH.value,
            timestamp=time.time(),
            topic=topic,
            type=MessageType.BROADCAST,
            source=source,
            data=data
        )
        
        self._queue.put(msg)
        self._stats["messages_sent"] += 1
        
        return msg.id
    
    def signal(self, signal_type: str, data: Any = None) -> str:
        """Send a control signal."""
        msg = Message(
            priority=MessagePriority.CRITICAL.value,
            timestamp=time.time(),
            topic=f"signal.{signal_type}",
            type=MessageType.SIGNAL,
            source="kernel",
            data=data
        )
        
        self._queue.put(msg)
        self._stats["messages_sent"] += 1
        
        return msg.id
    
    def request(
        self,
        topic: str,
        data: Any = None,
        timeout: float = 5.0,
        source: str = "kernel"
    ) -> Optional[Any]:
        """
        Send a request and wait for response.
        
        Args:
            topic: Request topic
            data: Request data
            timeout: Timeout in seconds
            source: Source module
        
        Returns:
            Response data or None on timeout
        """
        msg = Message(
            priority=MessagePriority.HIGH.value,
            timestamp=time.time(),
            topic=topic,
            type=MessageType.REQUEST,
            source=source,
            data=data
        )
        
        # Create event for waiting
        event = threading.Event()
        self._pending_requests[msg.id] = event
        
        self._queue.put(msg)
        self._stats["messages_sent"] += 1
        
        # Wait for response
        if event.wait(timeout=timeout):
            response = self._responses.pop(msg.id, None)
            del self._pending_requests[msg.id]
            return response.data if response else None
        
        # Timeout
        self._pending_requests.pop(msg.id, None)
        return None
    
    def respond(self, original_msg: Message, data: Any):
        """Respond to a request message."""
        if original_msg.type != MessageType.REQUEST:
            return
        
        response = Message(
            priority=MessagePriority.HIGH.value,
            timestamp=time.time(),
            topic=f"{original_msg.topic}.response",
            type=MessageType.RESPONSE,
            source="kernel",
            target=original_msg.source,
            data=data,
            reply_to=original_msg.id
        )
        
        # Store response and signal
        self._responses[original_msg.id] = response
        event = self._pending_requests.get(original_msg.id)
        if event:
            event.set()
    
    # =========================================================================
    # Subscriptions
    # =========================================================================
    
    def subscribe(
        self,
        pattern: str,
        handler: Callable[[Message], None],
        subscriber: str = "anonymous",
        filter_fn: Optional[Callable[[Message], bool]] = None,
        once: bool = False
    ) -> str:
        """
        Subscribe to messages matching a pattern.
        
        Patterns:
        - "module.started" - exact match
        - "module.*" - wildcard suffix
        - "*.error" - wildcard prefix
        - "*" - all messages
        
        Args:
            pattern: Topic pattern to match
            handler: Callback function
            subscriber: Subscriber name
            filter_fn: Optional filter function
            once: If True, unsubscribe after first message
        
        Returns:
            Subscription ID
        """
        sub_id = str(uuid.uuid4())
        
        sub = Subscription(
            id=sub_id,
            pattern=pattern,
            handler=handler,
            subscriber=subscriber,
            filter_fn=filter_fn,
            once=once
        )
        
        with self._lock:
            if pattern not in self._subscriptions:
                self._subscriptions[pattern] = []
            self._subscriptions[pattern].append(sub)
            self._stats["subscriptions_total"] += 1
            self._invalidate_pattern_cache()
        
        return sub_id
    
    def unsubscribe(self, sub_id: str) -> bool:
        """Unsubscribe by subscription ID."""
        with self._lock:
            for pattern, subs in self._subscriptions.items():
                for i, sub in enumerate(subs):
                    if sub.id == sub_id:
                        subs.pop(i)
                        self._invalidate_pattern_cache()
                        return True
        return False
    
    def unsubscribe_all(self, subscriber: str) -> int:
        """Unsubscribe all subscriptions for a subscriber."""
        count = 0
        with self._lock:
            for pattern, subs in self._subscriptions.items():
                for i in range(len(subs) - 1, -1, -1):
                    if subs[i].subscriber == subscriber:
                        subs.pop(i)
                        count += 1
            if count > 0:
                self._invalidate_pattern_cache()
        return count
    
    def _invalidate_pattern_cache(self):
        """Invalidate the pattern matching cache."""
        self._pattern_cache.clear()
    
    def _match_pattern(self, topic: str, pattern: str) -> bool:
        """Check if a topic matches a pattern."""
        if pattern == "*":
            return True
        if pattern == topic:
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return topic.startswith(prefix + ".") or topic == prefix
        if pattern.startswith("*."):
            suffix = pattern[1:]
            return topic.endswith(suffix)
        return False
    
    def _get_matching_subscriptions(self, topic: str) -> List[Subscription]:
        """Get all subscriptions matching a topic."""
        # Check cache first
        if topic in self._pattern_cache:
            sub_ids = self._pattern_cache[topic]
            result = []
            for pattern, subs in self._subscriptions.items():
                for sub in subs:
                    if sub.id in sub_ids:
                        result.append(sub)
            return result
        
        # Find matching subscriptions
        matching = []
        matching_ids = set()
        
        with self._lock:
            for pattern, subs in self._subscriptions.items():
                if self._match_pattern(topic, pattern):
                    for sub in subs:
                        matching.append(sub)
                        matching_ids.add(sub.id)
        
        # Cache result
        self._pattern_cache[topic] = matching_ids
        
        return matching
    
    # =========================================================================
    # Message processing
    # =========================================================================
    
    def process_queue(self, max_messages: int = 100):
        """Process pending messages in the queue."""
        processed = 0
        to_unsubscribe = []
        
        while processed < max_messages:
            try:
                msg = self._queue.get_nowait()
            except queue.Empty:
                break
            
            # Check TTL
            if msg.ttl and (time.time() - msg.timestamp) > msg.ttl:
                self._stats["messages_dropped"] += 1
                continue
            
            # Get matching subscriptions
            subscriptions = self._get_matching_subscriptions(msg.topic)
            
            # Deliver to subscribers
            for sub in subscriptions:
                try:
                    # Apply filter
                    if sub.filter_fn and not sub.filter_fn(msg):
                        continue
                    
                    # Check target
                    if msg.target and msg.target != sub.subscriber:
                        continue
                    
                    # Call handler
                    sub.handler(msg)
                    
                    # Mark for unsubscribe if once
                    if sub.once:
                        to_unsubscribe.append(sub.id)
                        
                except Exception as e:
                    print(f"[MessageBus] Handler error for {msg.topic}: {e}")
            
            processed += 1
            self._stats["messages_processed"] += 1
        
        # Clean up one-time subscriptions
        for sub_id in to_unsubscribe:
            self.unsubscribe(sub_id)
        
        return processed
    
    def start_processor(self):
        """Start background message processor."""
        if self._running:
            return
        
        self._running = True
        
        def processor_loop():
            while self._running:
                self.process_queue()
                time.sleep(0.01)  # 100 Hz processing
        
        self._processor_thread = threading.Thread(
            target=processor_loop,
            name="MessageBusProcessor",
            daemon=True
        )
        self._processor_thread.start()
        print("[MessageBus] Background processor started")
    
    def stop_processor(self):
        """Stop background message processor."""
        self._running = False
        if self._processor_thread:
            self._processor_thread.join(timeout=1.0)
        print("[MessageBus] Background processor stopped")
    
    # =========================================================================
    # Utilities
    # =========================================================================
    
    def queue_size(self) -> int:
        """Get current queue size."""
        return self._queue.qsize()
    
    def clear_queue(self):
        """Clear all pending messages."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
    
    def get_subscriptions(self, pattern: Optional[str] = None) -> List[Subscription]:
        """Get subscriptions, optionally filtered by pattern."""
        if pattern:
            return self._subscriptions.get(pattern, [])
        
        all_subs = []
        for subs in self._subscriptions.values():
            all_subs.extend(subs)
        return all_subs
    
    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistics."""
        return {
            **self._stats,
            "queue_size": self.queue_size(),
            "active_patterns": len(self._subscriptions),
            "pending_requests": len(self._pending_requests)
        }
    
    # =========================================================================
    # Convenience methods
    # =========================================================================
    
    def on(self, topic: str, handler: Callable[[Message], None], subscriber: str = "anonymous") -> str:
        """Alias for subscribe."""
        return self.subscribe(topic, handler, subscriber)
    
    def once(self, topic: str, handler: Callable[[Message], None], subscriber: str = "anonymous") -> str:
        """Subscribe to a topic for a single message."""
        return self.subscribe(topic, handler, subscriber, once=True)
    
    def off(self, sub_id: str) -> bool:
        """Alias for unsubscribe."""
        return self.unsubscribe(sub_id)
