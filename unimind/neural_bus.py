# unimind/neural_bus.py
# Neural Bus - Inter-module communication system for the cognitive architecture

import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from queue import Queue, Empty
import json


class SignalType(Enum):
    """Types of neural signals."""
    EXCITATORY = "excitatory"       # Activating signal
    INHIBITORY = "inhibitory"       # Suppressing signal
    MODULATORY = "modulatory"       # Modifying other signals
    BROADCAST = "broadcast"         # Global broadcast
    QUERY = "query"                 # Request for information
    RESPONSE = "response"           # Response to query
    SYNC = "sync"                   # Synchronization pulse
    ATTENTION = "attention"         # Attention direction
    REWARD = "reward"               # Reward/punishment signal


class Priority(Enum):
    """Signal priority levels."""
    CRITICAL = 0                    # Immediate processing (threats, errors)
    HIGH = 1                        # High priority (user input, goals)
    NORMAL = 2                      # Standard processing
    LOW = 3                         # Background processing
    MAINTENANCE = 4                 # System maintenance


@dataclass
class NeuralSignal:
    """Represents a signal traveling through the neural bus."""
    signal_id: str
    signal_type: SignalType
    source: str                     # Source module ID
    target: Optional[str]           # Target module ID (None for broadcast)
    payload: Dict[str, Any]
    priority: Priority = Priority.NORMAL
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    ttl: int = 5                    # Time-to-live (hops)
    requires_response: bool = False
    correlation_id: Optional[str] = None  # For request/response pairing
    
    def to_dict(self) -> Dict:
        return {
            "signal_id": self.signal_id,
            "type": self.signal_type.value,
            "source": self.source,
            "target": self.target,
            "payload": self.payload,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "ttl": self.ttl
        }


@dataclass
class BrainRegion:
    """Registration info for a brain region/module."""
    region_id: str
    name: str
    module_type: str                # e.g., "cortex", "limbic", "subcortical"
    capabilities: List[str]         # What this region can process
    handler: Callable[[NeuralSignal], Optional[NeuralSignal]]
    priority_override: Optional[Priority] = None
    enabled: bool = True
    signal_count: int = 0
    last_active: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "region_id": self.region_id,
            "name": self.name,
            "type": self.module_type,
            "capabilities": self.capabilities,
            "enabled": self.enabled,
            "signal_count": self.signal_count,
            "last_active": self.last_active
        }


