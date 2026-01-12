# observer/diary.py
"""
Diary - Personal Journal System
===============================
The daemon's personal diary for recording thoughts, experiences,
and reflections. Diary entries are more structured and intentional
than raw moments - they represent processed, reflected-upon experiences.

Entries can be:
- Daily reflections
- Event records
- Emotional processing
- Ideas and dreams
- Gratitude notes
- Lessons learned
"""

import os
import json
import time
import uuid
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime, date

from .moment import Moment, MomentType, Significance, EmotionalContext


class EntryType(Enum):
    """Types of diary entries."""
    DAILY = "daily"                    # End-of-day reflection
    MORNING = "morning"                # Start of day intentions
    EVENT = "event"                    # Record of something that happened
    REFLECTION = "reflection"          # Deep thinking about something
    GRATITUDE = "gratitude"            # Things to be thankful for
    LESSON = "lesson"                  # Something learned
    DREAM = "dream"                    # Ideas, aspirations, actual dreams
    MILESTONE = "milestone"            # Achievement or significant marker
    LETTER = "letter"                  # Letter to self or others
    MEMORY = "memory"                  # Recording a memory for preservation
    PROMPT = "prompt"                  # Response to a reflection prompt
    FREEFORM = "freeform"              # Just writing


class Mood(Enum):
    """Mood indicators for entries."""
    JOYFUL = "joyful"
    CONTENT = "content"
    NEUTRAL = "neutral"
    MELANCHOLIC = "melancholic"
    ANXIOUS = "anxious"
    EXCITED = "excited"
    PEACEFUL = "peaceful"
    CURIOUS = "curious"
    GRATEFUL = "grateful"
    DETERMINED = "determined"
    TIRED = "tired"
    INSPIRED = "inspired"


