# storyrealms/entity_system.py
"""
Story Realms Entity System

Manages all entities within a Story Realm: NPCs, players, creatures,
objects, locations, and abstract concepts. Designed for AI-driven
behavior and symbolic interaction.
"""

import uuid
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum


class EntityType(Enum):
    NPC = "npc"
    PLAYER = "player"
    CREATURE = "creature"
    OBJECT = "object"
    LOCATION = "location"
    CONCEPT = "concept"  # Abstract entities (ideas, factions, etc.)
    PORTAL = "portal"    # Connections between locations/realms


class EntityState(Enum):
    DORMANT = "dormant"
    ACTIVE = "active"
    INTERACTING = "interacting"
    MOVING = "moving"
    DESTROYED = "destroyed"


@dataclass
class EntityComponent:
    """Base component for entity composition."""
    component_type: str
    data: Dict = field(default_factory=dict)


@dataclass
class Entity:
    """
    Core entity representation in Story Realms.
    
    Uses a component-based architecture for flexible entity composition.
    AI agents can attach behaviors, memories, and goals to entities.
    """
    id: str
    name: str
    entity_type: EntityType
    state: EntityState = EntityState.DORMANT
    
    # Spatial properties
    location_id: Optional[str] = None
    position: Dict = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    
    # Core attributes
    attributes: Dict = field(default_factory=dict)
    
    # Component system (for flexible behaviors)
    components: Dict[str, EntityComponent] = field(default_factory=dict)
    
    # Relationships to other entities
    relationships: Dict[str, List[str]] = field(default_factory=dict)
    
    # AI-specific properties
    memories: List[Dict] = field(default_factory=list)
    goals: List[Dict] = field(default_factory=list)
    personality: Dict = field(default_factory=dict)
    dialog_state: Dict = field(default_factory=dict)
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    tags: Set[str] = field(default_factory=set)
    
    def add_component(self, component_type: str, data: Dict = None):
        """Add a component to this entity."""
        self.components[component_type] = EntityComponent(
            component_type=component_type,
            data=data or {}
        )
        self.last_updated = time.time()
    
    def get_component(self, component_type: str) -> Optional[EntityComponent]:
        """Get a component by type."""
        return self.components.get(component_type)
    
    def add_relationship(self, relationship_type: str, target_id: str):
        """Add a relationship to another entity."""
        if relationship_type not in self.relationships:
            self.relationships[relationship_type] = []
        if target_id not in self.relationships[relationship_type]:
            self.relationships[relationship_type].append(target_id)
        self.last_updated = time.time()
    
    def add_memory(self, memory: Dict):
        """Add a memory to this entity's memory bank."""
        memory["timestamp"] = time.time()
        self.memories.append(memory)
        # Keep memories bounded
        if len(self.memories) > 100:
            self.memories = self.memories[-100:]
        self.last_updated = time.time()
    
    def add_goal(self, goal: Dict):
        """Add a goal for this entity to pursue."""
        goal["created_at"] = time.time()
        goal["status"] = goal.get("status", "active")
        self.goals.append(goal)
        self.last_updated = time.time()
    
    def to_dict(self) -> Dict:
        """Convert entity to dictionary for serialization."""
        data = asdict(self)
        data["entity_type"] = self.entity_type.value
        data["state"] = self.state.value
        data["tags"] = list(self.tags)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Entity':
        """Create entity from dictionary."""
        data["entity_type"] = EntityType(data["entity_type"])
        data["state"] = EntityState(data["state"])
        data["tags"] = set(data.get("tags", []))
        
        # Reconstruct components
        components = {}
        for key, comp_data in data.get("components", {}).items():
            if isinstance(comp_data, dict):
                components[key] = EntityComponent(**comp_data)
        data["components"] = components
        
        return cls(**data)


