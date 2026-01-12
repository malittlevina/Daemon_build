# devices/wearables/__init__.py
"""
Wearable Device Interfaces
==========================
Interfaces for wearable and companion devices that the daemon
can observe through and interact with:

- Smart Ring: Biometrics, gestures, haptic feedback
- Smart Glasses: Visual input, AR overlay, audio
- Companion Robot: Physical presence, mobility, interaction
- Drone: Aerial observation, delivery, surveillance
"""

from .base_wearable import WearableDevice, WearableType, WearableCapability
from .smart_ring import SmartRing
from .smart_glasses import SmartGlasses
from .companion_robot import CompanionRobot
from .drone import Drone

__all__ = [
    'WearableDevice',
    'WearableType',
    'WearableCapability',
    'SmartRing',
    'SmartGlasses',
    'CompanionRobot',
    'Drone',
]
