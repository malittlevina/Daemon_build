# observer/observer_core.py
"""
Observer Core
=============
The daemon's observational awareness system.

The Observer watches the flow of events, interactions, and experiences,
deciding what's worth remembering and nurturing those memories over time.
It integrates the Memory Garden and Mind Palace to create a rich,
navigable landscape of preserved experiences.
"""

import os
import json
import time
import threading
import re
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, date

from .moment import Moment, MomentType, Significance, EmotionalContext, create_moment
from .memory_garden import MemoryGarden, GrowthStage
from .mind_palace import MindPalace
from .diary import Diary, DiaryEntry, EntryType, Mood


class ObserverCore:
    """
    The Observer - the daemon's awareness and memory system.
    
    Watches for significant moments, records them in the garden
    and palace, maintains the diary, and enables review of past
    experiences.
    """
    
    # Keywords that suggest significance
    SIGNIFICANCE_KEYWORDS = {
        'high': [
            'important', 'critical', 'crucial', 'milestone', 'achievement',
            'breakthrough', 'realized', 'discovered', 'learned', 'never forget',
            'remember this', 'significant', 'meaningful', 'profound'
        ],
        'medium': [
            'interesting', 'notable', 'noticed', 'observed', 'felt',
            'thought', 'idea', 'insight', 'pattern', 'connection'
        ],
        'low': [
            'maybe', 'perhaps', 'minor', 'small', 'brief', 'quick'
        ]
    }
    
    # Emotional indicators
    EMOTION_PATTERNS = {
        'joy': ['happy', 'joy', 'excited', 'wonderful', 'amazing', 'love', 'great'],
        'sadness': ['sad', 'disappointed', 'upset', 'miss', 'lost', 'regret'],
        'curiosity': ['curious', 'wonder', 'interesting', 'fascinating', 'intriguing'],
        'gratitude': ['grateful', 'thankful', 'appreciate', 'blessed'],
        'anxiety': ['worried', 'anxious', 'nervous', 'uncertain', 'afraid'],
        'peace': ['calm', 'peaceful', 'serene', 'relaxed', 'content'],
        'pride': ['proud', 'accomplished', 'achieved', 'succeeded'],
    }
    
    def __init__(self, observer_path: str = "observer"):
        self.observer_path = observer_path
        self.state_file = os.path.join(observer_path, "observer_state.json")
        
        os.makedirs(observer_path, exist_ok=True)
        
        # Initialize subsystems
        self.garden = MemoryGarden(os.path.join(observer_path, "garden"))
        self.palace = MindPalace(os.path.join(observer_path, "palace"))
        self.diary = Diary(os.path.join(observer_path, "diary"))
        
        # All moments (indexed for quick access)
        self.moments: Dict[str, Moment] = {}
        self.moments_file = os.path.join(observer_path, "moments.json")
        
        # Observer state
        self.is_observing = False
        self.observation_count = 0
        self.last_observation: Optional[float] = None
        
        # Importance threshold (moments below this are not persisted)
        self.significance_threshold = Significance.MINOR
        
        # Event callbacks
        self._moment_callbacks: List[Callable[[Moment], None]] = []
        
        # Background processing
        self._background_thread: Optional[threading.Thread] = None
        self._background_active = False
        
        self._load_state()
        
        print(f"[Observer] Awakened. Watching for moments worth remembering.")
    
    def _load_state(self):
        """Load observer state and moments."""
        if os.path.exists(self.moments_file):
            try:
                with open(self.moments_file, 'r') as f:
                    data = json.load(f)
                    for moment_data in data.get('moments', []):
                        moment = Moment.from_dict(moment_data)
                        self.moments[moment.id] = moment
                        
                        # Also add to garden/palace moment stores
                        self.garden.moments[moment.id] = moment
                        self.palace.moments[moment.id] = moment
                        
            except Exception as e:
                print(f"[Observer] Error loading moments: {e}")
        
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.observation_count = state.get('observation_count', 0)
                    self.last_observation = state.get('last_observation')
            except Exception as e:
                print(f"[Observer] Error loading state: {e}")
    
    def _save_state(self):
        """Save observer state and moments."""
        try:
            # Save moments
            with open(self.moments_file, 'w') as f:
                data = {
                    'moments': [m.to_dict() for m in self.moments.values()],
                    'total': len(self.moments),
                    'last_saved': time.time()
                }
                json.dump(data, f, indent=2)
            
            # Save state
            with open(self.state_file, 'w') as f:
                state = {
                    'observation_count': self.observation_count,
                    'last_observation': self.last_observation,
                    'is_observing': self.is_observing,
                    'total_moments': len(self.moments)
                }
                json.dump(state, f, indent=2)
                
        except Exception as e:
            print(f"[Observer] Error saving state: {e}")
    
    def on_moment(self, callback: Callable[[Moment], None]):
        """Register a callback for new moments."""
        self._moment_callbacks.append(callback)
    
    def _emit_moment(self, moment: Moment):
        """Emit a moment to all callbacks."""
        for callback in self._moment_callbacks:
            try:
                callback(moment)
            except Exception as e:
                print(f"[Observer] Callback error: {e}")
    
    # ================
    # Observation APIs
    # ================
    
    def observe(
        self,
        content: str,
        moment_type: MomentType = MomentType.OBSERVATION,
        significance: Optional[Significance] = None,
        source: str = "user",
        tags: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        emotion: Optional[str] = None
    ) -> Optional[Moment]:
        """
        Observe and potentially record a moment.
        
        This is the primary API for recording observations.
        The observer will analyze the content and decide if
        it's worth remembering.
        
        Args:
            content: What happened / what was observed
            moment_type: Category of observation
            significance: Importance (auto-detected if None)
            source: Where this came from
            tags: Optional categorization tags
            context: Additional context
            emotion: Primary emotion if known
            
        Returns:
            The created Moment, or None if below threshold
        """
        # Auto-detect significance if not provided
        if significance is None:
            significance = self._detect_significance(content)
        
        # Check threshold
        if significance.value < self.significance_threshold.value:
            return None
        
        # Detect emotion if not provided
        if emotion is None:
            emotion = self._detect_emotion(content)
        
        # Create the moment
        moment = create_moment(
            content=content,
            moment_type=moment_type,
            significance=significance,
            tags=tags or self._extract_tags(content),
            context=context or {},
            source=source,
            emotion=emotion,
            valence=self._calculate_valence(emotion)
        )
        
        # Store the moment
        self.moments[moment.id] = moment
        self.observation_count += 1
        self.last_observation = time.time()
        
        # Plant in garden
        self.garden.plant(moment)
        
        # Place in mind palace
        self.palace.place_memory(moment)
        
        # Save state
        self._save_state()
        
        # Emit to callbacks
        self._emit_moment(moment)
        
        print(f"[Observer] Moment captured: {moment.summary()}")
        
        return moment
    
    def _detect_significance(self, content: str) -> Significance:
        """Analyze content to determine significance level."""
        content_lower = content.lower()
        
        # Check for high significance keywords
        for keyword in self.SIGNIFICANCE_KEYWORDS['high']:
            if keyword in content_lower:
                return Significance.SIGNIFICANT
        
        # Check for medium significance
        for keyword in self.SIGNIFICANCE_KEYWORDS['medium']:
            if keyword in content_lower:
                return Significance.MODERATE
        
        # Check for low significance
        for keyword in self.SIGNIFICANCE_KEYWORDS['low']:
            if keyword in content_lower:
                return Significance.MINOR
        
        # Default to moderate
        return Significance.MODERATE
    
    def _detect_emotion(self, content: str) -> Optional[str]:
        """Detect primary emotion from content."""
        content_lower = content.lower()
        
        emotion_scores = {}
        for emotion, keywords in self.EMOTION_PATTERNS.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        
        return None
    
    def _calculate_valence(self, emotion: Optional[str]) -> float:
        """Calculate emotional valence from emotion."""
        if not emotion:
            return 0.0
        
        valence_map = {
            'joy': 0.8,
            'gratitude': 0.7,
            'pride': 0.6,
            'peace': 0.5,
            'curiosity': 0.3,
            'anxiety': -0.3,
            'sadness': -0.6,
        }
        
        return valence_map.get(emotion, 0.0)
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract potential tags from content."""
        tags = []
        
        # Look for hashtags
        hashtags = re.findall(r'#(\w+)', content)
        tags.extend(hashtags)
        
        # Look for quoted phrases
        quoted = re.findall(r'"([^"]+)"', content)
        for phrase in quoted:
            if len(phrase.split()) <= 3:
                tags.append(phrase.lower())
        
        return tags[:5]  # Limit to 5 tags
    
    # ===============
    # Quick Observers
    # ===============
    
    def note(self, content: str) -> Optional[Moment]:
        """Quick note - a brief observation."""
        return self.observe(
            content=content,
            moment_type=MomentType.OBSERVATION,
            significance=Significance.MINOR
        )
    
    def insight(self, content: str) -> Optional[Moment]:
        """Record an insight or realization."""
        return self.observe(
            content=content,
            moment_type=MomentType.INSIGHT,
            significance=Significance.SIGNIFICANT
        )
    
    def milestone(self, content: str) -> Optional[Moment]:
        """Record a milestone or achievement."""
        return self.observe(
            content=content,
            moment_type=MomentType.MILESTONE,
            significance=Significance.PROFOUND
        )
    
    def learned(self, content: str) -> Optional[Moment]:
        """Record something learned."""
        moment = self.observe(
            content=content,
            moment_type=MomentType.DISCOVERY,
            significance=Significance.SIGNIFICANT,
            tags=['learning', 'growth']
        )
        
        # Also record in diary as a lesson
        if moment:
            self.diary.write_lesson(content)
        
        return moment
    
    def felt(self, emotion: str, context: str) -> Optional[Moment]:
        """Record an emotional moment."""
        return self.observe(
            content=f"Felt {emotion}: {context}",
            moment_type=MomentType.FEELING,
            emotion=emotion.lower()
        )
    
    def pattern(self, content: str) -> Optional[Moment]:
        """Record a recognized pattern."""
        return self.observe(
            content=content,
            moment_type=MomentType.PATTERN,
            significance=Significance.SIGNIFICANT,
            tags=['pattern', 'recognition']
        )
    
    def error_learned(self, error: str, lesson: str) -> Optional[Moment]:
        """Record an error and what was learned from it."""
        return self.observe(
            content=f"Error: {error}\nLesson: {lesson}",
            moment_type=MomentType.ERROR,
            significance=Significance.SIGNIFICANT,
            tags=['error', 'learning', 'growth']
        )
    
    # =============
    # Diary Methods
    # =============
    
    def journal(
        self,
        content: str,
        title: Optional[str] = None,
        mood: Optional[str] = None
    ) -> DiaryEntry:
        """Write a diary entry."""
        mood_enum = None
        if mood:
            try:
                mood_enum = Mood(mood.lower())
            except ValueError:
                pass
        
        return self.diary.write(
            content=content,
            title=title,
            mood=mood_enum
        )
    
    def daily_reflection(
        self,
        content: str,
        mood: Optional[str] = None,
        gratitude: Optional[List[str]] = None
    ) -> DiaryEntry:
        """Write daily reflection."""
        mood_enum = Mood(mood.lower()) if mood else None
        return self.diary.write_daily(content, mood_enum, gratitude)
    
    def gratitude(self, items: List[str]) -> DiaryEntry:
        """Record gratitude."""
        return self.diary.write_gratitude(items)
    
    def get_prompt(self, category: str = 'reflection') -> str:
        """Get a reflection prompt."""
        return self.diary.get_prompt(category)
    
    def respond_to_prompt(self, prompt: str, response: str) -> DiaryEntry:
        """Respond to a reflection prompt."""
        return self.diary.respond_to_prompt(prompt, response)
    
    # ================
    # Recall & Review
    # ================
    
    def recall(self, moment_id: str) -> Optional[Moment]:
        """Recall a specific moment (strengthens memory)."""
        moment = self.moments.get(moment_id)
        if moment:
            moment.recall()
            self.garden.water(moment_id)
            self._save_state()
            return moment
        return None
    
    def search_memories(self, query: str) -> List[Dict[str, Any]]:
        """Search through all memories."""
        results = []
        query_lower = query.lower()
        
        # Search moments
        for moment in self.moments.values():
            if query_lower in moment.content.lower():
                results.append({
                    'type': 'moment',
                    'id': moment.id,
                    'content': moment.content,
                    'summary': moment.summary(),
                    'significance': moment.significance.name
                })
            elif any(query_lower in tag.lower() for tag in moment.tags):
                results.append({
                    'type': 'moment',
                    'id': moment.id,
                    'content': moment.content,
                    'summary': moment.summary(),
                    'significance': moment.significance.name
                })
        
        # Search diary
        for entry in self.diary.search(query):
            results.append({
                'type': 'diary',
                'id': entry.id,
                'content': entry.content,
                'summary': entry.summary(),
                'date': entry.entry_date
            })
        
        # Search mind palace
        palace_results = self.palace.search(query)
        for r in palace_results:
            results.append({
                'type': 'palace',
                'room': r['room'],
                'object': r['object'],
                'summary': r['moment']
            })
        
        return results
    
    def get_recent_moments(self, limit: int = 10) -> List[Moment]:
        """Get most recent moments."""
        sorted_moments = sorted(
            self.moments.values(),
            key=lambda m: m.timestamp,
            reverse=True
        )
        return sorted_moments[:limit]
    
    def get_significant_moments(self, min_significance: Significance = Significance.SIGNIFICANT) -> List[Moment]:
        """Get moments above a significance threshold."""
        return [
            m for m in self.moments.values()
            if m.significance.value >= min_significance.value
        ]
    
    def get_moments_by_type(self, moment_type: MomentType) -> List[Moment]:
        """Get moments of a specific type."""
        return [m for m in self.moments.values() if m.moment_type == moment_type]
    
    def get_strongest_memories(self, limit: int = 10) -> List[Moment]:
        """Get the strongest/most recalled memories."""
        return self.garden.get_strongest_memories(limit)
    
    def on_this_day(self) -> Dict[str, Any]:
        """Get memories from this day in previous years."""
        today = datetime.now()
        matching_moments = []
        
        for moment in self.moments.values():
            moment_date = moment.datetime
            if (moment_date.month == today.month and 
                moment_date.day == today.day and
                moment_date.year != today.year):
                matching_moments.append(moment)
        
        matching_entries = self.diary.on_this_day()
        
        return {
            'date': f"{today.strftime('%B %d')}",
            'moments': [m.summary() for m in matching_moments],
            'diary_entries': [e.summary() for e in matching_entries]
        }
    
    # ================
    # Palace Navigation
    # ================
    
    def enter_palace(self) -> str:
        """Enter the mind palace."""
        room = self.palace.begin_journey()
        return room.describe()
    
    def palace_go(self, direction: str) -> str:
        """Move through the palace."""
        room = self.palace.go(direction)
        if room:
            return room.describe()
        return "No door in that direction."
    
    def palace_look(self) -> Dict[str, Any]:
        """Look around current palace room."""
        return self.palace.look_around()
    
    def palace_examine(self, object_id: str) -> Optional[Dict[str, Any]]:
        """Examine an object in the palace."""
        return self.palace.examine_object(object_id)
    
    # ===============
    # Garden Tending
    # ===============
    
    def tend_garden(self):
        """Tend the memory garden (should be called periodically)."""
        self.garden.tend_garden()
    
    def water_memory(self, moment_id: str):
        """Water a memory to help it grow."""
        self.garden.water(moment_id)
    
    def garden_view(self) -> str:
        """Get a view of the garden."""
        return self.garden.describe_garden()
    
    # ==========
    # Statistics
    # ==========
    
    def get_stats(self) -> Dict[str, Any]:
        """Get observer statistics."""
        return {
            'total_moments': len(self.moments),
            'observation_count': self.observation_count,
            'last_observation': datetime.fromtimestamp(self.last_observation).isoformat() if self.last_observation else None,
            'garden': self.garden.get_garden_view(),
            'palace': self.palace.get_palace_map(),
            'diary': self.diary.get_statistics(),
            'moments_by_type': {
                t.value: len(self.get_moments_by_type(t))
                for t in MomentType
                if self.get_moments_by_type(t)
            }
        }
    
    def describe(self) -> str:
        """Get a poetic description of the observer's state."""
        stats = self.get_stats()
        
        lines = [
            "👁️ The Observer",
            "",
            f"Moments witnessed: {stats['total_moments']}",
            f"Observations made: {stats['observation_count']}",
            "",
            self.garden.describe_garden(),
            "",
            self.palace.describe_palace(),
            "",
            self.diary.describe()
        ]
        
        return "\n".join(lines)
    
    # ===================
    # Background Processing
    # ===================
    
    def start_background_processing(self, interval_seconds: float = 3600):
        """Start background memory processing (consolidation, decay, etc.)."""
        if self._background_active:
            return
        
        self._background_active = True
        
        def background_loop():
            while self._background_active:
                try:
                    # Tend the garden
                    self.tend_garden()
                    
                    # Apply memory decay
                    for moment in self.moments.values():
                        moment.decay()
                    
                    self._save_state()
                    
                except Exception as e:
                    print(f"[Observer] Background error: {e}")
                
                # Wait for next cycle
                time.sleep(interval_seconds)
        
        self._background_thread = threading.Thread(target=background_loop, daemon=True)
        self._background_thread.start()
        print("[Observer] Background processing started.")
    
    def stop_background_processing(self):
        """Stop background processing."""
        self._background_active = False
        if self._background_thread:
            self._background_thread.join(timeout=5)
        print("[Observer] Background processing stopped.")
    
    def shutdown(self):
        """Shutdown the observer."""
        self.stop_background_processing()
        self._save_state()
        print("[Observer] Shutting down. Memories preserved.")


# Singleton instance
_observer: Optional[ObserverCore] = None


def get_observer() -> ObserverCore:
    """Get or create the global observer instance."""
    global _observer
    if _observer is None:
        _observer = ObserverCore()
    return _observer


def observe(content: str, **kwargs) -> Optional[Moment]:
    """Convenience function to observe a moment."""
    return get_observer().observe(content, **kwargs)


def journal(content: str, **kwargs) -> DiaryEntry:
    """Convenience function to write a diary entry."""
    return get_observer().journal(content, **kwargs)
