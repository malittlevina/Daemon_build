# kernel/memory_manager.py
"""
Memory Manager - Symbolic memory allocation and management.

The memory manager provides:
- Symbolic memory spaces for modules
- Short-term and long-term memory partitions
- Memory lifecycle management
- Garbage collection for expired memories
- Cross-module memory sharing
"""

import threading
import time
from typing import Dict, Any, Optional, List, Set, Callable
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
import weakref


class MemoryType(Enum):
    """Types of memory in the system."""
    EPHEMERAL = auto()     # Very short-lived (single interaction)
    SHORT_TERM = auto()    # Session-based memory
    WORKING = auto()       # Active task memory
    LONG_TERM = auto()     # Persistent memory
    PROCEDURAL = auto()    # Learned behaviors/patterns
    SEMANTIC = auto()      # Factual knowledge
    EPISODIC = auto()      # Event-based memories


class MemoryPriority(Enum):
    """Priority for memory retention."""
    CRITICAL = 0    # Never auto-expire
    HIGH = 1        # Long retention
    NORMAL = 2      # Standard retention
    LOW = 3         # Short retention
    TEMPORARY = 4   # Very short retention


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    namespace: str = "global"
    key: str = ""
    value: Any = None
    memory_type: MemoryType = MemoryType.SHORT_TERM
    priority: MemoryPriority = MemoryPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    owner: str = "kernel"