class EntityManager:
    """
    Manages all entities within a Story Realm world.
    
    Provides:
    - Entity lifecycle management (spawn, update, despawn)
    - Spatial queries (entities near location, in region)
    - Relationship queries (find connected entities)
    - Component-based updates
    - AI behavior integration hooks
    """
    
    def __init__(self, world_engine):
        self.world_engine = world_engine
        self.entities: Dict[str, Entity] = {}
        self.spatial_index: Dict[str, Set[str]] = {}  # location_id -> entity_ids
        self.type_index: Dict[EntityType, Set[str]] = {}  # type -> entity_ids
        
        print("[EntityManager] Initialized")
    
    # ─────────────────────────────────────────────────────────────────
    # LIFECYCLE METHODS
    # ─────────────────────────────────────────────────────────────────
    
    def spawn(
        self,
        name: str,
        entity_type: EntityType | str,
        location_id: Optional[str] = None,
        position: Dict = None,
        attributes: Dict = None,
        personality: Dict = None,
        **kwargs
    ) -> Entity:
        """
        Spawn a new entity in the world.
        
        Args:
            name: Display name for the entity
            entity_type: Type of entity (NPC, OBJECT, etc.)
            location_id: Optional location to spawn at
            position: Optional position coordinates
            attributes: Initial attributes
            personality: AI personality traits (for NPCs)
            
        Returns:
            The newly created Entity
        """
        if isinstance(entity_type, str):
            entity_type = EntityType(entity_type.lower())
        
        entity = Entity(
            id=str(uuid.uuid4()),
            name=name,
            entity_type=entity_type,
            location_id=location_id,
            position=position or {"x": 0, "y": 0, "z": 0},
            attributes=attributes or {},
            personality=personality or {},
            state=EntityState.ACTIVE
        )
        
        # Store entity
        self.entities[entity.id] = entity
        
        # Update indices
        self._index_entity(entity)
        
        # Emit spawn event
        self.world_engine._emit_event("entity_spawned", {
            "entity_id": entity.id,
            "name": entity.name,
            "type": entity_type.value,
            "location": location_id
        })
        
        print(f"[EntityManager] Spawned {entity_type.value}: {name} ({entity.id[:8]}...)")
        return entity
    
    def despawn(self, entity_id: str, reason: str = "unknown") -> bool:
        """Remove an entity from the world."""
        if entity_id not in self.entities:
            return False
        
        entity = self.entities[entity_id]
        entity.state = EntityState.DESTROYED
        
        # Remove from indices
        self._unindex_entity(entity)
        
        # Keep in entities dict for reference but mark as destroyed
        self.world_engine._emit_event("entity_despawned", {
            "entity_id": entity_id,
            "name": entity.name,
            "reason": reason
        })
        
        print(f"[EntityManager] Despawned: {entity.name} (reason: {reason})")
        return True
    
    def update(self, entity_id: str, delta_time: float) -> Dict:
        """Update a single entity's state."""
        if entity_id not in self.entities:
            return {"status": "not_found"}
        
        entity = self.entities[entity_id]
        if entity.state == EntityState.DESTROYED:
            return {"status": "destroyed"}
        
        result = {"status": "updated", "actions": []}
        
        # Process AI behaviors if entity has them
        if entity.entity_type in [EntityType.NPC, EntityType.CREATURE]:
            actions = self._process_ai_behavior(entity, delta_time)
            result["actions"] = actions
        
        # Update components
        for comp_type, component in entity.components.items():
            self._update_component(entity, component, delta_time)
        
        entity.last_updated = time.time()
        return result
    
    def update_all(self, delta_time: float) -> Dict:
        """Update all active entities."""
        updated = 0
        actions = []
        
        for entity_id, entity in self.entities.items():
            if entity.state in [EntityState.ACTIVE, EntityState.MOVING, EntityState.INTERACTING]:
                result = self.update(entity_id, delta_time)
                if result["status"] == "updated":
                    updated += 1
                    actions.extend(result.get("actions", []))
        
        return {"updated": updated, "actions": actions}
    
    # ─────────────────────────────────────────────────────────────────
    # QUERY METHODS
    # ─────────────────────────────────────────────────────────────────
    
    def get(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID."""
        return self.entities.get(entity_id)
    
    def get_by_name(self, name: str) -> List[Entity]:
        """Find entities by name (partial match)."""
        return [e for e in self.entities.values() 
                if name.lower() in e.name.lower() and e.state != EntityState.DESTROYED]
    
    def get_by_type(self, entity_type: EntityType | str) -> List[Entity]:
        """Get all entities of a specific type."""
        if isinstance(entity_type, str):
            entity_type = EntityType(entity_type.lower())
        
        entity_ids = self.type_index.get(entity_type, set())
        return [self.entities[eid] for eid in entity_ids 
                if self.entities[eid].state != EntityState.DESTROYED]
    
    def get_at_location(self, location_id: str) -> List[Entity]:
        """Get all entities at a specific location."""
        entity_ids = self.spatial_index.get(location_id, set())
        return [self.entities[eid] for eid in entity_ids 
                if self.entities[eid].state != EntityState.DESTROYED]
    
    def get_nearby(self, entity_id: str, radius: float = 10.0) -> List[Entity]:
        """Get entities near another entity."""
        source = self.get(entity_id)
        if not source or not source.location_id:
            return []
        
        # Get entities at same location
        candidates = self.get_at_location(source.location_id)
        
        # Filter by distance
        nearby = []
        for entity in candidates:
            if entity.id == entity_id:
                continue
            dist = self._calculate_distance(source.position, entity.position)
            if dist <= radius:
                nearby.append(entity)
        
        return nearby
    
    def get_related(self, entity_id: str, relationship_type: str) -> List[Entity]:
        """Get entities related to the given entity."""
        entity = self.get(entity_id)
        if not entity:
            return []
        
        related_ids = entity.relationships.get(relationship_type, [])
        return [self.entities[rid] for rid in related_ids 
                if rid in self.entities and self.entities[rid].state != EntityState.DESTROYED]
    
    def query(self, **filters) -> List[Dict]:
        """
        Query entities with flexible filters.
        
        Supported filters:
        - type: EntityType or string
        - location: location_id
        - tags: list of required tags
        - attributes: dict of required attribute values
        - state: EntityState or string
        """
        results = list(self.entities.values())
        
        if "type" in filters:
            etype = filters["type"]
            if isinstance(etype, str):
                etype = EntityType(etype.lower())
            results = [e for e in results if e.entity_type == etype]
        
        if "location" in filters:
            results = [e for e in results if e.location_id == filters["location"]]
        
        if "tags" in filters:
            required_tags = set(filters["tags"])
            results = [e for e in results if required_tags.issubset(e.tags)]
        
        if "state" in filters:
            state = filters["state"]
            if isinstance(state, str):
                state = EntityState(state.lower())
            results = [e for e in results if e.state == state]
        
        # Exclude destroyed entities by default
        results = [e for e in results if e.state != EntityState.DESTROYED]
        
        return [e.to_dict() for e in results]
    
    # ─────────────────────────────────────────────────────────────────
    # ENTITY ACTIONS
    # ─────────────────────────────────────────────────────────────────
    
    def move_entity(self, entity_id: str, new_location_id: str, new_position: Dict = None):
        """Move an entity to a new location."""
        entity = self.get(entity_id)
        if not entity:
            return False
        
        old_location = entity.location_id
        
        # Update spatial index
        if old_location and old_location in self.spatial_index:
            self.spatial_index[old_location].discard(entity_id)
        
        entity.location_id = new_location_id
        if new_position:
            entity.position = new_position
        
        if new_location_id not in self.spatial_index:
            self.spatial_index[new_location_id] = set()
        self.spatial_index[new_location_id].add(entity_id)
        
        entity.state = EntityState.MOVING
        entity.last_updated = time.time()
        
        self.world_engine._emit_event("entity_moved", {
            "entity_id": entity_id,
            "from": old_location,
            "to": new_location_id
        })
        
        return True
    
    def interact(self, source_id: str, target_id: str, interaction_type: str, data: Dict = None):
        """Record an interaction between two entities."""
        source = self.get(source_id)
        target = self.get(target_id)
        
        if not source or not target:
            return {"status": "error", "message": "Entity not found"}
        
        interaction = {
            "type": interaction_type,
            "source": source_id,
            "target": target_id,
            "data": data or {},
            "timestamp": time.time()
        }
        
        # Add to both entities' memories
        source.add_memory({"type": "interaction", "role": "source", **interaction})
        target.add_memory({"type": "interaction", "role": "target", **interaction})
        
        # Update states
        source.state = EntityState.INTERACTING
        target.state = EntityState.INTERACTING
        
        self.world_engine._emit_event("entity_interaction", interaction)
        
        return {"status": "success", "interaction": interaction}
    
    # ─────────────────────────────────────────────────────────────────
    # INTERNAL HELPERS
    # ─────────────────────────────────────────────────────────────────
    
    def _index_entity(self, entity: Entity):
        """Add entity to lookup indices."""
        # Spatial index
        if entity.location_id:
            if entity.location_id not in self.spatial_index:
                self.spatial_index[entity.location_id] = set()
            self.spatial_index[entity.location_id].add(entity.id)
        
        # Type index
        if entity.entity_type not in self.type_index:
            self.type_index[entity.entity_type] = set()
        self.type_index[entity.entity_type].add(entity.id)
    
    def _unindex_entity(self, entity: Entity):
        """Remove entity from lookup indices."""
        if entity.location_id and entity.location_id in self.spatial_index:
            self.spatial_index[entity.location_id].discard(entity.id)
        
        if entity.entity_type in self.type_index:
            self.type_index[entity.entity_type].discard(entity.id)
    
    def _calculate_distance(self, pos1: Dict, pos2: Dict) -> float:
        """Calculate distance between two positions."""
        dx = pos1.get("x", 0) - pos2.get("x", 0)
        dy = pos1.get("y", 0) - pos2.get("y", 0)
        dz = pos1.get("z", 0) - pos2.get("z", 0)
        return (dx**2 + dy**2 + dz**2) ** 0.5
    
    def _process_ai_behavior(self, entity: Entity, delta_time: float) -> List[Dict]:
        """
        Process AI behaviors for intelligent entities.
        
        This hooks into the Daemon's AI systems for decision-making.
        """
        actions = []
        
        # Check active goals
        for goal in entity.goals:
            if goal.get("status") == "active":
                # Future: Use Daemon's reasoning system to decide actions
                action = self._evaluate_goal(entity, goal, delta_time)
                if action:
                    actions.append(action)
        
        return actions
    
    def _evaluate_goal(self, entity: Entity, goal: Dict, delta_time: float) -> Optional[Dict]:
        """Evaluate progress toward a goal and determine next action."""
        # Placeholder for AI goal evaluation
        # Future: Connect to unimind/reasoner for symbolic reasoning
        return None
    
    def _update_component(self, entity: Entity, component: EntityComponent, delta_time: float):
        """Update a specific component on an entity."""
        # Component-specific update logic
        if component.component_type == "health":
            self._update_health_component(entity, component, delta_time)
        elif component.component_type == "movement":
            self._update_movement_component(entity, component, delta_time)
        elif component.component_type == "inventory":
            pass  # Inventories don't need tick updates
    
    def _update_health_component(self, entity: Entity, component: EntityComponent, delta_time: float):
        """Update health regeneration/decay."""
        regen_rate = component.data.get("regen_rate", 0)
        if regen_rate > 0:
            current = component.data.get("current", 100)
            max_health = component.data.get("max", 100)
            component.data["current"] = min(max_health, current + regen_rate * delta_time)
    
    def _update_movement_component(self, entity: Entity, component: EntityComponent, delta_time: float):
        """Update entity movement toward destination."""
        destination = component.data.get("destination")
        speed = component.data.get("speed", 1.0)
        
        if destination:
            # Simple movement toward destination
            dx = destination.get("x", 0) - entity.position.get("x", 0)
            dy = destination.get("y", 0) - entity.position.get("y", 0)
            dz = destination.get("z", 0) - entity.position.get("z", 0)
            
            dist = (dx**2 + dy**2 + dz**2) ** 0.5
            if dist < speed * delta_time:
                # Arrived
                entity.position = destination.copy()
                component.data["destination"] = None
                entity.state = EntityState.ACTIVE
            else:
                # Move toward destination
                factor = (speed * delta_time) / dist
                entity.position["x"] += dx * factor
                entity.position["y"] += dy * factor
                entity.position["z"] += dz * factor
    
    # ─────────────────────────────────────────────────────────────────
    # SERIALIZATION
    # ─────────────────────────────────────────────────────────────────
    
    def export_all(self) -> List[Dict]:
        """Export all entities for persistence."""
        return [entity.to_dict() for entity in self.entities.values()]
    
    def import_all(self, entities_data: List[Dict]):
        """Import entities from persisted data."""
        self.entities.clear()
        self.spatial_index.clear()
        self.type_index.clear()
        
        for entity_data in entities_data:
            entity = Entity.from_dict(entity_data)
            self.entities[entity.id] = entity
            self._index_entity(entity)
        
        print(f"[EntityManager] Imported {len(self.entities)} entities")
