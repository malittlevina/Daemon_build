# observer/__init__.py
"""
Observer Module
===============
Gives the daemon observational awareness - the ability to notice,
record, and remember significant moments, events, and experiences.

The daemon watches the flow of interactions and system events,
identifying what matters and nurturing those memories over time.

Components:
- Moment: A captured instant worth remembering
- MemoryGarden: Organic growth of memories over time
- MindPalace: Spatial organization for memory retrieval
- Diary: Personal reflection and entry recording
- ObserverCore: The central observer that coordinates everything
"""

from .moment import Moment, MomentType, Significance, EmotionalContext, create_moment
from .memory_garden import MemoryGarden, MemorySeed, MemoryFlower, GrowthStage, Season
from .mind_palace import MindPalace, Room, MemoryObject, RoomType
from .diary import Diary, DiaryEntry, EntryType, Mood
from .observer_core import ObserverCore, get_observer, observe, journal
from .integration import (
    ObserverIntegration,
    ObserverScrollTriggers,
    ObserverCommandHandler,
    setup_observer_integration,
    handle_observer_command
)

__all__ = [
    # Moment
    'Moment',
    'MomentType', 
    'Significance',
    'EmotionalContext',
    'create_moment',
    
    # Memory Garden
    'MemoryGarden',
    'MemorySeed',
    'MemoryFlower',
    'GrowthStage',
    'Season',
    
    # Mind Palace
    'MindPalace',
    'Room',
    'MemoryObject',
    'RoomType',
    
    # Diary
    'Diary',
    'DiaryEntry',
    'EntryType',
    'Mood',
    
    # Core
    'ObserverCore',
    'get_observer',
    'observe',
    'journal',
    
    # Integration
    'ObserverIntegration',
    'ObserverScrollTriggers',
    'ObserverCommandHandler',
    'setup_observer_integration',
    'handle_observer_command',
]
