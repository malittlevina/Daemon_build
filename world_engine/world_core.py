# world_engine/world_core.py
"""
World Engine Core - The heart of the world simulation system.

The WorldEngine orchestrates:
- Physics simulation
- Entity management
- Spatial indexing
- Rule processing
- Time flow
"""

import threading
import time
from typing import Dict, Any, Optional, List, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
import uuid


class WorldState(Enum):
    """World simulation states."""
    UNINITIALIZED = auto()
    LOADING = auto()
    RUNNING = auto()
    PAUSED = auto()
    STEPPING = auto()
    STOPPED = auto()


@dataclass
class WorldConfig:
    """Configuration for the world engine."""
    name: str = "default_world"
    
    # Simulation settings
    tick_rate: float = 60.0          # Physics ticks per second
    max_entities: int = 100000       # Maximum entities
    spatial_bounds: tuple = ((-1000, -1000, -1000), (1000, 1000, 1000))
    
    # Physics settings
    gravity: tuple = (0, -9.81, 0)   # Gravity vector
    air_resistance: float = 0.01     # Global air resistance
    time_scale: float = 1.0          # Time multiplier
    
    # Simulation features
    enable_physics: bool = True
    enable_collision: bool = True
    enable_rules: bool = True
    enable_causality: bool = True
    
    # Narrative features
    enable_narrative_physics: bool = True
    dramatic_tension_factor: float = 1.0


@dataclass
class WorldStats:
    """Statistics about the world simulation."""
    tick_count: int = 0
    entity_count: int = 0
    active_forces: int = 0
    active_constraints: int = 0
    collision_checks: int = 0
    collision_pairs: int = 0
    rules_evaluated: int = 0
    average_tick_ms: float = 0.0
    peak_tick_ms: float = 0.0


