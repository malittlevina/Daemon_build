import json
import importlib
from world_engine.ecs import EntityManager, Entity
from world_engine.components import * # Import all components for dynamic loading

class WorldSerializer:
    def serialize(self, entity_manager: EntityManager) -> str:
        data = {"entities": []}
        for uid, entity in entity_manager.entities.items():
            entity_data = {"uid": uid, "components": {}}
            for comp_type, comp in entity.components.items():
                # We assume all components have __init__ args matching their vars
                # or are simple data classes.
                # serialize class name
                class_name = comp_type.__name__
                entity_data["components"][class_name] = vars(comp)
            data["entities"].append(entity_data)
        return json.dumps(data, indent=2)

    def deserialize(self, json_data: str) -> EntityManager:
        manager = EntityManager()
        data = json.loads(json_data)
        
        # Get module for dynamic class loading
        module = importlib.import_module("world_engine.components")

        for ent_data in data["entities"]:
            entity = Entity(ent_data["uid"])
            for comp_name, comp_vars in ent_data["components"].items():
                # Dynamic instantiation
                try:
                    cls = getattr(module, comp_name)
                    # We create instance. Ideally we'd match init args, 
                    # but for simple data components we can init empty/default and update dict.
                    # This requires components to have defaults for all args in __init__.
                    # Or we simply instantiate and blindly update __dict__.
                    instance = cls() # Relies on defaults!
                    instance.__dict__.update(comp_vars)
                    entity.add_component(instance)
                except Exception as e:
                    print(f"[Serializer] Failed to load component {comp_name}: {e}")
            
            manager.entities[entity.uid] = entity
            
        return manager
