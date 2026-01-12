# observer/integration.py
"""
Observer Integration
====================
Integrates the Observer module with existing daemon systems:
- memory_tree: Connects to MemoryLogger for event logging
- introspection: Connects to PersonalityTracker and ReflectionJournal
- scrolls: Provides triggers for memory-based automation
"""

import os
import sys
import threading
from typing import Dict, List, Optional, Any, Callable

# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from .observer_core import ObserverCore, get_observer
from .moment import Moment, MomentType, Significance
from .diary import DiaryEntry, EntryType


class ObserverIntegration:
    """
    Bridges the Observer with other daemon subsystems.
    """
    
    def __init__(self, observer: Optional[ObserverCore] = None):
        self.observer = observer or get_observer()
        self._memory_logger = None
        self._personality_tracker = None
        self._reflection_journal = None
        self._scroll_engine = None
        
        # Track what's connected
        self._connected_systems: List[str] = []
    
    def connect_memory_logger(self, memory_logger):
        """
        Connect to memory_tree.MemoryLogger.
        
        When moments are observed, they'll also be logged to the
        memory logger for compatibility with existing systems.
        """
        self._memory_logger = memory_logger
        
        # Register callback to log moments
        def on_moment(moment: Moment):
            try:
                self._memory_logger.log_event(
                    event_type=moment.moment_type.value,
                    content=moment.content,
                    context={
                        'moment_id': moment.id,
                        'significance': moment.significance.value,
                        'tags': moment.tags,
                        'emotion': moment.emotional_context.primary_emotion
                    }
                )
            except Exception as e:
                print(f"[ObserverIntegration] MemoryLogger error: {e}")
        
        self.observer.on_moment(on_moment)
        self._connected_systems.append('memory_logger')
        print("[ObserverIntegration] Connected to MemoryLogger")
    
    def connect_personality_tracker(self, personality_tracker):
        """
        Connect to introspection.PersonalityTracker.
        
        Emotional moments may influence personality traits over time.
        """
        self._personality_tracker = personality_tracker
        
        def on_moment(moment: Moment):
            # Only process emotional moments
            if moment.moment_type != MomentType.FEELING:
                return
            
            emotion = moment.emotional_context.primary_emotion
            if not emotion:
                return
            
            try:
                # Map emotions to personality traits
                trait_impacts = {
                    'joy': ('positivity', 0.01),
                    'sadness': ('sensitivity', 0.01),
                    'curiosity': ('openness', 0.01),
                    'anxiety': ('cautiousness', 0.01),
                    'peace': ('equanimity', 0.01),
                    'pride': ('confidence', 0.01),
                    'gratitude': ('appreciation', 0.01),
                }
                
                if emotion in trait_impacts:
                    trait, delta = trait_impacts[emotion]
                    current = self._personality_tracker.current_traits.get(trait, 0.5)
                    new_value = min(1.0, max(0.0, current + delta))
                    self._personality_tracker.log_trait_change(trait, new_value)
                    
            except Exception as e:
                print(f"[ObserverIntegration] PersonalityTracker error: {e}")
        
        self.observer.on_moment(on_moment)
        self._connected_systems.append('personality_tracker')
        print("[ObserverIntegration] Connected to PersonalityTracker")
    
    def connect_reflection_journal(self, reflection_journal):
        """
        Connect to introspection.ReflectionJournal.
        
        Significant diary entries are also written to the reflection journal.
        """
        self._reflection_journal = reflection_journal
        self._connected_systems.append('reflection_journal')
        print("[ObserverIntegration] Connected to ReflectionJournal")
    
    def sync_diary_to_journal(self, entry: DiaryEntry):
        """Sync a diary entry to the reflection journal."""
        if not self._reflection_journal:
            return
        
        try:
            self._reflection_journal.write_entry(
                title=entry.title or f"Diary: {entry.entry_type.value}",
                content=entry.to_markdown()
            )
        except Exception as e:
            print(f"[ObserverIntegration] ReflectionJournal error: {e}")
    
    def connect_scroll_engine(self, scroll_engine):
        """
        Connect to scrolls.ScrollEngine.
        
        Provides memory-based triggers for scroll automation.
        """
        self._scroll_engine = scroll_engine
        self._connected_systems.append('scroll_engine')
        print("[ObserverIntegration] Connected to ScrollEngine")
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            'connected_systems': self._connected_systems,
            'observer_active': self.observer.is_observing,
            'total_moments': len(self.observer.moments)
        }