class NeuralBus:
    """
    Central nervous system bus for inter-module communication.
    
    Provides:
    - Pub/sub messaging between brain regions
    - Priority-based signal routing
    - Broadcast and targeted signals
    - Attention modulation
    - Synchronization pulses
    - Signal history for debugging
    """
    
    def __init__(self, max_history: int = 1000):
        self.regions: Dict[str, BrainRegion] = {}
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)  # capability -> region_ids
        self.signal_queue: Queue = Queue()
        self.signal_history: List[NeuralSignal] = []
        self.max_history = max_history
        self.pending_responses: Dict[str, Queue] = {}  # correlation_id -> response queue
        
        # Global state
        self.global_attention: Optional[str] = None  # Current attention focus
        self.global_arousal: float = 0.5  # 0-1 arousal level
        self.inhibited_regions: Set[str] = set()
        
        # Processing
        self._running = False
        self._processor_thread: Optional[threading.Thread] = None
        self._signal_counter = 0
        
        print("[NeuralBus] Initialized.")
        
    def register_region(
        self,
        region_id: str,
        name: str,
        module_type: str,
        capabilities: List[str],
        handler: Callable[[NeuralSignal], Optional[NeuralSignal]]
    ) -> BrainRegion:
        """
        Register a brain region with the bus.
        
        Args:
            region_id: Unique identifier for the region
            name: Human-readable name
            module_type: Type of module (cortex, limbic, etc.)
            capabilities: List of signal types this region handles
            handler: Callback function to handle signals
            
        Returns:
            Created BrainRegion
        """
        region = BrainRegion(
            region_id=region_id,
            name=name,
            module_type=module_type,
            capabilities=capabilities,
            handler=handler
        )
        
        self.regions[region_id] = region
        
        # Subscribe to capabilities
        for capability in capabilities:
            self.subscriptions[capability].add(region_id)
            
        print(f"[NeuralBus] Registered region: {name} ({region_id})")
        return region
    
    def unregister_region(self, region_id: str) -> bool:
        """Unregister a brain region."""
        if region_id not in self.regions:
            return False
            
        region = self.regions[region_id]
        
        # Remove from subscriptions
        for capability in region.capabilities:
            self.subscriptions[capability].discard(region_id)
            
        del self.regions[region_id]
        print(f"[NeuralBus] Unregistered region: {region_id}")
        return True
    
    def _generate_signal_id(self) -> str:
        """Generate unique signal ID."""
        self._signal_counter += 1
        return f"sig_{int(time.time() * 1000)}_{self._signal_counter}"
    
    def emit(
        self,
        source: str,
        signal_type: str,
        payload: Dict[str, Any],
        target: Optional[str] = None,
        priority: str = "normal",
        requires_response: bool = False,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Emit a signal onto the bus.
        
        Args:
            source: Source region ID
            signal_type: Type of signal (excitatory, inhibitory, etc.)
            payload: Signal data
            target: Target region (None for broadcast based on capability)
            priority: Signal priority
            requires_response: Whether to wait for response
            correlation_id: ID for request/response pairing
            
        Returns:
            Signal ID
        """
        signal = NeuralSignal(
            signal_id=self._generate_signal_id(),
            signal_type=SignalType(signal_type),
            source=source,
            target=target,
            payload=payload,
            priority=Priority[priority.upper()],
            requires_response=requires_response,
            correlation_id=correlation_id or (self._generate_signal_id() if requires_response else None)
        )
        
        # Set up response queue if needed
        if requires_response and signal.correlation_id:
            self.pending_responses[signal.correlation_id] = Queue()
            
        self.signal_queue.put(signal)
        self._record_signal(signal)
        
        return signal.signal_id
    
    def emit_broadcast(
        self,
        source: str,
        payload: Dict[str, Any],
        priority: str = "normal"
    ) -> str:
        """Emit a broadcast signal to all regions."""
        return self.emit(
            source=source,
            signal_type="broadcast",
            payload=payload,
            target=None,
            priority=priority
        )
    
    def emit_query(
        self,
        source: str,
        capability: str,
        query_data: Dict[str, Any],
        timeout: float = 5.0
    ) -> Optional[Dict]:
        """
        Emit a query and wait for response.
        
        Args:
            source: Source region
            capability: Capability to query
            query_data: Query payload
            timeout: Timeout in seconds
            
        Returns:
            Response payload or None if timeout
        """
        correlation_id = self._generate_signal_id()
        self.pending_responses[correlation_id] = Queue()
        
        self.emit(
            source=source,
            signal_type="query",
            payload={"capability": capability, "data": query_data},
            target=None,  # Route to capability handlers
            priority="high",
            requires_response=True,
            correlation_id=correlation_id
        )
        
        # Wait for response
        try:
            response = self.pending_responses[correlation_id].get(timeout=timeout)
            return response.payload if response else None
        except Empty:
            return None
        finally:
            del self.pending_responses[correlation_id]
    
    def emit_attention(self, source: str, focus: str, intensity: float = 1.0):
        """Emit an attention signal to focus processing."""
        self.global_attention = focus
        self.emit(
            source=source,
            signal_type="attention",
            payload={"focus": focus, "intensity": intensity},
            priority="high"
        )
        
    def emit_sync(self, source: str, sync_data: Dict[str, Any] = None):
        """Emit a synchronization pulse."""
        self.emit(
            source=source,
            signal_type="sync",
            payload=sync_data or {"pulse": time.time()},
            priority="low"
        )
        
    def inhibit_region(self, region_id: str, duration_ms: int = 1000):
        """Temporarily inhibit a region."""
        self.inhibited_regions.add(region_id)
        
        def release():
            time.sleep(duration_ms / 1000)
            self.inhibited_regions.discard(region_id)
            
        threading.Thread(target=release, daemon=True).start()
        print(f"[NeuralBus] Inhibited region: {region_id} for {duration_ms}ms")
        
    def set_arousal(self, level: float):
        """Set global arousal level (affects processing speed/depth)."""
        self.global_arousal = max(0.0, min(1.0, level))
        self.emit_broadcast(
            source="neural_bus",
            payload={"arousal": self.global_arousal},
            priority="normal"
        )
        
    def _record_signal(self, signal: NeuralSignal):
        """Record signal in history."""
        self.signal_history.append(signal)
        if len(self.signal_history) > self.max_history:
            self.signal_history = self.signal_history[-self.max_history:]
            
    def _route_signal(self, signal: NeuralSignal):
        """Route a signal to appropriate regions."""
        targets = []
        
        if signal.target:
            # Direct target
            if signal.target in self.regions:
                targets.append(signal.target)
        elif signal.signal_type == SignalType.BROADCAST:
            # Broadcast to all
            targets = list(self.regions.keys())
        elif signal.signal_type == SignalType.QUERY:
            # Route to capability handlers
            capability = signal.payload.get("capability", "")
            targets = list(self.subscriptions.get(capability, set()))
        else:
            # Route based on signal type subscription
            targets = list(self.subscriptions.get(signal.signal_type.value, set()))
            
        # Filter inhibited regions
        targets = [t for t in targets if t not in self.inhibited_regions]
        
        return targets
    
    def _process_signal(self, signal: NeuralSignal):
        """Process a single signal."""
        if signal.ttl <= 0:
            return
            
        targets = self._route_signal(signal)
        
        for target_id in targets:
            region = self.regions.get(target_id)
            if not region or not region.enabled:
                continue
                
            try:
                # Call region handler
                response = region.handler(signal)
                region.signal_count += 1
                region.last_active = datetime.now().isoformat()
                
                # Handle response
                if response and signal.correlation_id:
                    response.correlation_id = signal.correlation_id
                    response.signal_type = SignalType.RESPONSE
                    
                    if signal.correlation_id in self.pending_responses:
                        self.pending_responses[signal.correlation_id].put(response)
                    else:
                        # Route response back to source
                        response.target = signal.source
                        self.signal_queue.put(response)
                        
            except Exception as e:
                print(f"[NeuralBus] Error processing signal in {target_id}: {e}")
    
    def process_queue(self, max_signals: int = 100) -> int:
        """
        Process pending signals in the queue.
        
        Args:
            max_signals: Maximum signals to process
            
        Returns:
            Number of signals processed
        """
        processed = 0
        
        # Sort by priority
        signals = []
        while not self.signal_queue.empty() and len(signals) < max_signals:
            try:
                signal = self.signal_queue.get_nowait()
                signals.append(signal)
            except Empty:
                break
                
        # Sort by priority (lower value = higher priority)
        signals.sort(key=lambda s: s.priority.value)
        
        for signal in signals:
            self._process_signal(signal)
            processed += 1
            
        return processed
    
    def start_processing(self, interval_ms: int = 10):
        """Start background signal processing."""
        if self._running:
            return
            
        self._running = True
        
        def processor():
            while self._running:
                self.process_queue()
                time.sleep(interval_ms / 1000)
                
        self._processor_thread = threading.Thread(target=processor, daemon=True)
        self._processor_thread.start()
        print("[NeuralBus] Started background processing.")
        
    def stop_processing(self):
        """Stop background processing."""
        self._running = False
        if self._processor_thread:
            self._processor_thread.join(timeout=1.0)
        print("[NeuralBus] Stopped processing.")
        
    def get_region_stats(self) -> List[Dict]:
        """Get statistics for all regions."""
        return [r.to_dict() for r in self.regions.values()]
    
    def get_recent_signals(self, count: int = 20) -> List[Dict]:
        """Get recent signal history."""
        return [s.to_dict() for s in self.signal_history[-count:]]
    
    def get_connectivity_map(self) -> Dict[str, List[str]]:
        """Get map of region connectivity based on signal history."""
        connections = defaultdict(set)
        
        for signal in self.signal_history:
            if signal.target:
                connections[signal.source].add(signal.target)
                
        return {k: list(v) for k, v in connections.items()}
    
    def get_bus_status(self) -> Dict[str, Any]:
        """Get overall bus status."""
        return {
            "regions_registered": len(self.regions),
            "subscriptions": {k: len(v) for k, v in self.subscriptions.items()},
            "queue_size": self.signal_queue.qsize(),
            "signals_processed": len(self.signal_history),
            "global_attention": self.global_attention,
            "global_arousal": self.global_arousal,
            "inhibited_regions": list(self.inhibited_regions),
            "is_processing": self._running
        }


# Global neural bus instance
_neural_bus: Optional[NeuralBus] = None


def get_neural_bus() -> NeuralBus:
    """Get or create the global neural bus."""
    global _neural_bus
    if _neural_bus is None:
        _neural_bus = NeuralBus()
    return _neural_bus
