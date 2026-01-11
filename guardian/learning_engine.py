# guardian/learning_engine.py
"""
Learning Engine - Adaptive learning from experience

Provides:
- Pattern recognition from interactions
- Preference learning
- Skill acquisition
- Performance optimization
"""

from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import json
import os
import math
import threading


class LearningType(Enum):
    """Types of learning."""
    REINFORCEMENT = "reinforcement"    # Learn from feedback
    IMITATION = "imitation"            # Learn from examples
    ASSOCIATION = "association"        # Learn patterns
    OPTIMIZATION = "optimization"      # Learn to improve metrics


class FeedbackType(Enum):
    """Types of feedback."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CORRECTION = "correction"


@dataclass
class Experience:
    """A recorded experience for learning."""
    experience_id: str
    context: Dict[str, Any]
    action: str
    result: Any
    feedback: Optional[FeedbackType] = None
    reward: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearnedPattern:
    """A pattern learned from experiences."""
    pattern_id: str
    pattern_type: str
    trigger: str
    response: str
    confidence: float = 0.5
    usage_count: int = 0
    success_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        return self.success_count / max(1, self.usage_count)


@dataclass
class Skill:
    """A learned skill/capability."""
    name: str
    description: str
    proficiency: float = 0.0  # 0.0 to 1.0
    practice_count: int = 0
    success_count: int = 0
    last_practiced: Optional[datetime] = None
    prerequisites: List[str] = field(default_factory=list)
    related_patterns: List[str] = field(default_factory=list)


@dataclass
class Preference:
    """A learned preference."""
    name: str
    category: str
    value: Any
    confidence: float = 0.5
    observation_count: int = 1
    last_observed: datetime = field(default_factory=datetime.utcnow)


class LearningEngine:
    """
    Engine for learning from experience.
    
    Features:
    - Experience recording and analysis
    - Pattern extraction
    - Skill development
    - Preference learning
    - Continuous improvement
    """
    
    module_name = "learning_engine"
    dependencies = []
    
    def __init__(self, storage_path: str = "logs/learning"):
        self._lock = threading.RLock()
        self._kernel = None
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Experience memory
        self.experiences: List[Experience] = []
        self.max_experiences = 10000
        
        # Learned knowledge
        self.patterns: Dict[str, LearnedPattern] = {}
        self.skills: Dict[str, Skill] = {}
        self.preferences: Dict[str, Preference] = {}
        
        # Learning statistics
        self.stats = {
            "total_experiences": 0,
            "positive_feedback": 0,
            "negative_feedback": 0,
            "patterns_learned": 0,
            "skills_acquired": 0
        }
        
        # Pattern extraction thresholds
        self.min_pattern_occurrences = 3
        self.min_pattern_confidence = 0.6
        
        # Load persisted knowledge
        self._load_knowledge()
        
        print("[LearningEngine] Initialized.")
    
    def initialize(self, kernel) -> bool:
        """Initialize with kernel reference."""
        self._kernel = kernel
        
        if kernel:
            kernel.subscribe("interaction.complete", self._on_interaction)
            kernel.subscribe("feedback.received", self._on_feedback)
        
        return True
    
    def start(self) -> bool:
        """Start learning services."""
        # Start background learning
        self._start_background_learning()
        return True
    
    def stop(self) -> bool:
        """Stop and persist."""
        self._save_knowledge()
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "status": "healthy",
            "experiences": len(self.experiences),
            "patterns": len(self.patterns),
            "skills": len(self.skills)
        }
    
    # ==================== Experience Recording ====================
    
    def record_experience(
        self,
        context: Dict[str, Any],
        action: str,
        result: Any,
        reward: float = 0.0,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Record an experience for learning."""
        import uuid
        exp_id = str(uuid.uuid4())[:8]
        
        experience = Experience(
            experience_id=exp_id,
            context=context,
            action=action,
            result=result,
            reward=reward,
            metadata=metadata or {}
        )
        
        with self._lock:
            self.experiences.append(experience)
            self.stats["total_experiences"] += 1
            
            # Enforce memory limit
            if len(self.experiences) > self.max_experiences:
                self.experiences = self.experiences[-self.max_experiences:]
        
        # Trigger pattern extraction if enough experiences
        if len(self.experiences) % 100 == 0:
            self._extract_patterns()
        
        return exp_id
    
    def add_feedback(
        self,
        experience_id: str,
        feedback_type: FeedbackType,
        details: str = ""
    ):
        """Add feedback to an experience."""
        with self._lock:
            for exp in self.experiences:
                if exp.experience_id == experience_id:
                    exp.feedback = feedback_type
                    
                    # Update reward based on feedback
                    if feedback_type == FeedbackType.POSITIVE:
                        exp.reward = max(exp.reward + 1.0, exp.reward)
                        self.stats["positive_feedback"] += 1
                    elif feedback_type == FeedbackType.NEGATIVE:
                        exp.reward = min(exp.reward - 1.0, exp.reward)
                        self.stats["negative_feedback"] += 1
                    
                    break
        
        # Update related patterns
        self._update_patterns_from_feedback(experience_id, feedback_type)
    
    # ==================== Pattern Learning ====================
    
    def _extract_patterns(self):
        """Extract patterns from recent experiences."""
        with self._lock:
            # Group experiences by context features
            context_groups = defaultdict(list)
            
            for exp in self.experiences[-500:]:  # Look at recent experiences
                # Create context key from important features
                context_key = self._create_context_key(exp.context)
                context_groups[context_key].append(exp)
            
            # Find patterns in groups
            for context_key, group in context_groups.items():
                if len(group) < self.min_pattern_occurrences:
                    continue
                
                # Find common actions
                action_counts = defaultdict(int)
                for exp in group:
                    action_counts[exp.action] += 1
                
                # Check for dominant action
                if action_counts:
                    best_action = max(action_counts.items(), key=lambda x: x[1])
                    action, count = best_action
                    
                    confidence = count / len(group)
                    if confidence >= self.min_pattern_confidence:
                        pattern_id = f"pattern_{context_key}_{action}"[:50]
                        
                        if pattern_id not in self.patterns:
                            self.patterns[pattern_id] = LearnedPattern(
                                pattern_id=pattern_id,
                                pattern_type="context_action",
                                trigger=context_key,
                                response=action,
                                confidence=confidence
                            )
                            self.stats["patterns_learned"] += 1
                            print(f"[LearningEngine] Learned pattern: {context_key} -> {action}")
    
    def _create_context_key(self, context: Dict[str, Any]) -> str:
        """Create a hashable key from context."""
        # Extract relevant features
        features = []
        
        if "mode" in context:
            features.append(f"mode:{context['mode']}")
        if "intent" in context:
            features.append(f"intent:{context['intent']}")
        if "topic" in context:
            features.append(f"topic:{context['topic']}")
        if "type" in context:
            features.append(f"type:{context['type']}")
        
        return "|".join(sorted(features)) if features else "default"
    
    def _update_patterns_from_feedback(
        self,
        experience_id: str,
        feedback: FeedbackType
    ):
        """Update patterns based on feedback."""
        with self._lock:
            # Find the experience
            exp = None
            for e in self.experiences:
                if e.experience_id == experience_id:
                    exp = e
                    break
            
            if not exp:
                return
            
            context_key = self._create_context_key(exp.context)
            
            # Find matching patterns
            for pattern in self.patterns.values():
                if pattern.trigger == context_key and pattern.response == exp.action:
                    pattern.usage_count += 1
                    pattern.last_used = datetime.utcnow()
                    
                    if feedback == FeedbackType.POSITIVE:
                        pattern.success_count += 1
                        pattern.confidence = min(1.0, pattern.confidence + 0.05)
                    elif feedback == FeedbackType.NEGATIVE:
                        pattern.confidence = max(0.1, pattern.confidence - 0.1)
    
    def get_pattern_for_context(
        self,
        context: Dict[str, Any]
    ) -> Optional[LearnedPattern]:
        """Get the best pattern for a given context."""
        context_key = self._create_context_key(context)
        
        with self._lock:
            matching = [
                p for p in self.patterns.values()
                if p.trigger == context_key and p.confidence >= self.min_pattern_confidence
            ]
            
            if matching:
                # Return highest confidence pattern
                return max(matching, key=lambda p: p.confidence * p.success_rate)
        
        return None
    
    # ==================== Skill Learning ====================
    
    def practice_skill(
        self,
        skill_name: str,
        success: bool,
        context: Dict[str, Any] = None
    ):
        """Record skill practice."""
        with self._lock:
            if skill_name not in self.skills:
                self.skills[skill_name] = Skill(
                    name=skill_name,
                    description=f"Skill: {skill_name}"
                )
                self.stats["skills_acquired"] += 1
            
            skill = self.skills[skill_name]
            skill.practice_count += 1
            skill.last_practiced = datetime.utcnow()
            
            if success:
                skill.success_count += 1
            
            # Update proficiency using learning curve
            success_rate = skill.success_count / skill.practice_count
            # Proficiency grows with practice (diminishing returns)
            practice_factor = 1 - math.exp(-skill.practice_count / 100)
            skill.proficiency = success_rate * practice_factor
    
    def get_skill_level(self, skill_name: str) -> float:
        """Get proficiency level for a skill."""
        with self._lock:
            skill = self.skills.get(skill_name)
            return skill.proficiency if skill else 0.0
    
    def get_top_skills(self, limit: int = 10) -> List[Skill]:
        """Get most proficient skills."""
        with self._lock:
            sorted_skills = sorted(
                self.skills.values(),
                key=lambda s: s.proficiency,
                reverse=True
            )
            return sorted_skills[:limit]
    
    # ==================== Preference Learning ====================
    
    def observe_preference(
        self,
        name: str,
        category: str,
        value: Any,
        confidence: float = 0.5
    ):
        """Record an observed preference."""
        pref_key = f"{category}:{name}"
        
        with self._lock:
            if pref_key in self.preferences:
                pref = self.preferences[pref_key]
                pref.observation_count += 1
                pref.last_observed = datetime.utcnow()
                
                # Update confidence with exponential moving average
                alpha = 0.3
                pref.confidence = alpha * confidence + (1 - alpha) * pref.confidence
                
                # Update value if confidence is high
                if confidence > pref.confidence:
                    pref.value = value
            else:
                self.preferences[pref_key] = Preference(
                    name=name,
                    category=category,
                    value=value,
                    confidence=confidence
                )
    
    def get_preference(
        self,
        name: str,
        category: str,
        default: Any = None
    ) -> Tuple[Any, float]:
        """Get a learned preference and its confidence."""
        pref_key = f"{category}:{name}"
        
        with self._lock:
            pref = self.preferences.get(pref_key)
            if pref and pref.confidence > 0.3:
                return pref.value, pref.confidence
        
        return default, 0.0
    
    def get_preferences_by_category(self, category: str) -> Dict[str, Any]:
        """Get all preferences in a category."""
        with self._lock:
            return {
                pref.name: pref.value
                for pref in self.preferences.values()
                if pref.category == category and pref.confidence > 0.3
            }
    
    # ==================== Continuous Improvement ====================
    
    def suggest_improvements(self) -> List[Dict[str, Any]]:
        """Analyze experiences and suggest improvements."""
        suggestions = []
        
        with self._lock:
            # Analyze negative feedback patterns
            negative_exps = [
                e for e in self.experiences
                if e.feedback == FeedbackType.NEGATIVE
            ]
            
            if negative_exps:
                # Group by action
                action_failures = defaultdict(int)
                for exp in negative_exps:
                    action_failures[exp.action] += 1
                
                for action, count in action_failures.items():
                    if count >= 3:
                        suggestions.append({
                            "type": "action_improvement",
                            "action": action,
                            "failure_count": count,
                            "suggestion": f"Review and improve '{action}' - failed {count} times"
                        })
            
            # Analyze skill deficiencies
            low_skills = [
                s for s in self.skills.values()
                if s.practice_count >= 5 and s.proficiency < 0.5
            ]
            
            for skill in low_skills:
                suggestions.append({
                    "type": "skill_development",
                    "skill": skill.name,
                    "proficiency": skill.proficiency,
                    "suggestion": f"Practice '{skill.name}' more - current proficiency: {skill.proficiency:.0%}"
                })
            
            # Analyze pattern effectiveness
            weak_patterns = [
                p for p in self.patterns.values()
                if p.usage_count >= 5 and p.success_rate < 0.5
            ]
            
            for pattern in weak_patterns:
                suggestions.append({
                    "type": "pattern_revision",
                    "pattern": pattern.pattern_id,
                    "success_rate": pattern.success_rate,
                    "suggestion": f"Revise pattern '{pattern.trigger}' -> '{pattern.response}'"
                })
        
        return suggestions
    
    def _start_background_learning(self):
        """Start background learning process."""
        def learn_loop():
            import time
            while True:
                time.sleep(300)  # Every 5 minutes
                self._extract_patterns()
                self._save_knowledge()
        
        thread = threading.Thread(target=learn_loop, daemon=True)
        thread.start()
    
    # ==================== Persistence ====================
    
    def _save_knowledge(self):
        """Save learned knowledge to disk."""
        try:
            # Save patterns
            patterns_path = os.path.join(self.storage_path, "patterns.json")
            with open(patterns_path, "w") as f:
                json.dump({
                    pid: {
                        "trigger": p.trigger,
                        "response": p.response,
                        "confidence": p.confidence,
                        "usage_count": p.usage_count,
                        "success_count": p.success_count
                    }
                    for pid, p in self.patterns.items()
                }, f, indent=2)
            
            # Save skills
            skills_path = os.path.join(self.storage_path, "skills.json")
            with open(skills_path, "w") as f:
                json.dump({
                    name: {
                        "description": s.description,
                        "proficiency": s.proficiency,
                        "practice_count": s.practice_count,
                        "success_count": s.success_count
                    }
                    for name, s in self.skills.items()
                }, f, indent=2)
            
            # Save preferences
            prefs_path = os.path.join(self.storage_path, "preferences.json")
            with open(prefs_path, "w") as f:
                json.dump({
                    key: {
                        "name": p.name,
                        "category": p.category,
                        "value": p.value,
                        "confidence": p.confidence
                    }
                    for key, p in self.preferences.items()
                }, f, indent=2)
            
            print(f"[LearningEngine] Saved {len(self.patterns)} patterns, {len(self.skills)} skills")
            
        except Exception as e:
            print(f"[LearningEngine] Error saving knowledge: {e}")
    
    def _load_knowledge(self):
        """Load learned knowledge from disk."""
        try:
            # Load patterns
            patterns_path = os.path.join(self.storage_path, "patterns.json")
            if os.path.exists(patterns_path):
                with open(patterns_path, "r") as f:
                    data = json.load(f)
                    for pid, pdata in data.items():
                        self.patterns[pid] = LearnedPattern(
                            pattern_id=pid,
                            pattern_type="context_action",
                            trigger=pdata["trigger"],
                            response=pdata["response"],
                            confidence=pdata["confidence"],
                            usage_count=pdata.get("usage_count", 0),
                            success_count=pdata.get("success_count", 0)
                        )
            
            # Load skills
            skills_path = os.path.join(self.storage_path, "skills.json")
            if os.path.exists(skills_path):
                with open(skills_path, "r") as f:
                    data = json.load(f)
                    for name, sdata in data.items():
                        self.skills[name] = Skill(
                            name=name,
                            description=sdata.get("description", ""),
                            proficiency=sdata.get("proficiency", 0),
                            practice_count=sdata.get("practice_count", 0),
                            success_count=sdata.get("success_count", 0)
                        )
            
            # Load preferences
            prefs_path = os.path.join(self.storage_path, "preferences.json")
            if os.path.exists(prefs_path):
                with open(prefs_path, "r") as f:
                    data = json.load(f)
                    for key, pdata in data.items():
                        self.preferences[key] = Preference(
                            name=pdata["name"],
                            category=pdata["category"],
                            value=pdata["value"],
                            confidence=pdata.get("confidence", 0.5)
                        )
            
            print(f"[LearningEngine] Loaded {len(self.patterns)} patterns, {len(self.skills)} skills")
            
        except Exception as e:
            print(f"[LearningEngine] Error loading knowledge: {e}")
    
    # ==================== Event Handlers ====================
    
    def _on_interaction(self, message):
        """Handle interaction completion event."""
        payload = message.payload
        
        self.record_experience(
            context=payload.get("context", {}),
            action=payload.get("action", "unknown"),
            result=payload.get("result"),
            metadata=payload.get("metadata", {})
        )
    
    def _on_feedback(self, message):
        """Handle feedback event."""
        payload = message.payload
        
        exp_id = payload.get("experience_id")
        feedback = payload.get("feedback")
        
        if exp_id and feedback:
            feedback_type = FeedbackType[feedback.upper()]
            self.add_feedback(exp_id, feedback_type)
    
    # ==================== Analytics ====================
    
    def get_learning_report(self) -> Dict[str, Any]:
        """Generate a learning report."""
        with self._lock:
            # Calculate learning velocity
            recent_exps = [
                e for e in self.experiences
                if e.timestamp > datetime.utcnow() - timedelta(hours=24)
            ]
            
            return {
                "total_experiences": self.stats["total_experiences"],
                "recent_experiences_24h": len(recent_exps),
                "patterns_learned": len(self.patterns),
                "skills_acquired": len(self.skills),
                "preferences_tracked": len(self.preferences),
                "positive_feedback_rate": (
                    self.stats["positive_feedback"] / 
                    max(1, self.stats["positive_feedback"] + self.stats["negative_feedback"])
                ),
                "top_skills": [
                    {"name": s.name, "proficiency": s.proficiency}
                    for s in self.get_top_skills(5)
                ],
                "improvement_suggestions": self.suggest_improvements()[:5]
            }