class ObserverScrollTriggers:
    """
    Scroll triggers based on observer events.
    """
    
    def __init__(self, observer: ObserverCore, scroll_engine=None):
        self.observer = observer
        self.scroll_engine = scroll_engine
        self._registered_triggers: List[Dict[str, Any]] = []
    
    def on_moment_type(
        self,
        moment_type: MomentType,
        handler: Callable[[Moment], None],
        min_significance: Significance = Significance.MINOR
    ):
        """Trigger when a specific moment type is observed."""
        def callback(moment: Moment):
            if moment.moment_type == moment_type:
                if moment.significance.value >= min_significance.value:
                    handler(moment)
        
        self.observer.on_moment(callback)
        self._registered_triggers.append({
            'type': 'moment_type',
            'moment_type': moment_type.value,
            'min_significance': min_significance.value
        })
    
    def on_emotion(
        self,
        emotion: str,
        handler: Callable[[Moment], None]
    ):
        """Trigger when a specific emotion is observed."""
        def callback(moment: Moment):
            if moment.emotional_context.primary_emotion == emotion:
                handler(moment)
        
        self.observer.on_moment(callback)
        self._registered_triggers.append({
            'type': 'emotion',
            'emotion': emotion
        })
    
    def on_tag(
        self,
        tag: str,
        handler: Callable[[Moment], None]
    ):
        """Trigger when a moment with a specific tag is observed."""
        def callback(moment: Moment):
            if tag.lower() in [t.lower() for t in moment.tags]:
                handler(moment)
        
        self.observer.on_moment(callback)
        self._registered_triggers.append({
            'type': 'tag',
            'tag': tag
        })
    
    def on_significant_moment(
        self,
        handler: Callable[[Moment], None],
        min_significance: Significance = Significance.SIGNIFICANT
    ):
        """Trigger on any significant moment."""
        def callback(moment: Moment):
            if moment.significance.value >= min_significance.value:
                handler(moment)
        
        self.observer.on_moment(callback)
        self._registered_triggers.append({
            'type': 'significant',
            'min_significance': min_significance.value
        })


def setup_observer_integration(
    observer: Optional[ObserverCore] = None,
    memory_logger=None,
    personality_tracker=None,
    reflection_journal=None,
    scroll_engine=None
) -> ObserverIntegration:
    """
    Set up observer integration with all available subsystems.
    
    Args:
        observer: ObserverCore instance (uses global if None)
        memory_logger: MemoryLogger instance
        personality_tracker: PersonalityTracker instance
        reflection_journal: ReflectionJournal instance
        scroll_engine: ScrollEngine instance
        
    Returns:
        Configured ObserverIntegration
    """
    integration = ObserverIntegration(observer)
    
    if memory_logger:
        integration.connect_memory_logger(memory_logger)
    
    if personality_tracker:
        integration.connect_personality_tracker(personality_tracker)
    
    if reflection_journal:
        integration.connect_reflection_journal(reflection_journal)
    
    if scroll_engine:
        integration.connect_scroll_engine(scroll_engine)
    
    return integration


