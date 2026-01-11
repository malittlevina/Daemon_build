# xr/spatial_anchor.py
# Spatial Anchor System - Persistent world-space anchors for AR/XR content

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class AnchorType(Enum):
    """Types of spatial anchors."""
    POINT = "point"                  # Single point in space
    PLANE = "plane"                  # Detected plane (floor, wall, table)
    VOLUME = "volume"                # 3D volume/bounding box
    OBJECT = "object"                # Tracked object
    SEMANTIC = "semantic"            # Semantic location (door, window, etc.)
    CLOUD = "cloud"                  # Cloud-synced persistent anchor


class AnchorState(Enum):
    """Anchor tracking state."""
    TRACKING = "tracking"            # Actively being tracked
    LIMITED = "limited"              # Limited tracking (drift possible)
    NOT_TRACKING = "not_tracking"    # Lost tracking
    PENDING = "pending"              # Waiting to be resolved


class SpatialAnchor:
    """Represents a spatial anchor in the XR environment."""
    
    def __init__(
        self,
        anchor_id: str,
        anchor_type: AnchorType,
        position: Tuple[float, float, float],
        rotation: Tuple[float, float, float, float] = (0, 0, 0, 1),  # Quaternion
        label: Optional[str] = None
    ):
        self.anchor_id = anchor_id
        self.anchor_type = anchor_type
        self.position = position
        self.rotation = rotation  # Quaternion (x, y, z, w)
        self.label = label
        self.state = AnchorState.TRACKING
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.confidence = 1.0
        self.metadata: Dict[str, Any] = {}
        self.attached_overlays: List[str] = []
        self.persistent = False
        self.cloud_id: Optional[str] = None
        
    def update_pose(
        self,
        position: Tuple[float, float, float],
        rotation: Optional[Tuple[float, float, float, float]] = None,
        confidence: float = 1.0
    ):
        """Update anchor pose from tracking system."""
        self.position = position
        if rotation:
            self.rotation = rotation
        self.confidence = confidence
        self.last_updated = datetime.now()
        
    def set_state(self, state: AnchorState):
        """Set anchor tracking state."""
        self.state = state
        self.last_updated = datetime.now()
        
    def attach_overlay(self, overlay_id: str):
        """Attach an overlay to this anchor."""
        if overlay_id not in self.attached_overlays:
            self.attached_overlays.append(overlay_id)
            
    def detach_overlay(self, overlay_id: str):
        """Detach an overlay from this anchor."""
        if overlay_id in self.attached_overlays:
            self.attached_overlays.remove(overlay_id)
            
    def to_dict(self) -> Dict:
        """Serialize anchor to dictionary."""
        return {
            "anchor_id": self.anchor_id,
            "type": self.anchor_type.value,
            "label": self.label,
            "position": self.position,
            "rotation": self.rotation,
            "state": self.state.value,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "persistent": self.persistent,
            "cloud_id": self.cloud_id,
            "attached_overlays": len(self.attached_overlays)
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "SpatialAnchor":
        """Create anchor from dictionary."""
        anchor = SpatialAnchor(
            anchor_id=data["anchor_id"],
            anchor_type=AnchorType(data["type"]),
            position=tuple(data["position"]),
            rotation=tuple(data["rotation"]),
            label=data.get("label")
        )
        anchor.state = AnchorState(data.get("state", "tracking"))
        anchor.confidence = data.get("confidence", 1.0)
        anchor.persistent = data.get("persistent", False)
        anchor.cloud_id = data.get("cloud_id")
        anchor.metadata = data.get("metadata", {})
        return anchor


class SpatialAnchorSystem:
    """
    Manages spatial anchors for AR/XR positioning.
    
    Provides:
    - World-space anchor creation and tracking
    - Plane and surface detection anchors
    - Persistent anchor storage and recall
    - Cloud anchor support for shared experiences
    - Semantic labeling of spatial locations
    """
    
    def __init__(self, xr_engine=None, persistence_path: str = "data/xr_anchors.json"):
        self.xr_engine = xr_engine
        self.persistence_path = persistence_path
        self.anchors: Dict[str, SpatialAnchor] = {}
        self.detected_planes: List[Dict] = []
        self.semantic_locations: Dict[str, str] = {}  # label -> anchor_id
        self._load_persistent_anchors()
        print("[SpatialAnchorSystem] Initialized.")
        
    def _load_persistent_anchors(self):
        """Load persistent anchors from storage."""
        if os.path.exists(self.persistence_path):
            try:
                with open(self.persistence_path, "r") as f:
                    data = json.load(f)
                    for anchor_data in data.get("anchors", []):
                        anchor = SpatialAnchor.from_dict(anchor_data)
                        anchor.state = AnchorState.PENDING  # Needs re-localization
                        self.anchors[anchor.anchor_id] = anchor
                    self.semantic_locations = data.get("semantic_locations", {})
                print(f"[SpatialAnchorSystem] Loaded {len(self.anchors)} persistent anchors")
            except Exception as e:
                print(f"[SpatialAnchorSystem] Failed to load anchors: {e}")
                
    def _save_persistent_anchors(self):
        """Save persistent anchors to storage."""
        persistent_anchors = [
            a.to_dict() for a in self.anchors.values() if a.persistent
        ]
        
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        with open(self.persistence_path, "w") as f:
            json.dump({
                "anchors": persistent_anchors,
                "semantic_locations": self.semantic_locations,
                "saved_at": datetime.now().isoformat()
            }, f, indent=2)
        print(f"[SpatialAnchorSystem] Saved {len(persistent_anchors)} persistent anchors")
        
    def create_anchor(
        self,
        position: Tuple[float, float, float],
        rotation: Tuple[float, float, float, float] = (0, 0, 0, 1),
        anchor_type: str = "point",
        label: Optional[str] = None,
        persistent: bool = False,
        metadata: Optional[Dict] = None
    ) -> SpatialAnchor:
        """
        Create a new spatial anchor.
        
        Args:
            position: World-space position (x, y, z)
            rotation: Quaternion rotation (x, y, z, w)
            anchor_type: Type of anchor
            label: Optional human-readable label
            persistent: Whether to persist across sessions
            metadata: Additional anchor metadata
            
        Returns:
            Created SpatialAnchor
        """
        anchor_id = f"anchor_{uuid.uuid4().hex[:8]}"
        atype = AnchorType(anchor_type.lower())
        
        anchor = SpatialAnchor(
            anchor_id=anchor_id,
            anchor_type=atype,
            position=position,
            rotation=rotation,
            label=label
        )
        anchor.persistent = persistent
        if metadata:
            anchor.metadata = metadata
            
        self.anchors[anchor_id] = anchor
        
        # Register semantic location if labeled
        if label:
            self.semantic_locations[label.lower()] = anchor_id
            
        # Notify XR engine
        if self.xr_engine and self.xr_engine.current_session:
            self.xr_engine.current_session.spatial_anchors.append(anchor_id)
            self.xr_engine.current_session.log_event("anchor_created", {
                "anchor_id": anchor_id,
                "type": atype.value,
                "label": label
            })
            
        # Save if persistent
        if persistent:
            self._save_persistent_anchors()
            
        print(f"[SpatialAnchorSystem] Created {atype.value} anchor: {anchor_id}" + 
              (f" ({label})" if label else ""))
        return anchor
    
    def create_plane_anchor(
        self,
        plane_type: str,
        center: Tuple[float, float, float],
        normal: Tuple[float, float, float],
        extents: Tuple[float, float],
        label: Optional[str] = None
    ) -> SpatialAnchor:
        """Create an anchor for a detected plane surface."""
        anchor = self.create_anchor(
            position=center,
            anchor_type="plane",
            label=label or f"{plane_type}_plane",
            metadata={
                "plane_type": plane_type,
                "normal": normal,
                "extents": extents
            }
        )
        return anchor
    
    def create_semantic_anchor(
        self,
        semantic_label: str,
        position: Tuple[float, float, float],
        persistent: bool = True
    ) -> SpatialAnchor:
        """Create a semantically labeled anchor (e.g., 'front door', 'workbench')."""
        return self.create_anchor(
            position=position,
            anchor_type="semantic",
            label=semantic_label,
            persistent=persistent,
            metadata={"semantic": True}
        )
    
    def get_anchor(self, anchor_id: str) -> Optional[SpatialAnchor]:
        """Get an anchor by ID."""
        return self.anchors.get(anchor_id)
    
    def get_anchor_by_label(self, label: str) -> Optional[SpatialAnchor]:
        """Get an anchor by its semantic label."""
        anchor_id = self.semantic_locations.get(label.lower())
        if anchor_id:
            return self.anchors.get(anchor_id)
        return None
    
    def update_anchor_pose(
        self,
        anchor_id: str,
        position: Tuple[float, float, float],
        rotation: Optional[Tuple[float, float, float, float]] = None,
        confidence: float = 1.0
    ) -> bool:
        """Update an anchor's tracked pose."""
        anchor = self.anchors.get(anchor_id)
        if not anchor:
            return False
            
        anchor.update_pose(position, rotation, confidence)
        
        # Update state based on confidence
        if confidence > 0.8:
            anchor.set_state(AnchorState.TRACKING)
        elif confidence > 0.4:
            anchor.set_state(AnchorState.LIMITED)
        else:
            anchor.set_state(AnchorState.NOT_TRACKING)
            
        return True
    
    def remove_anchor(self, anchor_id: str) -> bool:
        """Remove an anchor."""
        if anchor_id not in self.anchors:
            return False
            
        anchor = self.anchors[anchor_id]
        
        # Remove from semantic locations
        label_to_remove = None
        for label, aid in self.semantic_locations.items():
            if aid == anchor_id:
                label_to_remove = label
                break
        if label_to_remove:
            del self.semantic_locations[label_to_remove]
            
        # Remove from XR session
        if self.xr_engine and self.xr_engine.current_session:
            if anchor_id in self.xr_engine.current_session.spatial_anchors:
                self.xr_engine.current_session.spatial_anchors.remove(anchor_id)
                
        del self.anchors[anchor_id]
        
        # Update persistence
        if anchor.persistent:
            self._save_persistent_anchors()
            
        print(f"[SpatialAnchorSystem] Removed anchor: {anchor_id}")
        return True
    
    def list_anchors(self, state_filter: Optional[str] = None) -> List[Dict]:
        """List all anchors with optional state filter."""
        anchors = self.anchors.values()
        
        if state_filter:
            filter_state = AnchorState(state_filter.lower())
            anchors = [a for a in anchors if a.state == filter_state]
            
        return [a.to_dict() for a in anchors]
    
    def get_nearby_anchors(
        self,
        position: Tuple[float, float, float],
        radius: float = 5.0
    ) -> List[SpatialAnchor]:
        """Get anchors within a radius of a position."""
        nearby = []
        px, py, pz = position
        
        for anchor in self.anchors.values():
            ax, ay, az = anchor.position
            distance = ((px - ax)**2 + (py - ay)**2 + (pz - az)**2)**0.5
            if distance <= radius:
                nearby.append(anchor)
                
        return sorted(nearby, key=lambda a: (
            (px - a.position[0])**2 + 
            (py - a.position[1])**2 + 
            (pz - a.position[2])**2
        ))
    
    def get_semantic_locations(self) -> Dict[str, Tuple[float, float, float]]:
        """Get all semantic locations with their positions."""
        locations = {}
        for label, anchor_id in self.semantic_locations.items():
            anchor = self.anchors.get(anchor_id)
            if anchor:
                locations[label] = anchor.position
        return locations
    
    def process_plane_detection(self, planes_data: List[Dict]):
        """
        Process plane detection results from tracking system.
        
        Args:
            planes_data: List of detected planes with geometry info
        """
        self.detected_planes = planes_data
        
        for plane in planes_data:
            plane_id = plane.get("id")
            if not any(a.metadata.get("plane_id") == plane_id for a in self.anchors.values()):
                # New plane detected
                self.create_plane_anchor(
                    plane_type=plane.get("type", "horizontal"),
                    center=tuple(plane.get("center", [0, 0, 0])),
                    normal=tuple(plane.get("normal", [0, 1, 0])),
                    extents=tuple(plane.get("extents", [1, 1]))
                )
                
    def relocalize_persistent_anchors(self) -> int:
        """
        Attempt to relocalize persistent anchors.
        Called when environment is recognized.
        
        Returns:
            Number of anchors successfully relocalized
        """
        relocalized = 0
        for anchor in self.anchors.values():
            if anchor.persistent and anchor.state == AnchorState.PENDING:
                # In a real implementation, this would use visual features
                # to match and update anchor poses
                anchor.set_state(AnchorState.TRACKING)
                relocalized += 1
                
        print(f"[SpatialAnchorSystem] Relocalized {relocalized} persistent anchors")
        return relocalized
    
    def export_map(self) -> Dict:
        """Export spatial map data for sharing or backup."""
        return {
            "anchors": [a.to_dict() for a in self.anchors.values()],
            "semantic_locations": self.semantic_locations,
            "planes": self.detected_planes,
            "exported_at": datetime.now().isoformat()
        }
    
    def import_map(self, map_data: Dict, merge: bool = False) -> int:
        """
        Import spatial map data.
        
        Args:
            map_data: Exported map data
            merge: If True, merge with existing anchors
            
        Returns:
            Number of anchors imported
        """
        if not merge:
            self.anchors.clear()
            self.semantic_locations.clear()
            
        imported = 0
        for anchor_data in map_data.get("anchors", []):
            anchor = SpatialAnchor.from_dict(anchor_data)
            anchor.state = AnchorState.PENDING
            self.anchors[anchor.anchor_id] = anchor
            imported += 1
            
        self.semantic_locations.update(map_data.get("semantic_locations", {}))
        
        print(f"[SpatialAnchorSystem] Imported {imported} anchors")
        return imported