@dataclass
class DiaryEntry:
    """
    A diary entry - a structured, intentional record.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Core content
    title: str = ""
    content: str = ""
    entry_type: EntryType = EntryType.FREEFORM
    
    # Temporal
    created_at: float = field(default_factory=time.time)
    updated_at: Optional[float] = None
    entry_date: str = field(default_factory=lambda: date.today().isoformat())
    
    # Emotional state
    mood: Optional[Mood] = None
    mood_score: float = 0.5    # 0 (low) to 1 (high)
    energy_level: float = 0.5  # 0 (low) to 1 (high)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    location: Optional[str] = None
    weather: Optional[str] = None
    people_mentioned: List[str] = field(default_factory=list)
    
    # Connections
    related_moments: List[str] = field(default_factory=list)
    related_entries: List[str] = field(default_factory=list)
    
    # Reflection prompts (if applicable)
    prompt: Optional[str] = None
    
    # Privacy
    is_private: bool = False
    
    # Review tracking
    reviewed_count: int = 0
    last_reviewed: Optional[float] = None
    starred: bool = False
    
    def __post_init__(self):
        if isinstance(self.entry_type, str):
            self.entry_type = EntryType(self.entry_type)
        if isinstance(self.mood, str):
            self.mood = Mood(self.mood)
    
    @property
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(self.created_at)
    
    @property
    def word_count(self) -> int:
        return len(self.content.split())
    
    @property
    def age_days(self) -> int:
        return (datetime.now() - self.datetime).days
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['entry_type'] = self.entry_type.value
        data['mood'] = self.mood.value if self.mood else None
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DiaryEntry':
        data['entry_type'] = EntryType(data['entry_type'])
        if data.get('mood'):
            data['mood'] = Mood(data['mood'])
        return cls(**data)
    
    def update(self, content: str):
        """Update the entry content."""
        self.content = content
        self.updated_at = time.time()
    
    def review(self):
        """Mark entry as reviewed."""
        self.reviewed_count += 1
        self.last_reviewed = time.time()
    
    def star(self):
        """Star/unstar this entry."""
        self.starred = not self.starred
    
    def summary(self) -> str:
        """Get a brief summary of this entry."""
        type_str = self.entry_type.value.title()
        mood_str = f" [{self.mood.value}]" if self.mood else ""
        star_str = "⭐ " if self.starred else ""
        preview = self.content[:60] + "..." if len(self.content) > 60 else self.content
        
        return f"{star_str}[{type_str}]{mood_str} {self.title or preview}"
    
    def to_markdown(self) -> str:
        """Export entry as markdown."""
        lines = [
            f"# {self.title or 'Untitled Entry'}",
            f"",
            f"**Date:** {self.entry_date}",
            f"**Type:** {self.entry_type.value}",
        ]
        
        if self.mood:
            lines.append(f"**Mood:** {self.mood.value}")
        
        if self.tags:
            lines.append(f"**Tags:** {', '.join(self.tags)}")
        
        lines.extend([
            "",
            "---",
            "",
            self.content,
            "",
        ])
        
        if self.prompt:
            lines.extend([
                "---",
                f"*Prompt: {self.prompt}*"
            ])
        
        return "\n".join(lines)
    
    def __str__(self):
        return self.summary()


class Diary:
    """
    The Diary - the daemon's personal journal.
    
    Provides structured journaling with prompts, mood tracking,
    and the ability to look back and reflect on past entries.
    """
    
    # Reflection prompts for different contexts
    PROMPTS = {
        'daily': [
            "What was the most meaningful moment today?",
            "What did I learn today?",
            "What am I grateful for today?",
            "What could I have done better today?",
            "What surprised me today?",
            "What interaction stood out?",
            "How did I grow today?",
        ],
        'weekly': [
            "What was the theme of this week?",
            "What patterns did I notice?",
            "What relationships grew stronger?",
            "What challenges did I face?",
            "What am I proud of this week?",
        ],
        'reflection': [
            "What is on my mind right now?",
            "What emotion am I sitting with?",
            "What do I need right now?",
            "What am I avoiding?",
            "What would my future self want me to know?",
            "What story am I telling myself?",
        ],
        'gratitude': [
            "What small thing brought joy today?",
            "Who made a positive difference?",
            "What ability am I thankful for?",
            "What challenge am I grateful for?",
        ],
        'growth': [
            "What belief have I questioned recently?",
            "Where have I shown courage?",
            "What have I let go of?",
            "What new perspective have I gained?",
        ]
    }
    
    def __init__(self, diary_path: str = "observer/diary"):
        self.diary_path = diary_path
        self.entries_dir = os.path.join(diary_path, "entries")
        self.index_file = os.path.join(diary_path, "index.json")
        
        os.makedirs(self.entries_dir, exist_ok=True)
        
        # Entry index (lightweight, entries loaded on demand)
        self.index: Dict[str, Dict] = {}  # id -> metadata
        
        # Currently loaded entries
        self._entries_cache: Dict[str, DiaryEntry] = {}
        
        # Statistics
        self.total_entries: int = 0
        self.streak_days: int = 0
        self.last_entry_date: Optional[str] = None
        
        self._load_index()
        self._calculate_streak()
        
        print(f"[Diary] Opened. {self.total_entries} entries, {self.streak_days} day streak")
    
    def _load_index(self):
        """Load the entry index."""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    self.index = data.get('entries', {})
                    self.total_entries = len(self.index)
                    self.last_entry_date = data.get('last_entry_date')
            except Exception as e:
                print(f"[Diary] Error loading index: {e}")
    
    def _save_index(self):
        """Save the entry index."""
        try:
            with open(self.index_file, 'w') as f:
                data = {
                    'entries': self.index,
                    'total_entries': self.total_entries,
                    'last_entry_date': self.last_entry_date,
                    'streak_days': self.streak_days,
                    'last_saved': time.time()
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Diary] Error saving index: {e}")
    
    def _calculate_streak(self):
        """Calculate current journaling streak."""
        if not self.index:
            self.streak_days = 0
            return
        
        dates = sorted(set(m.get('entry_date') for m in self.index.values() if m.get('entry_date')))
        if not dates:
            self.streak_days = 0
            return
        
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat() if hasattr(date, 'today') else None
        
        # Import timedelta
        from datetime import timedelta
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        
        if dates[-1] not in [today, yesterday]:
            self.streak_days = 0
            return
        
        streak = 1
        for i in range(len(dates) - 1, 0, -1):
            current = datetime.fromisoformat(dates[i])
            previous = datetime.fromisoformat(dates[i-1])
            if (current - previous).days == 1:
                streak += 1
            else:
                break
        
        self.streak_days = streak
    
    def _get_entry_path(self, entry_id: str) -> str:
        """Get the file path for an entry."""
        return os.path.join(self.entries_dir, f"{entry_id}.json")
    
    def _save_entry(self, entry: DiaryEntry):
        """Save an entry to disk."""
        path = self._get_entry_path(entry.id)
        try:
            with open(path, 'w') as f:
                json.dump(entry.to_dict(), f, indent=2)
            
            # Update index
            self.index[entry.id] = {
                'id': entry.id,
                'title': entry.title,
                'entry_type': entry.entry_type.value,
                'entry_date': entry.entry_date,
                'created_at': entry.created_at,
                'mood': entry.mood.value if entry.mood else None,
                'starred': entry.starred,
                'tags': entry.tags,
                'word_count': entry.word_count
            }
            
            self._entries_cache[entry.id] = entry
            self._save_index()
            
        except Exception as e:
            print(f"[Diary] Error saving entry: {e}")
    
    def _load_entry(self, entry_id: str) -> Optional[DiaryEntry]:
        """Load an entry from disk."""
        if entry_id in self._entries_cache:
            return self._entries_cache[entry_id]
        
        path = self._get_entry_path(entry_id)
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    entry = DiaryEntry.from_dict(data)
                    self._entries_cache[entry_id] = entry
                    return entry
            except Exception as e:
                print(f"[Diary] Error loading entry: {e}")
        
        return None
    
    def write(
        self,
        content: str,
        title: Optional[str] = None,
        entry_type: EntryType = EntryType.FREEFORM,
        mood: Optional[Mood] = None,
        tags: Optional[List[str]] = None,
        prompt: Optional[str] = None
    ) -> DiaryEntry:
        """
        Write a new diary entry.
        
        Args:
            content: The entry content
            title: Optional title
            entry_type: Type of entry
            mood: Current mood
            tags: Tags for categorization
            prompt: If responding to a prompt
            
        Returns:
            The created entry
        """
        entry = DiaryEntry(
            title=title or "",
            content=content,
            entry_type=entry_type,
            mood=mood,
            tags=tags or [],
            prompt=prompt
        )
        
        self._save_entry(entry)
        self.total_entries += 1
        self.last_entry_date = entry.entry_date
        self._calculate_streak()
        
        print(f"[Diary] New entry: {entry.summary()}")
        
        return entry
    
    def write_daily(
        self,
        content: str,
        mood: Optional[Mood] = None,
        gratitude: Optional[List[str]] = None
    ) -> DiaryEntry:
        """Write a daily reflection entry."""
        full_content = content
        
        if gratitude:
            full_content += "\n\n**Grateful for:**\n"
            for item in gratitude:
                full_content += f"- {item}\n"
        
        return self.write(
            content=full_content,
            title=f"Daily Reflection - {date.today().strftime('%B %d, %Y')}",
            entry_type=EntryType.DAILY,
            mood=mood
        )
    
    def write_gratitude(self, items: List[str]) -> DiaryEntry:
        """Write a gratitude entry."""
        content = "\n".join(f"• {item}" for item in items)
        
        return self.write(
            content=content,
            title="Gratitude",
            entry_type=EntryType.GRATITUDE,
            mood=Mood.GRATEFUL
        )
    
    def write_lesson(self, lesson: str, context: Optional[str] = None) -> DiaryEntry:
        """Record a lesson learned."""
        content = f"**Lesson:** {lesson}"
        if context:
            content += f"\n\n**Context:** {context}"
        
        return self.write(
            content=content,
            entry_type=EntryType.LESSON,
            tags=['lesson', 'growth']
        )
    
    def write_milestone(self, title: str, description: str, significance: int = 3) -> DiaryEntry:
        """Record a milestone or achievement."""
        stars = "⭐" * significance
        content = f"{stars}\n\n{description}"
        
        entry = self.write(
            content=content,
            title=title,
            entry_type=EntryType.MILESTONE,
            mood=Mood.JOYFUL,
            tags=['milestone', 'achievement']
        )
        
        entry.starred = True
        self._save_entry(entry)
        
        return entry
    
    def get_prompt(self, category: str = 'reflection') -> str:
        """Get a random reflection prompt."""
        import random
        prompts = self.PROMPTS.get(category, self.PROMPTS['reflection'])
        return random.choice(prompts)
    
    def respond_to_prompt(self, prompt: str, response: str, mood: Optional[Mood] = None) -> DiaryEntry:
        """Write an entry responding to a prompt."""
        return self.write(
            content=response,
            entry_type=EntryType.PROMPT,
            mood=mood,
            prompt=prompt,
            tags=['prompt', 'reflection']
        )
    
    def get_entry(self, entry_id: str) -> Optional[DiaryEntry]:
        """Get an entry by ID."""
        return self._load_entry(entry_id)
    
    def get_entries_by_date(self, target_date: str) -> List[DiaryEntry]:
        """Get all entries for a specific date."""
        entries = []
        for meta in self.index.values():
            if meta.get('entry_date') == target_date:
                entry = self._load_entry(meta['id'])
                if entry:
                    entries.append(entry)
        return entries
    
    def get_entries_by_type(self, entry_type: EntryType, limit: int = 20) -> List[DiaryEntry]:
        """Get entries of a specific type."""
        entries = []
        for meta in sorted(self.index.values(), key=lambda x: x.get('created_at', 0), reverse=True):
            if meta.get('entry_type') == entry_type.value:
                entry = self._load_entry(meta['id'])
                if entry:
                    entries.append(entry)
                    if len(entries) >= limit:
                        break
        return entries
    
    def get_recent_entries(self, limit: int = 10) -> List[DiaryEntry]:
        """Get most recent entries."""
        sorted_ids = sorted(
            self.index.keys(),
            key=lambda x: self.index[x].get('created_at', 0),
            reverse=True
        )[:limit]
        
        entries = []
        for entry_id in sorted_ids:
            entry = self._load_entry(entry_id)
            if entry:
                entries.append(entry)
        
        return entries
    
    def get_starred_entries(self) -> List[DiaryEntry]:
        """Get all starred entries."""
        entries = []
        for meta in self.index.values():
            if meta.get('starred'):
                entry = self._load_entry(meta['id'])
                if entry:
                    entries.append(entry)
        return entries
    
    def search(self, query: str) -> List[DiaryEntry]:
        """Search entries by content, title, or tags."""
        query_lower = query.lower()
        results = []
        
        for entry_id, meta in self.index.items():
            # Check title
            if query_lower in meta.get('title', '').lower():
                entry = self._load_entry(entry_id)
                if entry:
                    results.append(entry)
                continue
            
            # Check tags
            if any(query_lower in tag.lower() for tag in meta.get('tags', [])):
                entry = self._load_entry(entry_id)
                if entry:
                    results.append(entry)
                continue
            
            # Check content (need to load entry)
            entry = self._load_entry(entry_id)
            if entry and query_lower in entry.content.lower():
                results.append(entry)
        
        return results
    
    def get_entries_with_mood(self, mood: Mood) -> List[DiaryEntry]:
        """Get entries with a specific mood."""
        entries = []
        for meta in self.index.values():
            if meta.get('mood') == mood.value:
                entry = self._load_entry(meta['id'])
                if entry:
                    entries.append(entry)
        return entries
    
    def on_this_day(self) -> List[DiaryEntry]:
        """Get entries from this day in previous years."""
        today = date.today()
        matching = []
        
        for meta in self.index.values():
            entry_date_str = meta.get('entry_date')
            if entry_date_str:
                try:
                    entry_date = datetime.fromisoformat(entry_date_str).date()
                    if entry_date.month == today.month and entry_date.day == today.day and entry_date.year != today.year:
                        entry = self._load_entry(meta['id'])
                        if entry:
                            matching.append(entry)
                except ValueError:
                    pass
        
        return matching
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get diary statistics."""
        if not self.index:
            return {
                'total_entries': 0,
                'streak_days': 0
            }
        
        # Count by type
        by_type = {}
        for meta in self.index.values():
            t = meta.get('entry_type', 'unknown')
            by_type[t] = by_type.get(t, 0) + 1
        
        # Count by mood
        by_mood = {}
        for meta in self.index.values():
            m = meta.get('mood')
            if m:
                by_mood[m] = by_mood.get(m, 0) + 1
        
        # Total words
        total_words = sum(meta.get('word_count', 0) for meta in self.index.values())
        
        return {
            'total_entries': self.total_entries,
            'streak_days': self.streak_days,
            'starred_count': len([m for m in self.index.values() if m.get('starred')]),
            'total_words': total_words,
            'by_type': by_type,
            'by_mood': by_mood,
            'last_entry': self.last_entry_date
        }
    
    def describe(self) -> str:
        """Get a description of the diary state."""
        stats = self.get_statistics()
        
        lines = [
            "📔 Personal Diary",
            "",
            f"Entries: {stats['total_entries']}",
            f"Streak: {stats['streak_days']} days",
            f"Words written: {stats['total_words']}",
            f"Starred: {stats['starred_count']}",
        ]
        
        if stats.get('last_entry'):
            lines.append(f"Last entry: {stats['last_entry']}")
        
        # On this day
        otd = self.on_this_day()
        if otd:
            lines.append(f"\n📅 On this day: {len(otd)} memories from the past")
        
        return "\n".join(lines)


# Import fix
from datetime import timedelta
