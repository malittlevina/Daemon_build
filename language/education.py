# language/education.py
"""
Education Module
================
Learning and educational capabilities:
- Vocabulary building
- Grammar lessons
- Learning progress tracking
- Spaced repetition
- Tutoring interactions
"""

import os
import json
import time
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .vocabulary import Vocabulary, Word, PartOfSpeech
from .grammar import Grammar


@dataclass
class LearningItem:
    """An item to learn (word, rule, concept)."""
    item_id: str
    item_type: str  # word, grammar_rule, concept
    content: Dict[str, Any]
    
    # Spaced repetition data
    interval_days: float = 1.0
    ease_factor: float = 2.5
    repetitions: int = 0
    next_review: Optional[float] = None
    last_review: Optional[float] = None
    
    # Performance
    correct_count: int = 0
    incorrect_count: int = 0
    
    def __post_init__(self):
        if self.next_review is None:
            self.next_review = time.time()
    
    @property
    def accuracy(self) -> float:
        total = self.correct_count + self.incorrect_count
        return self.correct_count / total if total > 0 else 0.0
    
    def update_after_review(self, quality: int):
        """
        Update using SM-2 spaced repetition algorithm.
        Quality: 0-5 (0-2 = fail, 3-5 = pass)
        """
        self.last_review = time.time()
        
        if quality >= 3:
            self.correct_count += 1
            if self.repetitions == 0:
                self.interval_days = 1
            elif self.repetitions == 1:
                self.interval_days = 6
            else:
                self.interval_days = self.interval_days * self.ease_factor
            
            self.repetitions += 1
            self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        else:
            self.incorrect_count += 1
            self.repetitions = 0
            self.interval_days = 1
        
        self.next_review = time.time() + (self.interval_days * 86400)
    
    def is_due(self) -> bool:
        """Check if item is due for review."""
        return time.time() >= self.next_review
    
    def to_dict(self) -> dict:
        return {
            'item_id': self.item_id,
            'item_type': self.item_type,
            'content': self.content,
            'interval_days': self.interval_days,
            'ease_factor': self.ease_factor,
            'repetitions': self.repetitions,
            'next_review': self.next_review,
            'last_review': self.last_review,
            'correct_count': self.correct_count,
            'incorrect_count': self.incorrect_count
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LearningItem':
        return cls(**data)


@dataclass
class LearningSession:
    """A learning session with items to review."""
    session_id: str
    session_type: str  # vocabulary, grammar, mixed
    items: List[LearningItem]
    current_index: int = 0
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    results: List[Dict] = field(default_factory=list)
    
    @property
    def is_complete(self) -> bool:
        return self.current_index >= len(self.items)
    
    @property
    def current_item(self) -> Optional[LearningItem]:
        if self.current_index < len(self.items):
            return self.items[self.current_index]
        return None
    
    def next_item(self) -> Optional[LearningItem]:
        """Move to next item and return it."""
        self.current_index += 1
        return self.current_item
    
    def record_result(self, item_id: str, quality: int, response: str):
        """Record a review result."""
        self.results.append({
            'item_id': item_id,
            'quality': quality,
            'response': response,
            'timestamp': time.time()
        })
    
    def complete(self):
        """Mark session as complete."""
        self.completed_at = time.time()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        correct = len([r for r in self.results if r['quality'] >= 3])
        total = len(self.results)
        
        return {
            'total_items': len(self.items),
            'reviewed': total,
            'correct': correct,
            'accuracy': correct / total if total > 0 else 0,
            'duration_minutes': (time.time() - self.started_at) / 60
        }


@dataclass
class LearningProgress:
    """Track overall learning progress."""
    total_items_learned: int = 0
    total_reviews: int = 0
    streak_days: int = 0
    last_study_date: Optional[str] = None
    
    # By category
    vocabulary_mastered: int = 0
    grammar_mastered: int = 0
    
    # Session history
    sessions_completed: int = 0
    total_study_minutes: float = 0
    
    def to_dict(self) -> dict:
        return {
            'total_items_learned': self.total_items_learned,
            'total_reviews': self.total_reviews,
            'streak_days': self.streak_days,
            'last_study_date': self.last_study_date,
            'vocabulary_mastered': self.vocabulary_mastered,
            'grammar_mastered': self.grammar_mastered,
            'sessions_completed': self.sessions_completed,
            'total_study_minutes': self.total_study_minutes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LearningProgress':
        return cls(**data)


class EducationModule:
    """
    Education system for vocabulary and grammar learning.
    Uses spaced repetition for effective learning.
    """
    
    def __init__(
        self,
        vocabulary: Optional[Vocabulary] = None,
        grammar: Optional[Grammar] = None,
        data_path: str = "language/data/learning"
    ):
        self.vocabulary = vocabulary or Vocabulary()
        self.grammar = grammar or Grammar(self.vocabulary)
        self.data_path = data_path
        
        os.makedirs(data_path, exist_ok=True)
        
        # Learning items
        self.items: Dict[str, LearningItem] = {}
        self.progress = LearningProgress()
        
        # Current session
        self.current_session: Optional[LearningSession] = None
        
        self._load()
        print(f"[Education] Initialized with {len(self.items)} learning items.")
    
    def _load(self):
        """Load learning data."""
        items_file = os.path.join(self.data_path, "items.json")
        progress_file = os.path.join(self.data_path, "progress.json")
        
        if os.path.exists(items_file):
            try:
                with open(items_file, 'r') as f:
                    data = json.load(f)
                    for item_data in data.get('items', []):
                        item = LearningItem.from_dict(item_data)
                        self.items[item.item_id] = item
            except Exception as e:
                print(f"[Education] Load items error: {e}")
        
        if os.path.exists(progress_file):
            try:
                with open(progress_file, 'r') as f:
                    data = json.load(f)
                    self.progress = LearningProgress.from_dict(data)
            except Exception as e:
                print(f"[Education] Load progress error: {e}")
    
    def _save(self):
        """Save learning data."""
        try:
            items_file = os.path.join(self.data_path, "items.json")
            with open(items_file, 'w') as f:
                json.dump({
                    'items': [i.to_dict() for i in self.items.values()],
                    'count': len(self.items)
                }, f, indent=2)
            
            progress_file = os.path.join(self.data_path, "progress.json")
            with open(progress_file, 'w') as f:
                json.dump(self.progress.to_dict(), f, indent=2)
                
        except Exception as e:
            print(f"[Education] Save error: {e}")
    
    def add_vocabulary_item(self, word: str, definition: str = None) -> LearningItem:
        """Add a vocabulary word to learn."""
        item_id = f"vocab_{word.lower()}"
        
        if item_id in self.items:
            return self.items[item_id]
        
        # Get from vocabulary if exists
        vocab_word = self.vocabulary.get(word)
        if vocab_word and not definition:
            definition = vocab_word.primary_definition
        
        if not definition:
            definition = f"Definition of {word}"
        
        item = LearningItem(
            item_id=item_id,
            item_type='word',
            content={
                'word': word,
                'definition': definition,
                'examples': [],
                'synonyms': vocab_word.synonyms() if vocab_word else []
            }
        )
        
        self.items[item_id] = item
        self.progress.total_items_learned += 1
        self._save()
        
        return item
    
    def add_grammar_rule(self, name: str, rule: str, examples: List[str] = None) -> LearningItem:
        """Add a grammar rule to learn."""
        item_id = f"grammar_{name.lower().replace(' ', '_')}"
        
        if item_id in self.items:
            return self.items[item_id]
        
        item = LearningItem(
            item_id=item_id,
            item_type='grammar_rule',
            content={
                'name': name,
                'rule': rule,
                'examples': examples or []
            }
        )
        
        self.items[item_id] = item
        self.progress.total_items_learned += 1
        self._save()
        
        return item
    
    def get_due_items(self, limit: int = 20) -> List[LearningItem]:
        """Get items due for review."""
        due = [item for item in self.items.values() if item.is_due()]
        due.sort(key=lambda x: x.next_review)
        return due[:limit]
    
    def start_session(self, session_type: str = 'mixed', item_count: int = 10) -> LearningSession:
        """Start a new learning session."""
        # Get due items
        due_items = self.get_due_items(item_count * 2)
        
        # Filter by type if needed
        if session_type == 'vocabulary':
            due_items = [i for i in due_items if i.item_type == 'word']
        elif session_type == 'grammar':
            due_items = [i for i in due_items if i.item_type == 'grammar_rule']
        
        # Shuffle and limit
        random.shuffle(due_items)
        session_items = due_items[:item_count]
        
        # If not enough due items, add some random items
        if len(session_items) < item_count:
            all_items = list(self.items.values())
            random.shuffle(all_items)
            for item in all_items:
                if item not in session_items:
                    session_items.append(item)
                if len(session_items) >= item_count:
                    break
        
        self.current_session = LearningSession(
            session_id=f"session_{int(time.time())}",
            session_type=session_type,
            items=session_items
        )
        
        print(f"[Education] Started {session_type} session with {len(session_items)} items.")
        return self.current_session
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Get the current question in the session."""
        if not self.current_session or self.current_session.is_complete:
            return None
        
        item = self.current_session.current_item
        if not item:
            return None
        
        if item.item_type == 'word':
            return self._create_vocabulary_question(item)
        elif item.item_type == 'grammar_rule':
            return self._create_grammar_question(item)
        
        return None
    
    def _create_vocabulary_question(self, item: LearningItem) -> Dict[str, Any]:
        """Create a vocabulary question."""
        word = item.content['word']
        definition = item.content['definition']
        
        # Randomly choose question type
        q_type = random.choice(['define', 'word_from_def', 'fill_blank'])
        
        if q_type == 'define':
            return {
                'type': 'define',
                'question': f"What does '{word}' mean?",
                'answer': definition,
                'item_id': item.item_id
            }
        elif q_type == 'word_from_def':
            return {
                'type': 'word_from_def',
                'question': f"What word means: \"{definition}\"?",
                'answer': word,
                'item_id': item.item_id
            }
        else:
            # Fill in the blank
            examples = item.content.get('examples', [])
            if examples:
                example = random.choice(examples)
                blanked = example.replace(word, '_____')
                return {
                    'type': 'fill_blank',
                    'question': f"Fill in the blank: {blanked}",
                    'answer': word,
                    'item_id': item.item_id
                }
            else:
                return {
                    'type': 'define',
                    'question': f"What does '{word}' mean?",
                    'answer': definition,
                    'item_id': item.item_id
                }
    
    def _create_grammar_question(self, item: LearningItem) -> Dict[str, Any]:
        """Create a grammar question."""
        name = item.content['name']
        rule = item.content['rule']
        examples = item.content.get('examples', [])
        
        return {
            'type': 'grammar',
            'question': f"Explain the grammar rule: {name}",
            'answer': rule,
            'examples': examples,
            'item_id': item.item_id
        }
    
    def answer_question(self, response: str, self_grade: int = None) -> Dict[str, Any]:
        """
        Answer the current question.
        
        Args:
            response: The user's answer
            self_grade: Self-graded quality (0-5) or None for auto-grade
            
        Returns:
            Result with feedback
        """
        if not self.current_session:
            return {'error': 'No active session'}
        
        item = self.current_session.current_item
        if not item:
            return {'error': 'No current item'}
        
        question = self.get_current_question()
        if not question:
            return {'error': 'No current question'}
        
        correct_answer = question['answer']
        
        # Auto-grade if not self-graded
        if self_grade is None:
            # Simple comparison (could be made smarter)
            response_clean = response.lower().strip()
            answer_clean = correct_answer.lower().strip()
            
            if response_clean == answer_clean:
                quality = 5
            elif answer_clean in response_clean or response_clean in answer_clean:
                quality = 4
            elif len(set(response_clean.split()) & set(answer_clean.split())) > 0:
                quality = 3
            else:
                quality = 2
        else:
            quality = self_grade
        
        # Update item with spaced repetition
        item.update_after_review(quality)
        
        # Record result
        self.current_session.record_result(item.item_id, quality, response)
        
        # Move to next
        next_item = self.current_session.next_item()
        
        # Update progress
        self.progress.total_reviews += 1
        self._update_streak()
        
        # Check if mastered
        if item.repetitions >= 5 and item.accuracy >= 0.9:
            if item.item_type == 'word':
                self.progress.vocabulary_mastered += 1
            elif item.item_type == 'grammar_rule':
                self.progress.grammar_mastered += 1
        
        self._save()
        
        result = {
            'correct': quality >= 3,
            'quality': quality,
            'correct_answer': correct_answer,
            'your_answer': response,
            'feedback': self._get_feedback(quality),
            'session_complete': self.current_session.is_complete,
            'next_review': datetime.fromtimestamp(item.next_review).strftime('%Y-%m-%d')
        }
        
        if self.current_session.is_complete:
            self.current_session.complete()
            self.progress.sessions_completed += 1
            stats = self.current_session.get_stats()
            self.progress.total_study_minutes += stats['duration_minutes']
            result['session_stats'] = stats
            self._save()
        
        return result
    
    def _get_feedback(self, quality: int) -> str:
        """Get feedback message based on quality."""
        if quality >= 5:
            return "Perfect! 🌟"
        elif quality >= 4:
            return "Great job! ✨"
        elif quality >= 3:
            return "Correct! Keep practicing. 👍"
        elif quality >= 2:
            return "Almost there. Review this one again. 📚"
        else:
            return "Let's learn this one better. 💪"
    
    def _update_streak(self):
        """Update study streak."""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if self.progress.last_study_date:
            last_date = datetime.strptime(self.progress.last_study_date, '%Y-%m-%d')
            today_date = datetime.strptime(today, '%Y-%m-%d')
            
            if (today_date - last_date).days == 1:
                self.progress.streak_days += 1
            elif (today_date - last_date).days > 1:
                self.progress.streak_days = 1
        else:
            self.progress.streak_days = 1
        
        self.progress.last_study_date = today
    
    def get_stats(self) -> Dict[str, Any]:
        """Get learning statistics."""
        due_count = len(self.get_due_items(100))
        
        return {
            'total_items': len(self.items),
            'due_for_review': due_count,
            'progress': self.progress.to_dict(),
            'vocabulary_items': len([i for i in self.items.values() if i.item_type == 'word']),
            'grammar_items': len([i for i in self.items.values() if i.item_type == 'grammar_rule'])
        }
    
    def describe(self) -> str:
        """Get a description of learning status."""
        stats = self.get_stats()
        
        lines = [
            "📚 Learning Progress",
            "",
            f"Items to learn: {stats['total_items']}",
            f"Due for review: {stats['due_for_review']}",
            f"Study streak: {self.progress.streak_days} days",
            f"Sessions completed: {self.progress.sessions_completed}",
            f"Total study time: {self.progress.total_study_minutes:.0f} minutes",
            "",
            f"Vocabulary mastered: {self.progress.vocabulary_mastered}",
            f"Grammar mastered: {self.progress.grammar_mastered}",
        ]
        
        return "\n".join(lines)
