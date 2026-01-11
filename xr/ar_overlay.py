# xr/ar_overlay.py
# AR Overlay Manager - Handles augmented reality visual overlays and projections

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import uuid


class OverlayType(Enum):
    """Types of AR overlays supported."""
    TEXT = "text"                    # Text labels and information panels
    IMAGE = "image"                  # 2D image overlays
    MODEL_3D = "model_3d"            # 3D model overlays
    VIDEO = "video"                  # Video panels
    WIDGET = "widget"                # Interactive UI widgets
    HIGHLIGHT = "highlight"          # Object highlighting/outlining
    WAYPOINT = "waypoint"            # Navigation waypoints
    ANNOTATION = "annotation"        # Contextual annotations
    HUD = "hud"                      # Head-up display elements
    HOLOGRAM = "hologram"            # Holographic projections


class OverlayAnchorMode(Enum):
    """How an overlay is positioned in space."""
    WORLD_LOCKED = "world_locked"    # Fixed in world space
    HEAD_LOCKED = "head_locked"      # Follows user's head/view
    SURFACE = "surface"              # Attached to detected surface
    OBJECT = "object"                # Attached to tracked object
    HAND = "hand"                    # Attached to user's hand


class AROverlay:
    """Represents a single AR overlay element."""
    
    def __init__(
        self,
        overlay_id: str,
        overlay_type: OverlayType,
        anchor_mode: OverlayAnchorMode,
        content: Any,
        position: Tuple[float, float, float] = (0, 0, 0),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        scale: Tuple[float, float, float] = (1, 1, 1)
    ):
        self.overlay_id = overlay_id
        self.overlay_type = overlay_type
        self.anchor_mode = anchor_mode
        self.content = content
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.is_visible = True
        self.opacity = 1.0
        self.created_at = datetime.now()
        self.metadata: Dict[str, Any] = {}
        self.interactions: List[Dict] = []
        
    def update_transform(
        self,
        position: Optional[Tuple[float, float, float]] = None,
        rotation: Optional[Tuple[float, float, float]] = None,
        scale: Optional[Tuple[float, float, float]] = None
    ):
        """Update overlay position, rotation, and scale."""
        if position:
            self.position = position
        if rotation:
            self.rotation = rotation
        if scale:
            self.scale = scale
            
    def set_visibility(self, visible: bool, opacity: float = 1.0):
        """Set overlay visibility and opacity."""
        self.is_visible = visible
        self.opacity = max(0.0, min(1.0, opacity))
        
    def log_interaction(self, interaction_type: str, data: Dict):
        """Log user interaction with this overlay."""
        self.interactions.append({
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "data": data
        })
        
    def to_dict(self) -> Dict:
        """Serialize overlay to dictionary."""
        return {
            "overlay_id": self.overlay_id,
            "type": self.overlay_type.value,
            "anchor_mode": self.anchor_mode.value,
            "content": str(self.content)[:100],  # Truncate for summary
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale,
            "is_visible": self.is_visible,
            "opacity": self.opacity,
            "created_at": self.created_at.isoformat(),
            "interaction_count": len(self.interactions)
        }


