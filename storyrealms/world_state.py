# storyrealms/world_state.py
"""
Story Realms World State Manager

Handles persistence, snapshots, and state management for Story Realm worlds.
Provides save/load functionality and state versioning.
"""

import json
import os
import time
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class WorldSnapshot:
    """A snapshot of world state at a point in time."""
    id: str
    world_name: str
    timestamp: float
    world_time: float
    tick_count: int
    checksum: str
    metadata: Dict = field(default_factory=dict)
    
    # File reference (if saved to disk)
    file_path: Optional[str] = None


class WorldStateManager:
    """
    Manages persistence and state for Story Realm worlds.
    
    Provides:
    - Save/load world state to disk
    - Automatic snapshots and backups
    - State versioning and rollback
    - State validation and checksums
    """
    
    def __init__(self, persistence_path: str = "storyrealms/worlds"):
        self.persistence_path = persistence_path
        self.snapshots: Dict[str, List[WorldSnapshot]] = {}  # world_name -> snapshots
        self.autosave_enabled = True
        self.autosave_interval = 300.0  # seconds
        self.max_snapshots = 10  # per world
        self.last_autosave: Dict[str, float] = {}
        
        # Ensure persistence directory exists
        os.makedirs(persistence_path, exist_ok=True)
        
        print(f"[WorldStateManager] Initialized at: {persistence_path}")
    
    # ─────────────────────────────────────────────────────────────────
    # SAVE/LOAD OPERATIONS
    # ─────────────────────────────────────────────────────────────────
    
    def save_world_state(self, state: Dict, world_name: str = None) -> str:
        """
        Save world state to disk.
        
        Args:
            state: Full world state dictionary
            world_name: Name of the world (defaults to state's realm_name)
            
        Returns:
            Path to saved state file
        """
        world_name = world_name or state.get("metadata", {}).get("realm_name", "unknown")
        
        # Create world directory
        world_dir = os.path.join(self.persistence_path, world_name)
        os.makedirs(world_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"state_{timestamp}.json"
        filepath = os.path.join(world_dir, filename)
        
        # Add save metadata
        state["_save_metadata"] = {
            "saved_at": time.time(),
            "saved_at_readable": datetime.now().isoformat(),
            "version": "1.0.0",
            "checksum": self._calculate_checksum(state)
        }
        
        # Write to file
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2, default=str)
        
        # Update current state symlink
        current_link = os.path.join(world_dir, "current.json")
        if os.path.exists(current_link):
            os.remove(current_link)
        
        # Copy to current.json (symlinks can be problematic)
        with open(current_link, "w") as f:
            json.dump(state, f, indent=2, default=str)
        
        # Create snapshot record
        snapshot = WorldSnapshot(
            id=f"{world_name}_{timestamp}",
            world_name=world_name,
            timestamp=time.time(),
            world_time=state.get("world_time", 0),
            tick_count=state.get("tick_count", 0),
            checksum=state["_save_metadata"]["checksum"],
            file_path=filepath
        )
        
        self._record_snapshot(snapshot)
        self.last_autosave[world_name] = time.time()
        
        print(f"[WorldStateManager] Saved world state: {filepath}")
        return filepath
    
    def load_world_state(self, world_name: str, snapshot_id: str = None) -> Optional[Dict]:
        """
        Load world state from disk.
        
        Args:
            world_name: Name of the world to load
            snapshot_id: Specific snapshot to load (defaults to current)
            
        Returns:
            World state dictionary or None if not found
        """
        world_dir = os.path.join(self.persistence_path, world_name)
        
        if snapshot_id:
            # Load specific snapshot
            snapshots = self.snapshots.get(world_name, [])
            snapshot = next((s for s in snapshots if s.id == snapshot_id), None)
            if snapshot and snapshot.file_path:
                filepath = snapshot.file_path
            else:
                print(f"[WorldStateManager] Snapshot not found: {snapshot_id}")
                return None
        else:
            # Load current state
            filepath = os.path.join(world_dir, "current.json")
        
        if not os.path.exists(filepath):
            print(f"[WorldStateManager] State file not found: {filepath}")
            return None
        
        try:
            with open(filepath, "r") as f:
                state = json.load(f)
            
            # Validate checksum
            if "_save_metadata" in state:
                saved_checksum = state["_save_metadata"].get("checksum")
                metadata = state.pop("_save_metadata")
                current_checksum = self._calculate_checksum(state)
                
                if saved_checksum and saved_checksum != current_checksum:
                    print(f"[WorldStateManager] Warning: State checksum mismatch!")
                    # State might be corrupted, but still return it
            
            print(f"[WorldStateManager] Loaded world state: {filepath}")
            return state
            
        except Exception as e:
            print(f"[WorldStateManager] Error loading state: {e}")
            return None
    
    def delete_world(self, world_name: str) -> bool:
        """Delete all saved states for a world."""
        import shutil
        
        world_dir = os.path.join(self.persistence_path, world_name)
        if os.path.exists(world_dir):
            shutil.rmtree(world_dir)
            self.snapshots.pop(world_name, None)
            print(f"[WorldStateManager] Deleted world: {world_name}")
            return True
        return False
    
    # ─────────────────────────────────────────────────────────────────
    # SNAPSHOT MANAGEMENT
    # ─────────────────────────────────────────────────────────────────
    
    def _record_snapshot(self, snapshot: WorldSnapshot):
        """Record a snapshot and prune old ones."""
        world_name = snapshot.world_name
        
        if world_name not in self.snapshots:
            self.snapshots[world_name] = []
        
        self.snapshots[world_name].append(snapshot)
        
        # Prune old snapshots
        if len(self.snapshots[world_name]) > self.max_snapshots:
            old_snapshots = self.snapshots[world_name][:-self.max_snapshots]
            self.snapshots[world_name] = self.snapshots[world_name][-self.max_snapshots:]
            
            # Delete old files
            for old in old_snapshots:
                if old.file_path and os.path.exists(old.file_path):
                    try:
                        os.remove(old.file_path)
                    except Exception:
                        pass
    
    def get_snapshots(self, world_name: str) -> List[WorldSnapshot]:
        """Get all snapshots for a world."""
        return self.snapshots.get(world_name, [])
    
    def rollback_to_snapshot(self, world_name: str, snapshot_id: str) -> Optional[Dict]:
        """
        Rollback a world to a previous snapshot.
        
        Returns the loaded state, which should be passed to WorldEngine.load_state()
        """
        state = self.load_world_state(world_name, snapshot_id)
        if state:
            # Save as current
            self.save_world_state(state, world_name)
        return state
    
    # ─────────────────────────────────────────────────────────────────
    # AUTOSAVE
    # ─────────────────────────────────────────────────────────────────
    
    def check_autosave(self, world_name: str, state: Dict) -> bool:
        """Check if autosave is needed and perform it."""
        if not self.autosave_enabled:
            return False
        
        last_save = self.last_autosave.get(world_name, 0)
        if time.time() - last_save >= self.autosave_interval:
            self.save_world_state(state, world_name)
            return True
        return False
    
    def enable_autosave(self, enabled: bool = True, interval: float = None):
        """Configure autosave settings."""
        self.autosave_enabled = enabled
        if interval:
            self.autosave_interval = interval
    
    # ─────────────────────────────────────────────────────────────────
    # STATE EXPORT/IMPORT
    # ─────────────────────────────────────────────────────────────────
    
    def export_world(self, world_name: str, export_path: str) -> bool:
        """Export a world to a portable format."""
        state = self.load_world_state(world_name)
        if not state:
            return False
        
        export_data = {
            "format_version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "world_name": world_name,
            "state": state,
            "snapshots_count": len(self.snapshots.get(world_name, []))
        }
        
        with open(export_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"[WorldStateManager] Exported world to: {export_path}")
        return True
    
    def import_world(self, import_path: str, new_name: str = None) -> Optional[str]:
        """Import a world from an exported file."""
        if not os.path.exists(import_path):
            print(f"[WorldStateManager] Import file not found: {import_path}")
            return None
        
        with open(import_path, "r") as f:
            export_data = json.load(f)
        
        world_name = new_name or export_data.get("world_name", "imported_world")
        state = export_data.get("state", {})
        
        # Update realm name if renamed
        if new_name and "metadata" in state:
            state["metadata"]["realm_name"] = new_name
        if new_name and "config" in state:
            state["config"]["name"] = new_name
        
        self.save_world_state(state, world_name)
        print(f"[WorldStateManager] Imported world: {world_name}")
        return world_name
    
    # ─────────────────────────────────────────────────────────────────
    # UTILITIES
    # ─────────────────────────────────────────────────────────────────
    
    def _calculate_checksum(self, state: Dict) -> str:
        """Calculate a checksum for state validation."""
        # Create a stable string representation
        state_str = json.dumps(state, sort_keys=True, default=str)
        return hashlib.md5(state_str.encode()).hexdigest()
    
    def list_worlds(self) -> List[Dict]:
        """List all saved worlds."""
        worlds = []
        
        if not os.path.exists(self.persistence_path):
            return worlds
        
        for name in os.listdir(self.persistence_path):
            world_dir = os.path.join(self.persistence_path, name)
            if os.path.isdir(world_dir):
                current_file = os.path.join(world_dir, "current.json")
                
                world_info = {
                    "name": name,
                    "has_current_state": os.path.exists(current_file),
                    "snapshots": len(self.snapshots.get(name, []))
                }
                
                # Get last modified time
                if os.path.exists(current_file):
                    world_info["last_modified"] = os.path.getmtime(current_file)
                
                worlds.append(world_info)
        
        return sorted(worlds, key=lambda w: w.get("last_modified", 0), reverse=True)
    
    def get_world_info(self, world_name: str) -> Optional[Dict]:
        """Get information about a specific world."""
        world_dir = os.path.join(self.persistence_path, world_name)
        if not os.path.exists(world_dir):
            return None
        
        current_file = os.path.join(world_dir, "current.json")
        
        info = {
            "name": world_name,
            "directory": world_dir,
            "has_current_state": os.path.exists(current_file),
            "snapshots": []
        }
        
        # Get snapshots
        snapshots = self.snapshots.get(world_name, [])
        info["snapshots"] = [
            {
                "id": s.id,
                "timestamp": s.timestamp,
                "world_time": s.world_time,
                "tick_count": s.tick_count
            }
            for s in snapshots
        ]
        
        # Load current state metadata
        if os.path.exists(current_file):
            try:
                with open(current_file, "r") as f:
                    state = json.load(f)
                info["world_time"] = state.get("world_time", 0)
                info["tick_count"] = state.get("tick_count", 0)
                info["entity_count"] = len(state.get("entities", []))
                info["narrative_count"] = len(state.get("narratives", []))
            except Exception:
                pass
        
        return info
    
    def scan_for_worlds(self):
        """Scan persistence directory and rebuild snapshot indices."""
        if not os.path.exists(self.persistence_path):
            return
        
        for world_name in os.listdir(self.persistence_path):
            world_dir = os.path.join(self.persistence_path, world_name)
            if not os.path.isdir(world_dir):
                continue
            
            # Find all state files
            for filename in sorted(os.listdir(world_dir)):
                if filename.startswith("state_") and filename.endswith(".json"):
                    filepath = os.path.join(world_dir, filename)
                    try:
                        with open(filepath, "r") as f:
                            state = json.load(f)
                        
                        metadata = state.get("_save_metadata", {})
                        snapshot = WorldSnapshot(
                            id=f"{world_name}_{filename[6:-5]}",  # Extract timestamp from filename
                            world_name=world_name,
                            timestamp=metadata.get("saved_at", os.path.getmtime(filepath)),
                            world_time=state.get("world_time", 0),
                            tick_count=state.get("tick_count", 0),
                            checksum=metadata.get("checksum", ""),
                            file_path=filepath
                        )
                        
                        if world_name not in self.snapshots:
                            self.snapshots[world_name] = []
                        self.snapshots[world_name].append(snapshot)
                    except Exception as e:
                        print(f"[WorldStateManager] Error scanning {filepath}: {e}")
        
        print(f"[WorldStateManager] Scanned {len(self.snapshots)} worlds")