class WorldEngine:
    """
    The main world simulation engine.
    
    Provides a complete simulation environment with:
    - Physics (forces, constraints, collision)
    - Entities (bodies, particles, fields)
    - Spatial indexing (octree/grid)
    - Symbolic rules (causality, affordances)
    - Time management (pause, scale, step)
    """
    
    _worlds: Dict[str, 'WorldEngine'] = {}
    
    def __init__(self, config: WorldConfig = None, kernel=None):
        """Initialize the world engine."""
        self.config = config or WorldConfig()
        self.kernel = kernel
        self.id = str(uuid.uuid4())
        self.state = WorldState.UNINITIALIZED
        self.created_at = datetime.now()
        
        # Core systems (lazy loaded)
        self._physics = None
        self._spatial = None
        self._time_manager = None
        self._rule_engine = None
        self._causality = None
        
        # Entity storage
        self._entities: Dict[str, 'Entity'] = {}
        self._entities_by_type: Dict[str, Set[str]] = {}
        self._entities_by_tag: Dict[str, Set[str]] = {}
        
        # Zones and regions
        self._zones: Dict[str, 'Zone'] = {}
        
        # Event hooks
        self._tick_hooks: List[Callable] = []
        self._entity_hooks: Dict[str, List[Callable]] = {
            "added": [],
            "removed": [],
            "modified": []
        }
        
        # Threading
        self._lock = threading.RLock()
        self._simulation_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Statistics
        self.stats = WorldStats()
        self._tick_times: List[float] = []
        
        # Register world
        WorldEngine._worlds[self.id] = self
        
        print(f"[WorldEngine] Created world '{self.config.name}' ({self.id[:8]}...)")
    
    # =========================================================================
    # Lazy-loaded subsystems
    # =========================================================================
    
    @property
    def physics(self):
        """Get the physics engine (lazy loaded)."""
        if self._physics is None:
            from world_engine.physics.physics_engine import PhysicsEngine
            self._physics = PhysicsEngine(self)
        return self._physics
    
    @property
    def spatial(self):
        """Get the spatial index (lazy loaded)."""
        if self._spatial is None:
            from world_engine.spatial.spatial_index import SpatialIndex
            self._spatial = SpatialIndex(self)
        return self._spatial
    
    @property
    def time_manager(self):
        """Get the time manager (lazy loaded)."""
        if self._time_manager is None:
            from world_engine.time.time_manager import TimeManager
            self._time_manager = TimeManager(self)
        return self._time_manager
    
    @property
    def rules(self):
        """Get the rule engine (lazy loaded)."""
        if self._rule_engine is None:
            from world_engine.rules.rule_engine import RuleEngine
            self._rule_engine = RuleEngine(self)
        return self._rule_engine
    
    @property
    def causality(self):
        """Get the causality system (lazy loaded)."""
        if self._causality is None:
            from world_engine.rules.causality import CausalityEngine
            self._causality = CausalityEngine(self)
        return self._causality
    
    # =========================================================================
    # World lifecycle
    # =========================================================================
    
    def initialize(self) -> bool:
        """Initialize the world and all subsystems."""
        if self.state != WorldState.UNINITIALIZED:
            return False
        
        self.state = WorldState.LOADING
        
        try:
            # Initialize subsystems
            if self.config.enable_physics:
                _ = self.physics
            _ = self.spatial
            _ = self.time_manager
            if self.config.enable_rules:
                _ = self.rules
            if self.config.enable_causality:
                _ = self.causality
            
            self.state = WorldState.PAUSED
            print(f"[WorldEngine] World '{self.config.name}' initialized")
            return True
            
        except Exception as e:
            print(f"[WorldEngine] Initialization failed: {e}")
            self.state = WorldState.STOPPED
            return False
    
    def start(self, threaded: bool = True):
        """Start the world simulation."""
        if self.state == WorldState.UNINITIALIZED:
            self.initialize()
        
        if self.state not in (WorldState.PAUSED, WorldState.STOPPED):
            return
        
        self.state = WorldState.RUNNING
        self._stop_event.clear()
        
        if threaded:
            self._simulation_thread = threading.Thread(
                target=self._simulation_loop,
                name=f"World-{self.config.name}",
                daemon=True
            )
            self._simulation_thread.start()
        
        print(f"[WorldEngine] World '{self.config.name}' started")
    
    def pause(self):
        """Pause the world simulation."""
        if self.state == WorldState.RUNNING:
            self.state = WorldState.PAUSED
            print(f"[WorldEngine] World '{self.config.name}' paused")
    
    def resume(self):
        """Resume the world simulation."""
        if self.state == WorldState.PAUSED:
            self.state = WorldState.RUNNING
            print(f"[WorldEngine] World '{self.config.name}' resumed")
    
    def stop(self):
        """Stop the world simulation."""
        self._stop_event.set()
        self.state = WorldState.STOPPED
        
        if self._simulation_thread:
            self._simulation_thread.join(timeout=2.0)
        
        print(f"[WorldEngine] World '{self.config.name}' stopped")
    
    def step(self, dt: float = None):
        """Advance the simulation by one step."""
        if self.state in (WorldState.PAUSED, WorldState.RUNNING):
            old_state = self.state
            self.state = WorldState.STEPPING
            
            if dt is None:
                dt = 1.0 / self.config.tick_rate
            
            self._tick(dt)
            self.state = old_state
    
    # =========================================================================
    # Simulation loop
    # =========================================================================
    
    def _simulation_loop(self):
        """Main simulation loop."""
        tick_interval = 1.0 / self.config.tick_rate
        
        while not self._stop_event.is_set():
            if self.state != WorldState.RUNNING:
                time.sleep(0.01)
                continue
            
            tick_start = time.perf_counter()
            
            # Calculate delta time with time scaling
            dt = tick_interval * self.config.time_scale
            
            # Run simulation tick
            self._tick(dt)
            
            # Track timing
            tick_time = (time.perf_counter() - tick_start) * 1000
            self._tick_times.append(tick_time)
            if len(self._tick_times) > 100:
                self._tick_times.pop(0)
            
            self.stats.average_tick_ms = sum(self._tick_times) / len(self._tick_times)
            self.stats.peak_tick_ms = max(self.stats.peak_tick_ms, tick_time)
            
            # Sleep for remaining time
            elapsed = time.perf_counter() - tick_start
            sleep_time = max(0, tick_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def _tick(self, dt: float):
        """Execute one simulation tick."""
        self.stats.tick_count += 1
        
        # Update time
        self.time_manager.advance(dt)
        
        # Process rules (before physics)
        if self.config.enable_rules:
            self.rules.evaluate(dt)
        
        # Physics simulation
        if self.config.enable_physics:
            self.physics.step(dt)
        
        # Process causality
        if self.config.enable_causality:
            self.causality.process(dt)
        
        # Execute tick hooks
        for hook in self._tick_hooks:
            try:
                hook(self, dt)
            except Exception as e:
                print(f"[WorldEngine] Tick hook error: {e}")
        
        # Emit tick event to kernel
        if self.kernel:
            self.kernel.message_bus.emit("world.tick", {
                "world_id": self.id,
                "tick": self.stats.tick_count,
                "time": self.time_manager.current_time
            })
    
    # =========================================================================
    # Entity management
    # =========================================================================
    
    def add_entity(self, entity: 'Entity') -> str:
        """Add an entity to the world."""
        with self._lock:
            if len(self._entities) >= self.config.max_entities:
                raise RuntimeError("Maximum entity limit reached")
            
            entity.world = self
            self._entities[entity.id] = entity
            
            # Index by type
            type_name = type(entity).__name__
            if type_name not in self._entities_by_type:
                self._entities_by_type[type_name] = set()
            self._entities_by_type[type_name].add(entity.id)
            
            # Index by tags
            for tag in entity.tags:
                if tag not in self._entities_by_tag:
                    self._entities_by_tag[tag] = set()
                self._entities_by_tag[tag].add(entity.id)
            
            # Add to spatial index
            self.spatial.insert(entity)
            
            # Update stats
            self.stats.entity_count = len(self._entities)
            
            # Fire hooks
            for hook in self._entity_hooks["added"]:
                hook(entity)
        
        return entity.id
    
    def remove_entity(self, entity_id: str) -> bool:
        """Remove an entity from the world."""
        with self._lock:
            if entity_id not in self._entities:
                return False
            
            entity = self._entities[entity_id]
            
            # Remove from spatial index
            self.spatial.remove(entity)
            
            # Remove from type index
            type_name = type(entity).__name__
            if type_name in self._entities_by_type:
                self._entities_by_type[type_name].discard(entity_id)
            
            # Remove from tag index
            for tag in entity.tags:
                if tag in self._entities_by_tag:
                    self._entities_by_tag[tag].discard(entity_id)
            
            del self._entities[entity_id]
            entity.world = None
            
            # Update stats
            self.stats.entity_count = len(self._entities)
            
            # Fire hooks
            for hook in self._entity_hooks["removed"]:
                hook(entity)
        
        return True
    
    def get_entity(self, entity_id: str) -> Optional['Entity']:
        """Get an entity by ID."""
        return self._entities.get(entity_id)
    
    def get_entities_by_type(self, type_name: str) -> List['Entity']:
        """Get all entities of a specific type."""
        ids = self._entities_by_type.get(type_name, set())
        return [self._entities[eid] for eid in ids if eid in self._entities]
    
    def get_entities_by_tag(self, tag: str) -> List['Entity']:
        """Get all entities with a specific tag."""
        ids = self._entities_by_tag.get(tag, set())
        return [self._entities[eid] for eid in ids if eid in self._entities]
    
    def query_entities(self, predicate: Callable[['Entity'], bool]) -> List['Entity']:
        """Query entities with a predicate function."""
        return [e for e in self._entities.values() if predicate(e)]
    
    def get_all_entities(self) -> List['Entity']:
        """Get all entities in the world."""
        return list(self._entities.values())
    
    # =========================================================================
    # Spatial queries
    # =========================================================================
    
    def query_sphere(self, center: tuple, radius: float) -> List['Entity']:
        """Query entities within a sphere."""
        return self.spatial.query_sphere(center, radius)
    
    def query_box(self, min_point: tuple, max_point: tuple) -> List['Entity']:
        """Query entities within a box."""
        return self.spatial.query_box(min_point, max_point)
    
    def raycast(self, origin: tuple, direction: tuple, max_distance: float = 1000) -> List[tuple]:
        """Cast a ray and return hit entities with distances."""
        return self.spatial.raycast(origin, direction, max_distance)
    
    # =========================================================================
    # Zones
    # =========================================================================
    
    def create_zone(self, name: str, bounds: tuple, properties: Dict[str, Any] = None) -> 'Zone':
        """Create a zone in the world."""
        from world_engine.spatial.zone import Zone
        zone = Zone(name, bounds, properties or {})
        self._zones[name] = zone
        return zone
    
    def get_zone(self, name: str) -> Optional['Zone']:
        """Get a zone by name."""
        return self._zones.get(name)
    
    def get_zones_at(self, position: tuple) -> List['Zone']:
        """Get all zones containing a position."""
        return [z for z in self._zones.values() if z.contains(position)]
    
    # =========================================================================
    # Hooks
    # =========================================================================
    
    def on_tick(self, hook: Callable[['WorldEngine', float], None]):
        """Register a tick hook."""
        self._tick_hooks.append(hook)
    
    def on_entity_added(self, hook: Callable[['Entity'], None]):
        """Register an entity added hook."""
        self._entity_hooks["added"].append(hook)
    
    def on_entity_removed(self, hook: Callable[['Entity'], None]):
        """Register an entity removed hook."""
        self._entity_hooks["removed"].append(hook)
    
    # =========================================================================
    # Utilities
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get world status."""
        return {
            "id": self.id,
            "name": self.config.name,
            "state": self.state.name,
            "tick_count": self.stats.tick_count,
            "entity_count": self.stats.entity_count,
            "world_time": self.time_manager.current_time if self._time_manager else 0,
            "average_tick_ms": self.stats.average_tick_ms,
            "peak_tick_ms": self.stats.peak_tick_ms
        }
    
    @classmethod
    def get_world(cls, world_id: str) -> Optional['WorldEngine']:
        """Get a world by ID."""
        return cls._worlds.get(world_id)
    
    @classmethod
    def get_all_worlds(cls) -> Dict[str, 'WorldEngine']:
        """Get all active worlds."""
        return dict(cls._worlds)