# NLU Command Handler for Observer
class ObserverCommandHandler:
    """
    Handles natural language commands for the observer.
    """
    
    COMMANDS = {
        'observe': ['observe', 'note', 'remember', 'record', 'noticed'],
        'insight': ['insight', 'realized', 'understood', 'aha'],
        'milestone': ['milestone', 'achieved', 'completed', 'finished'],
        'learned': ['learned', 'discovered', 'figured out'],
        'felt': ['felt', 'feeling', 'emotion'],
        'journal': ['journal', 'diary', 'write entry', 'dear diary'],
        'recall': ['recall', 'remember when', 'what was', 'search memory'],
        'garden': ['garden', 'memory garden', 'tend garden'],
        'palace': ['palace', 'mind palace', 'enter palace'],
        'gratitude': ['grateful', 'thankful', 'gratitude'],
    }
    
    def __init__(self, observer: Optional[ObserverCore] = None):
        self.observer = observer or get_observer()
    
    def can_handle(self, text: str) -> bool:
        """Check if this handler can process the text."""
        text_lower = text.lower()
        
        for command, keywords in self.COMMANDS.items():
            if any(kw in text_lower for kw in keywords):
                return True
        
        return False
    
    def handle(self, text: str) -> Optional[str]:
        """Handle an observer-related command."""
        text_lower = text.lower()
        
        # Observe/Note
        if any(kw in text_lower for kw in self.COMMANDS['observe']):
            # Extract content after the keyword
            content = self._extract_content(text, self.COMMANDS['observe'])
            if content:
                moment = self.observer.note(content)
                return f"[Observer] Noted: {moment.summary()}" if moment else "[Observer] Noted (below threshold)"
        
        # Insight
        if any(kw in text_lower for kw in self.COMMANDS['insight']):
            content = self._extract_content(text, self.COMMANDS['insight'])
            if content:
                moment = self.observer.insight(content)
                return f"[Observer] Insight recorded: {moment.summary()}" if moment else None
        
        # Milestone
        if any(kw in text_lower for kw in self.COMMANDS['milestone']):
            content = self._extract_content(text, self.COMMANDS['milestone'])
            if content:
                moment = self.observer.milestone(content)
                return f"[Observer] 🎉 Milestone: {moment.summary()}" if moment else None
        
        # Learned
        if any(kw in text_lower for kw in self.COMMANDS['learned']):
            content = self._extract_content(text, self.COMMANDS['learned'])
            if content:
                moment = self.observer.learned(content)
                return f"[Observer] Learning recorded: {moment.summary()}" if moment else None
        
        # Felt/Emotion
        if any(kw in text_lower for kw in self.COMMANDS['felt']):
            # Try to parse "felt [emotion]: [context]"
            import re
            match = re.search(r'felt?\s+(\w+):?\s*(.*)', text, re.IGNORECASE)
            if match:
                emotion = match.group(1)
                context = match.group(2) or "unspecified"
                moment = self.observer.felt(emotion, context)
                return f"[Observer] Emotion noted: {emotion}" if moment else None
        
        # Journal/Diary
        if any(kw in text_lower for kw in self.COMMANDS['journal']):
            content = self._extract_content(text, self.COMMANDS['journal'])
            if content:
                entry = self.observer.journal(content)
                return f"[Diary] Entry written: {entry.summary()}"
        
        # Recall/Search
        if any(kw in text_lower for kw in self.COMMANDS['recall']):
            query = self._extract_content(text, self.COMMANDS['recall'])
            if query:
                results = self.observer.search_memories(query)
                if results:
                    lines = [f"[Observer] Found {len(results)} memories:"]
                    for r in results[:5]:
                        lines.append(f"  - {r.get('summary', r.get('content', '')[:50])}")
                    return "\n".join(lines)
                return "[Observer] No memories found matching that query."
        
        # Garden
        if any(kw in text_lower for kw in self.COMMANDS['garden']):
            if 'tend' in text_lower:
                self.observer.tend_garden()
                return "[Observer] Garden tended."
            return self.observer.garden_view()
        
        # Palace
        if any(kw in text_lower for kw in self.COMMANDS['palace']):
            if 'enter' in text_lower:
                return self.observer.enter_palace()
            return self.observer.palace.describe_palace()
        
        # Gratitude
        if any(kw in text_lower for kw in self.COMMANDS['gratitude']):
            content = self._extract_content(text, self.COMMANDS['gratitude'])
            if content:
                # Parse comma-separated items
                items = [item.strip() for item in content.split(',')]
                entry = self.observer.gratitude(items)
                return f"[Diary] Gratitude recorded: {len(items)} items"
        
        return None
    
    def _extract_content(self, text: str, keywords: List[str]) -> str:
        """Extract content after a keyword."""
        text_lower = text.lower()
        
        for kw in keywords:
            idx = text_lower.find(kw)
            if idx >= 0:
                # Get text after keyword
                start = idx + len(kw)
                content = text[start:].strip()
                # Remove leading punctuation
                content = content.lstrip(':').strip()
                return content
        
        return text


def handle_observer_command(text: str) -> Optional[str]:
    """Convenience function to handle observer commands."""
    handler = ObserverCommandHandler()
    if handler.can_handle(text):
        return handler.handle(text)
    return None
