import uuid
from typing import Dict, List, Type, Any, Optional

EntityID = str

class Component:
    """Base class for all data components."""
    pass

class Entity:
    def __init__(self, uid: EntityID):
        self.uid = uid
        self.components: Dict[Type[Component], Component] = {}

    def add_component(self, component: Component):
        self.components[type(component)] = component

    def get_component(self, component_type: Type[Component]) -> Optional[Component]:
        return self.components.get(component_type)

    def has_component(self, component_type: Type[Component]) -> bool:
        return component_type in self.components

class System:
    """Base class for logic systems."""
    def __init__(self, world):
        self.world = world

    def update(self, delta_time: float):
        pass

class EntityManager:
    def __init__(self):
        self.entities: Dict[EntityID, Entity] = {}

    def create_entity(self) -> Entity:
        uid = str(uuid.uuid4())[:8]
        entity = Entity(uid)
        self.entities[uid] = entity
        return entity

    def get_entity(self, uid: EntityID) -> Optional[Entity]:
        return self.entities.get(uid)

    def get_entities_with(self, *component_types: Type[Component]) -> List[Entity]:
        result = []
        for entity in self.entities.values():
            if all(entity.has_component(ct) for ct in component_types):
                result.append(entity)
        return result

    def destroy_entity(self, uid: EntityID):
        if uid in self.entities:
            del self.entities[uid]
