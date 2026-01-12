# observer/moment.py
"""
Moment - A Captured Instant
===========================
Represents a significant moment that the daemon has observed and
decided is worth remembering. Moments can be events, realizations,
interactions, or any experience with emotional or practical weight.
"""

import time
import uuid
import json
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime


class MomentType(Enum):
    """Categories of observable moments."""
    # Interactions
    CONVERSATION = "conversation"      # Meaningful dialogue
    QUESTION = "question"              # Important question asked
    ANSWER = "answer"                  # Significant answer given
    INSIGHT = "insight"                # New understanding reached
    
    # Events
    EVENT = "event"                    # Something happened
    MILESTONE = "milestone"            # Achievement or progress marker
    DISCOVERY = "discovery"            # Found something new
    ERROR = "error"                    # Something went wrong (learn from it)
    RECOVERY = "recovery"              # Recovered from a problem
    
    # Personal
    REFLECTION = "reflection"          # Self-contemplation
    REALIZATION = "realization"        # Sudden understanding
    FEELING = "feeling"                # Emotional state worth noting
    DECISION = "decision"              # Choice that was made
    
    # System
    SYSTEM_EVENT = "system_event"      # System-level occurrence
    DEVICE_EVENT = "device_event"      # Device connected/detected
    PATTERN = "pattern"                # Recognized pattern
    ANOMALY = "anomaly"                # Something unusual
    
    # External
    OBSERVATION = "observation"        # Noticed something in environment
    NEWS = "news"                      # External information received
    REMINDER = "reminder"              # Something to remember for later


class Significance(Enum):
    """How significant/important a moment is."""
    FLEETING = 1      # Barely worth noting, may fade
    MINOR = 2         # Small but notable
    MODERATE = 3      # Worth remembering
    SIGNIFICANT = 4   # Important, should be preserved
    PROFOUND = 5      # Life-changing, never forget


@dataclass
class EmotionalContext:
    """Emotional state surrounding a moment."""
    valence: float = 0.0        # -1 (negative) to +1 (positive)
    arousal: float = 0.0        # 0 (calm) to 1 (excited)
    dominance: float = 0.5      # 0 (submissive) to 1 (dominant)
    primary_emotion: Optional[str] = None  # joy, sadness, curiosity, etc.
    secondary_emotions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EmotionalContext':
        return cls(**data)


@dataclass
class Moment:
    """
    A captured instant - something the daemon observed and found
    worth remembering.
    """
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Core content
    content: str = ""                  # What happened / the memory itself
    moment_type: MomentType = MomentType.EVENT
    significance: Significance = Significance.MODERATE
    
    # Temporal
    timestamp: float = field(default_factory=time.time)
    duration_seconds: Optional[float] = None  # How long it lasted
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    emotional_context: EmotionalContext = field(default_factory=EmotionalContext)
    
    # Relationships
    related_moments: List[str] = field(default_factory=list)  # IDs of related moments
    triggered_by: Optional[str] = None  # What caused this moment
    source: Optional[str] = None        # Where it came from (user, system, etc.)
    
    # Memory dynamics
    recall_count: int = 0              # How often this has been recalled
    last_recalled: Optional[float] = None
    strength: float = 1.0              # Memory strength (decays over time)
    consolidated: bool = False         # Has been processed into long-term memory
    
    # Location in Mind Palace (optional)
    palace_room: Optional[str] = None
    palace_position: Optional[Dict[str, float]] = None
    
    # Garden metaphor
    planted_at: Optional[float] = None  # When planted in garden
    growth_stage: int = 0               # 0=seed, 1=sprout, 2=growing, 3=flowering, 4=fruit
    
    def __post_init__(self):
        if isinstance(self.moment_type, str):
            self.moment_type = MomentType(self.moment_type)
        if isinstance(self.significance, int):
            self.significance = Significance(self.significance)
        if isinstance(self.emotional_context, dict):
            self.emotional_context = EmotionalContext.from_dict(self.emotional_context)
    
    @property
    def datetime(self) -> datetime:
        """Get timestamp as datetime."""
        return datetime.fromtimestamp(self.timestamp)
    
    @property
    def age_seconds(self) -> float:
        """How old is this moment in seconds."""
        return time.time() - self.timestamp
    
    @property
    def age_days(self) -> float:
        """How old is this moment in days."""
        return self.age_seconds / 86400
    
    def recall(self):
        """Mark this moment as recalled, strengthening the memory."""
        self.recall_count += 1
        self.last_recalled = time.time()
        # Recalling strengthens memory
        self.strength = min(1.0, self.strength + 0.1)
    
    def decay(self, factor: float = 0.99):
        """Apply memory decay over time."""
        # Significance affects decay rate
        decay_modifier = 1.0 - (self.significance.value * 0.05)
        self.strength *= (factor * decay_modifier)
        
        # Consolidated memories decay slower
        if self.consolidated:
            self.strength = max(0.5, self.strength)
    
    def to_dict(self) -> dict:
        """Serialize moment to dictionary."""
        data = asdict(self)
        data['moment_type'] = self.moment_type.value
        data['significance'] = self.significance.value
        data['emotional_context'] = self.emotional_context.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Moment':
        """Deserialize moment from dictionary."""
        data['moment_type'] = MomentType(data['moment_type'])
        data['significance'] = Significance(data['significance'])
        data['emotional_context'] = EmotionalContext.from_dict(data['emotional_context'])
        return cls(**data)
    
    def summary(self) -> str:
        """Get a brief summary of this moment."""
        type_str = self.moment_type.value.replace('_', ' ').title()
        sig_stars = '★' * self.significance.value
        age = self.age_days
        
        if age < 1:
            age_str = f"{int(self.age_seconds / 3600)}h ago"
        elif age < 7:
            age_str = f"{int(age)}d ago"
        else:
            age_str = self.datetime.strftime("%b %d")
        
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        
        return f"[{type_str}] {sig_stars} {preview} ({age_str})"
    
    def __str__(self):
        return self.summary()


def create_moment(
    content: str,
    moment_type: MomentType = MomentType.EVENT,
    significance: Significance = Significance.MODERATE,
    tags: Optional[List[str]] = None,
    context: Optional[Dict[str, Any]] = None,
    source: Optional[str] = None,
    emotion: Optional[str] = None,
    valence: float = 0.0
) -> Moment:
    """
    Convenience function to create a moment.
    
    Args:
        content: What happened
        moment_type: Category of moment
        significance: How important (1-5)
        tags: Optional tags for categorization
        context: Optional additional context
        source: Where this came from
        emotion: Primary emotion if any
        valence: Positive/negative (-1 to 1)
    
    Returns:
        New Moment instance
    """
    emotional_context = EmotionalContext(
        valence=valence,
        primary_emotion=emotion
    )
    
    return Moment(
        content=content,
        moment_type=moment_type,
        significance=significance,
        tags=tags or [],
        context=context or {},
        source=source,
        emotional_context=emotional_context
    )