class MemorySpace:
    """A namespace for memory entries."""
    
    def __init__(self, name: str, max_entries: int = 10000):
        self.name = name
        self.max_entries = max_entries
        self._entries: Dict[str, MemoryEntry] = {}
        self._by_key: Dict[str, str] = {}  # key -> id
        self._by_tag: Dict[str, Set[str]] = {}  # tag -> set of ids
        self._lock = threading.RLock()
    
    def store(self, entry: MemoryEntry) -> str:
        """Store a memory entry."""
        with self._lock:
            # Evict if at capacity
            if len(self._entries) >= self.max_entries:
                self._evict_lowest_priority()
            
            self._entries[entry.id] = entry
            self._by_key[entry.key] = entry.id
            
            for tag in entry.tags:
                if tag not in self._by_tag:
                    self._by_tag[tag] = set()
                self._by_tag[tag].add(entry.id)
            
            return entry.id
    
    def get(self, key: str) -> Optional[MemoryEntry]:
        """Get a memory entry by key."""
        with self._lock:
            entry_id = self._by_key.get(key)
            if entry_id and entry_id in self._entries:
                entry = self._entries[entry_id]
                entry.accessed_at = datetime.now()
                entry.access_count += 1
                return entry
            return None
    
    def get_by_id(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get a memory entry by ID."""
        with self._lock:
            entry = self._entries.get(entry_id)
            if entry:
                entry.accessed_at = datetime.now()
                entry.access_count += 1
            return entry
    
    def delete(self, key: str) -> bool:
        """Delete a memory entry by key."""
        with self._lock:
            entry_id = self._by_key.get(key)
            if entry_id:
                return self._remove_entry(entry_id)
            return False
    
    def _remove_entry(self, entry_id: str) -> bool:
        """Remove an entry by ID."""
        if entry_id not in self._entries:
            return False
        
        entry = self._entries[entry_id]
        del self._entries[entry_id]
        self._by_key.pop(entry.key, None)
        
        for tag in entry.tags:
            if tag in self._by_tag:
                self._by_tag[tag].discard(entry_id)
        
        return True
    
    def _evict_lowest_priority(self):
        """Evict the lowest priority entry."""
        if not self._entries:
            return
        
        # Find lowest priority, least recently accessed
        candidates = sorted(
            self._entries.values(),
            key=lambda e: (e.priority.value, -e.accessed_at.timestamp())
        )
        
        # Don't evict critical entries
        for entry in reversed(candidates):
            if entry.priority != MemoryPriority.CRITICAL:
                self._remove_entry(entry.id)
                return
    
    def find_by_tag(self, tag: str) -> List[MemoryEntry]:
        """Find all entries with a tag."""
        with self._lock:
            entry_ids = self._by_tag.get(tag, set())
            return [self._entries[eid] for eid in entry_ids if eid in self._entries]
    
    def search(self, predicate: Callable[[MemoryEntry], bool]) -> List[MemoryEntry]:
        """Search entries with a predicate."""
        with self._lock:
            return [e for e in self._entries.values() if predicate(e)]
    
    def clear(self):
        """Clear all entries."""
        with self._lock:
            self._entries.clear()
            self._by_key.clear()
            self._by_tag.clear()
    
    def count(self) -> int:
        """Get entry count."""
        return len(self._entries)


class MemoryManager:
    """
    Symbolic memory management for the kernel.
    
    Features:
    - Multiple memory spaces (namespaces)
    - Memory type classification
    - Priority-based retention
    - Automatic garbage collection
    - Memory sharing between modules
    """
    
    # Default TTL by memory type (in seconds)
    DEFAULT_TTL = {
        MemoryType.EPHEMERAL: 60,           # 1 minute
        MemoryType.SHORT_TERM: 3600,        # 1 hour
        MemoryType.WORKING: 1800,           # 30 minutes
        MemoryType.LONG_TERM: None,         # Never expires
        MemoryType.PROCEDURAL: None,        # Never expires
        MemoryType.SEMANTIC: None,          # Never expires
        MemoryType.EPISODIC: 86400 * 30     # 30 days
    }
    
    def __init__(self, kernel):
        """Initialize the memory manager."""
        self.kernel = kernel
        self._spaces: Dict[str, MemorySpace] = {}
        self._lock = threading.RLock()
        self._gc_thread: Optional[threading.Thread] = None
        self._gc_running = False
        
        # Create default spaces
        self._create_default_spaces()
        
        # Statistics
        self._stats = {
            "stores": 0,
            "reads": 0,
            "evictions": 0,
            "gc_runs": 0
        }
        
        print("[MemoryManager] Initialized")
    
    def _create_default_spaces(self):
        """Create default memory spaces."""
        self._spaces["global"] = MemorySpace("global", max_entries=50000)
        self._spaces["kernel"] = MemorySpace("kernel", max_entries=10000)
        self._spaces["context"] = MemorySpace("context", max_entries=5000)
        self._spaces["cache"] = MemorySpace("cache", max_entries=20000)
    
    # =========================================================================
    # Memory operations
    # =========================================================================
    
    def store(
        self,
        key: str,
        value: Any,
        namespace: str = "global",
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        priority: MemoryPriority = MemoryPriority.NORMAL,
        ttl: Optional[float] = None,
        tags: Set[str] = None,
        owner: str = "kernel",
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store a value in memory.
        
        Args:
            key: Memory key
            value: Value to store
            namespace: Memory space name
            memory_type: Type of memory
            priority: Retention priority
            ttl: Time-to-live in seconds (overrides default)
            tags: Tags for searching
            owner: Owning module
            metadata: Additional metadata
        
        Returns:
            Memory entry ID
        """
        # Get or create namespace
        space = self._get_or_create_space(namespace)
        
        # Calculate expiration
        if ttl is None:
            ttl = self.DEFAULT_TTL.get(memory_type)
        
        expires_at = None
        if ttl is not None:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        entry = MemoryEntry(
            namespace=namespace,
            key=key,
            value=value,
            memory_type=memory_type,
            priority=priority,
            expires_at=expires_at,
            tags=tags or set(),
            owner=owner,
            metadata=metadata or {}
        )
        
        entry_id = space.store(entry)
        self._stats["stores"] += 1
        
        return entry_id
    
    def get(self, key: str, namespace: str = "global") -> Optional[Any]:
        """Get a value from memory."""
        space = self._spaces.get(namespace)
        if not space:
            return None
        
        entry = space.get(key)
        self._stats["reads"] += 1
        
        if entry:
            # Check expiration
            if entry.expires_at and datetime.now() > entry.expires_at:
                space.delete(key)
                return None
            return entry.value
        
        return None
    
    def get_entry(self, key: str, namespace: str = "global") -> Optional[MemoryEntry]:
        """Get a full memory entry."""
        space = self._spaces.get(namespace)
        if space:
            return space.get(key)
        return None
    
    def delete(self, key: str, namespace: str = "global") -> bool:
        """Delete a memory entry."""
        space = self._spaces.get(namespace)
        if space:
            return space.delete(key)
        return False
    
    def exists(self, key: str, namespace: str = "global") -> bool:
        """Check if a key exists."""
        return self.get(key, namespace) is not None
    
    # =========================================================================
    # Space management
    # =========================================================================
    
    def _get_or_create_space(self, name: str) -> MemorySpace:
        """Get or create a memory space."""
        with self._lock:
            if name not in self._spaces:
                self._spaces[name] = MemorySpace(name)
            return self._spaces[name]
    
    def create_space(self, name: str, max_entries: int = 10000) -> bool:
        """Create a new memory space."""
        with self._lock:
            if name in self._spaces:
                return False
            self._spaces[name] = MemorySpace(name, max_entries)
            return True
    
    def delete_space(self, name: str) -> bool:
        """Delete a memory space."""
        with self._lock:
            if name in ("global", "kernel"):
                return False  # Protected spaces
            if name in self._spaces:
                del self._spaces[name]
                return True
            return False
    
    def list_spaces(self) -> List[str]:
        """List all memory space names."""
        return list(self._spaces.keys())
    
    # =========================================================================
    # Search and query
    # =========================================================================
    
    def find_by_tag(self, tag: str, namespace: str = "global") -> List[Any]:
        """Find all values with a tag."""
        space = self._spaces.get(namespace)
        if not space:
            return []
        return [e.value for e in space.find_by_tag(tag)]
    
    def find_by_type(self, memory_type: MemoryType, namespace: str = "global") -> List[MemoryEntry]:
        """Find all entries of a type."""
        space = self._spaces.get(namespace)
        if not space:
            return []
        return space.search(lambda e: e.memory_type == memory_type)
    
    def find_by_owner(self, owner: str, namespace: str = "global") -> List[MemoryEntry]:
        """Find all entries owned by a module."""
        space = self._spaces.get(namespace)
        if not space:
            return []
        return space.search(lambda e: e.owner == owner)
    
    def search(
        self,
        namespace: str = "global",
        predicate: Callable[[MemoryEntry], bool] = None
    ) -> List[MemoryEntry]:
        """Search entries with a predicate."""
        space = self._spaces.get(namespace)
        if not space or not predicate:
            return []
        return space.search(predicate)
    
    # =========================================================================
    # Garbage collection
    # =========================================================================
    
    def gc(self) -> int:
        """Run garbage collection on all spaces."""
        collected = 0
        now = datetime.now()
        
        for space in self._spaces.values():
            with space._lock:
                expired_ids = []
                for entry_id, entry in space._entries.items():
                    if entry.expires_at and now > entry.expires_at:
                        expired_ids.append(entry_id)
                
                for entry_id in expired_ids:
                    space._remove_entry(entry_id)
                    collected += 1
        
        self._stats["evictions"] += collected
        self._stats["gc_runs"] += 1
        
        return collected
    
    def start_gc(self, interval: float = 60.0):
        """Start background garbage collection."""
        if self._gc_running:
            return
        
        self._gc_running = True
        
        def gc_loop():
            while self._gc_running:
                time.sleep(interval)
                collected = self.gc()
                if collected > 0:
                    print(f"[MemoryManager] GC collected {collected} entries")
        
        self._gc_thread = threading.Thread(
            target=gc_loop,
            name="MemoryGC",
            daemon=True
        )
        self._gc_thread.start()
        print("[MemoryManager] GC started")
    
    def stop_gc(self):
        """Stop background garbage collection."""
        self._gc_running = False
        if self._gc_thread:
            self._gc_thread.join(timeout=2.0)
        print("[MemoryManager] GC stopped")
    
    # =========================================================================
    # Convenience methods
    # =========================================================================
    
    def remember(self, key: str, value: Any, **kwargs) -> str:
        """Store a long-term memory."""
        return self.store(key, value, memory_type=MemoryType.LONG_TERM, **kwargs)
    
    def recall(self, key: str, namespace: str = "global") -> Optional[Any]:
        """Recall a memory (alias for get)."""
        return self.get(key, namespace)
    
    def forget(self, key: str, namespace: str = "global") -> bool:
        """Forget a memory (alias for delete)."""
        return self.delete(key, namespace)
    
    def cache(self, key: str, value: Any, ttl: float = 300) -> str:
        """Store in cache with TTL."""
        return self.store(
            key, value,
            namespace="cache",
            memory_type=MemoryType.EPHEMERAL,
            priority=MemoryPriority.TEMPORARY,
            ttl=ttl
        )
    
    def get_cached(self, key: str) -> Optional[Any]:
        """Get from cache."""
        return self.get(key, namespace="cache")
    
    # =========================================================================
    # Statistics
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory manager statistics."""
        space_stats = {}
        total_entries = 0
        
        for name, space in self._spaces.items():
            count = space.count()
            space_stats[name] = {
                "entries": count,
                "max_entries": space.max_entries
            }
            total_entries += count
        
        return {
            **self._stats,
            "total_entries": total_entries,
            "spaces": space_stats
        }
    
    def clear_all(self):
        """Clear all memory (except kernel space)."""
        for name, space in self._spaces.items():
            if name != "kernel":
                space.clear()