class AROverlayManager:
    """
    Manages AR overlays for the daemon's XR subsystem.
    
    Provides capabilities for:
    - Creating and managing visual overlays in AR space
    - Information panels and contextual annotations
    - Training scenario visualizations
    - Interactive holographic interfaces
    """
    
    def __init__(self, xr_engine=None):
        self.xr_engine = xr_engine
        self.overlays: Dict[str, AROverlay] = {}
        self.overlay_groups: Dict[str, List[str]] = {}
        self.templates: Dict[str, Dict] = self._load_templates()
        print("[AROverlayManager] Initialized.")
        
    def _load_templates(self) -> Dict[str, Dict]:
        """Load predefined overlay templates."""
        return {
            "info_panel": {
                "type": OverlayType.TEXT,
                "anchor_mode": OverlayAnchorMode.WORLD_LOCKED,
                "default_scale": (0.5, 0.3, 0.01),
                "style": {"background": "rgba(0,0,0,0.7)", "text_color": "white"}
            },
            "waypoint_marker": {
                "type": OverlayType.WAYPOINT,
                "anchor_mode": OverlayAnchorMode.WORLD_LOCKED,
                "default_scale": (0.2, 0.2, 0.2),
                "style": {"color": "cyan", "pulsing": True}
            },
            "training_highlight": {
                "type": OverlayType.HIGHLIGHT,
                "anchor_mode": OverlayAnchorMode.OBJECT,
                "default_scale": (1, 1, 1),
                "style": {"outline_color": "yellow", "outline_width": 3}
            },
            "hud_status": {
                "type": OverlayType.HUD,
                "anchor_mode": OverlayAnchorMode.HEAD_LOCKED,
                "default_scale": (0.3, 0.1, 0.01),
                "style": {"position": "top-right", "opacity": 0.8}
            },
            "hologram_assistant": {
                "type": OverlayType.HOLOGRAM,
                "anchor_mode": OverlayAnchorMode.WORLD_LOCKED,
                "default_scale": (0.5, 0.5, 0.5),
                "style": {"emission": True, "scanlines": True}
            },
            "hand_menu": {
                "type": OverlayType.WIDGET,
                "anchor_mode": OverlayAnchorMode.HAND,
                "default_scale": (0.15, 0.15, 0.01),
                "style": {"curved": True, "follow_palm": True}
            }
        }
    
    def create_overlay(
        self,
        overlay_type: str,
        content: Any,
        position: Tuple[float, float, float] = (0, 0, 1),
        anchor_mode: str = "world_locked",
        template: Optional[str] = None,
        group: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> AROverlay:
        """
        Create a new AR overlay.
        
        Args:
            overlay_type: Type of overlay (text, image, model_3d, etc.)
            content: Content to display (text, path to asset, etc.)
            position: 3D position in world space
            anchor_mode: How the overlay is anchored
            template: Optional template name to use
            group: Optional group to add overlay to
            metadata: Optional metadata dictionary
            
        Returns:
            Created AROverlay instance
        """
        # Parse enums
        otype = OverlayType(overlay_type.lower())
        amode = OverlayAnchorMode(anchor_mode.lower())
        
        # Apply template if specified
        scale = (1, 1, 1)
        if template and template in self.templates:
            tmpl = self.templates[template]
            otype = tmpl.get("type", otype)
            amode = tmpl.get("anchor_mode", amode)
            scale = tmpl.get("default_scale", scale)
        
        # Generate unique ID
        overlay_id = f"overlay_{uuid.uuid4().hex[:8]}"
        
        # Create overlay
        overlay = AROverlay(
            overlay_id=overlay_id,
            overlay_type=otype,
            anchor_mode=amode,
            content=content,
            position=position,
            scale=scale
        )
        
        if metadata:
            overlay.metadata = metadata
            
        # Store overlay
        self.overlays[overlay_id] = overlay
        
        # Add to group if specified
        if group:
            if group not in self.overlay_groups:
                self.overlay_groups[group] = []
            self.overlay_groups[group].append(overlay_id)
            
        # Notify XR engine if connected
        if self.xr_engine and self.xr_engine.current_session:
            self.xr_engine.current_session.overlays.append(overlay_id)
            self.xr_engine.current_session.log_event("overlay_created", {
                "overlay_id": overlay_id,
                "type": otype.value
            })
            
        print(f"[AROverlayManager] Created {otype.value} overlay: {overlay_id}")
        return overlay
    
    def create_info_panel(
        self,
        text: str,
        title: Optional[str] = None,
        position: Tuple[float, float, float] = (0, 1.5, 2)
    ) -> AROverlay:
        """Create an information panel overlay."""
        content = {"title": title, "text": text} if title else text
        return self.create_overlay(
            overlay_type="text",
            content=content,
            position=position,
            template="info_panel",
            group="info_panels"
        )
    
    def create_waypoint(
        self,
        label: str,
        position: Tuple[float, float, float],
        color: str = "cyan"
    ) -> AROverlay:
        """Create a navigation waypoint marker."""
        overlay = self.create_overlay(
            overlay_type="waypoint",
            content=label,
            position=position,
            template="waypoint_marker",
            group="waypoints",
            metadata={"color": color}
        )
        return overlay
    
    def create_training_highlight(
        self,
        target_object: str,
        instruction: str,
        position: Tuple[float, float, float]
    ) -> AROverlay:
        """Create a training highlight overlay for an object."""
        return self.create_overlay(
            overlay_type="highlight",
            content={"target": target_object, "instruction": instruction},
            position=position,
            template="training_highlight",
            group="training"
        )
    
    def create_hologram(
        self,
        model_ref: str,
        position: Tuple[float, float, float] = (0, 0, 2),
        scale: float = 1.0
    ) -> AROverlay:
        """Create a holographic projection overlay."""
        overlay = self.create_overlay(
            overlay_type="hologram",
            content=model_ref,
            position=position,
            template="hologram_assistant",
            group="holograms"
        )
        overlay.scale = (scale, scale, scale)
        return overlay
    
    def create_hud_element(
        self,
        content: str,
        hud_position: str = "top-right"
    ) -> AROverlay:
        """Create a HUD (head-up display) element."""
        overlay = self.create_overlay(
            overlay_type="hud",
            content=content,
            position=(0, 0, 0),  # HUD elements use screen-space positioning
            anchor_mode="head_locked",
            template="hud_status",
            group="hud",
            metadata={"hud_position": hud_position}
        )
        return overlay
    
    def get_overlay(self, overlay_id: str) -> Optional[AROverlay]:
        """Get an overlay by ID."""
        return self.overlays.get(overlay_id)
    
    def update_overlay(
        self,
        overlay_id: str,
        content: Optional[Any] = None,
        position: Optional[Tuple[float, float, float]] = None,
        visible: Optional[bool] = None,
        opacity: Optional[float] = None
    ) -> bool:
        """Update an existing overlay."""
        overlay = self.overlays.get(overlay_id)
        if not overlay:
            print(f"[AROverlayManager] Overlay not found: {overlay_id}")
            return False
            
        if content is not None:
            overlay.content = content
        if position is not None:
            overlay.update_transform(position=position)
        if visible is not None:
            overlay.set_visibility(visible, opacity or overlay.opacity)
        elif opacity is not None:
            overlay.set_visibility(overlay.is_visible, opacity)
            
        print(f"[AROverlayManager] Updated overlay: {overlay_id}")
        return True
    
    def remove_overlay(self, overlay_id: str) -> bool:
        """Remove an overlay."""
        if overlay_id not in self.overlays:
            return False
            
        # Remove from groups
        for group_ids in self.overlay_groups.values():
            if overlay_id in group_ids:
                group_ids.remove(overlay_id)
                
        # Remove from XR session if active
        if self.xr_engine and self.xr_engine.current_session:
            if overlay_id in self.xr_engine.current_session.overlays:
                self.xr_engine.current_session.overlays.remove(overlay_id)
                
        del self.overlays[overlay_id]
        print(f"[AROverlayManager] Removed overlay: {overlay_id}")
        return True
    
    def clear_group(self, group: str) -> int:
        """Remove all overlays in a group."""
        if group not in self.overlay_groups:
            return 0
            
        overlay_ids = self.overlay_groups[group].copy()
        for overlay_id in overlay_ids:
            self.remove_overlay(overlay_id)
            
        del self.overlay_groups[group]
        print(f"[AROverlayManager] Cleared group '{group}': {len(overlay_ids)} overlays removed")
        return len(overlay_ids)
    
    def clear_all(self) -> int:
        """Remove all overlays."""
        count = len(self.overlays)
        self.overlays.clear()
        self.overlay_groups.clear()
        print(f"[AROverlayManager] Cleared all overlays: {count} removed")
        return count
    
    def get_visible_overlays(self) -> List[AROverlay]:
        """Get all currently visible overlays."""
        return [o for o in self.overlays.values() if o.is_visible]
    
    def get_group_overlays(self, group: str) -> List[AROverlay]:
        """Get all overlays in a specific group."""
        if group not in self.overlay_groups:
            return []
        return [self.overlays[oid] for oid in self.overlay_groups[group] if oid in self.overlays]
    
    def list_overlays(self) -> List[Dict]:
        """List all overlays with summary information."""
        return [o.to_dict() for o in self.overlays.values()]
    
    def get_render_queue(self) -> List[Dict]:
        """
        Get the render queue for visible overlays.
        Used by XR rendering loop.
        """
        queue = []
        for overlay in self.get_visible_overlays():
            queue.append({
                "id": overlay.overlay_id,
                "type": overlay.overlay_type.value,
                "anchor": overlay.anchor_mode.value,
                "transform": {
                    "position": overlay.position,
                    "rotation": overlay.rotation,
                    "scale": overlay.scale
                },
                "opacity": overlay.opacity,
                "content": overlay.content,
                "metadata": overlay.metadata
            })
        return queue
