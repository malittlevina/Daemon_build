# xr/__init__.py
# AR/XR Subsystem for ThothOS Daemon (Prometheus)

from xr.xr_engine import XREngine
from xr.ar_overlay import AROverlayManager
from xr.spatial_anchor import SpatialAnchorSystem
from xr.xr_training import XRTrainingModule
from xr.gesture_interface import GestureInterface

__all__ = [
    "XREngine",
    "AROverlayManager", 
    "SpatialAnchorSystem",
    "XRTrainingModule",
    "GestureInterface"
]
