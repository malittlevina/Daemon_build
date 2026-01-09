from core.module import Module
import json
import os

class SpatialMap(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.anchors = {} # anchor_id -> {transform, entity_uid, user_id, type}
        self.db_path = "world_engine/anchors.json"

    def initialize(self):
        self._load()
        self.kernel.log("SpatialMap", "Initialized. Real-world anchors loaded.")

    def start(self):
        pass

    def stop(self):
        self._save()

    def _load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    self.anchors = json.load(f)
            except Exception as e:
                self.kernel.log("SpatialMap", f"Load error: {e}", level="error")

    def _save(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        try:
            with open(self.db_path, "w") as f:
                json.dump(self.anchors, f, indent=2)
        except Exception as e:
            self.kernel.log("SpatialMap", f"Save error: {e}", level="error")

    def register_anchor(self, anchor_id, coords, user_id="system"):
        """Register a real-world anchor discovered by a client."""
        self.anchors[anchor_id] = {
            "coords": coords, # e.g. [x, y, z, qx, qy, qz, qw]
            "user_id": user_id,
            "type": "cloud_anchor"
        }
        self.kernel.log("SpatialMap", f"Registered Anchor {anchor_id} at {coords}")
        self._save()

    def get_anchor(self, anchor_id):
        return self.anchors.get(anchor_id)

    def attach_entity(self, entity_uid, anchor_id):
        """Link an entity to an anchor logic."""
        # In a full system, this would update the Entity's SpatialAnchor component
        self.kernel.log("SpatialMap", f"Attached Entity {entity_uid} to Anchor {anchor_id}")
