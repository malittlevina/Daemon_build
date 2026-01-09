import os
import shutil
from .engine import StoryRealmsEngine

class Construct:
    def __init__(self, world_engine):
        self.world_engine = world_engine

    def move_artifact(self, realm_name, artifact_name, target_region_name):
        """
        Moves a file (Artifact) from its current location to a new folder (Region)
        both in the Realm AND on the actual hard drive.
        """
        if realm_name not in self.world_engine.realms:
            return "Realm not found."
        
        realm = self.world_engine.realms[realm_name]
        
        # 1. Find the Artifact Entity
        artifact = next((e for e in realm.entities if e.get("name") == artifact_name and e.get("type") == "Artifact"), None)
        if not artifact:
            return "Artifact not found."

        # 2. Find the Target Region in the Structure
        structure = realm.state.get("structure", {})
        if target_region_name not in structure:
            return "Target region not found."

        # 3. Resolve Real Paths
        origin_path = realm.state.get("origin_path")
        if not origin_path:
            return "Realm has no tether to physical reality (Origin Path missing)."

        current_rel_path = artifact.get("location")
        
        # Calculate source absolute path
        if current_rel_path == "Root":
            src_abs = os.path.join(origin_path, artifact_name)
        else:
            src_abs = os.path.join(origin_path, current_rel_path, artifact_name)

        # Calculate dest absolute path
        if target_region_name == "Root":
            dst_abs = os.path.join(origin_path, artifact_name)
        else:
            dst_abs = os.path.join(origin_path, target_region_name, artifact_name)

        # 4. Perform Physical Move
        try:
            shutil.move(src_abs, dst_abs)
        except Exception as e:
            return f"Physical move failed: {e}"

        # 5. Update Realm State
        # Update Entity Location
        artifact["location"] = target_region_name
        artifact["properties"]["path"] = dst_abs
        
        # Update Structure (Remove from old list, add to new)
        if current_rel_path in structure:
             if artifact_name in structure[current_rel_path]["artifacts"]:
                 structure[current_rel_path]["artifacts"].remove(artifact_name)
        
        if artifact_name not in structure[target_region_name]["artifacts"]:
            structure[target_region_name]["artifacts"].append(artifact_name)

        self.world_engine.save_realm(realm)
        return f"Construct moved '{artifact_name}' to '{target_region_name}'."

    def delete_artifact(self, realm_name, artifact_name):
        """
        Deletes a file (Artifact). Warning: Permanent.
        """
        if realm_name not in self.world_engine.realms:
            return "Realm not found."
        realm = self.world_engine.realms[realm_name]
        
        artifact = next((e for e in realm.entities if e.get("name") == artifact_name and e.get("type") == "Artifact"), None)
        if not artifact:
            return "Artifact not found."
            
        # Resolve Path
        path = artifact.get("properties", {}).get("path")
        if not path or not os.path.exists(path):
            return "Physical tether broken (File not found)."

        try:
            os.remove(path)
        except Exception as e:
            return f"Deletion failed: {e}"

        # Update Realm
        realm.entities.remove(artifact)
        loc = artifact.get("location")
        structure = realm.state.get("structure", {})
        if loc in structure and artifact_name in structure[loc]["artifacts"]:
            structure[loc]["artifacts"].remove(artifact_name)

        self.world_engine.save_realm(realm)
        return f"Artifact '{artifact_name}' has been erased from existence."
