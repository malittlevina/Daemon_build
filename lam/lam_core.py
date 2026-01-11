# lam/lam_core.py
# Language-Action Model Core Engine - The learning brain of the daemon

import json
import os
import time
import math
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib


class LearningMode(Enum):
    """LAM learning modes."""
    SUPERVISED = "supervised"           # Learn from labeled examples
    REINFORCEMENT = "reinforcement"     # Learn from rewards/penalties
    IMITATION = "imitation"             # Learn by observing demonstrations
    SELF_SUPERVISED = "self_supervised" # Learn from self-generated tasks
    TRANSFER = "transfer"               # Transfer learning from other domains


class ActionType(Enum):
    """Types of actions the LAM can learn and execute."""
    SCROLL = "scroll"                   # Invoke a scroll/ritual
    RESPONSE = "response"               # Generate a response
    QUERY = "query"                     # Query knowledge base
    TASK = "task"                       # Execute a task
    PLAN = "plan"                       # Create a multi-step plan
    DELEGATE = "delegate"               # Delegate to another system
    OBSERVE = "observe"                 # Passive observation
    LEARN = "learn"                     # Meta-learning action
    XR_ACTION = "xr_action"             # XR-specific action


@dataclass
class LearnedPattern:
    """Represents a learned input-action pattern."""
    pattern_id: str
    input_pattern: str                  # Input pattern (can include wildcards)
    action_type: ActionType
    action_params: Dict[str, Any]
    confidence: float = 0.5
    success_count: int = 0
    failure_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_used: str = field(default_factory=lambda: datetime.now().isoformat())
    context_requirements: Dict[str, Any] = field(default_factory=dict)
    embeddings: List[float] = field(default_factory=list)  # For semantic matching
    
    def update_stats(self, success: bool):
        """Update pattern statistics based on outcome."""
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.last_used = datetime.now().isoformat()
        # Update confidence using exponential moving average
        outcome = 1.0 if success else 0.0
        self.confidence = 0.9 * self.confidence + 0.1 * outcome
        
    def get_success_rate(self) -> float:
        """Get the success rate of this pattern."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.5  # Default uncertainty
        return self.success_count / total
    
    def to_dict(self) -> Dict:
        return {
            "pattern_id": self.pattern_id,
            "input_pattern": self.input_pattern,
            "action_type": self.action_type.value,
            "action_params": self.action_params,
            "confidence": self.confidence,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.get_success_rate(),
            "created_at": self.created_at,
            "last_used": self.last_used
        }


@dataclass
class Experience:
    """Represents a single learning experience/episode."""
    experience_id: str
    input_text: str
    context: Dict[str, Any]
    action_taken: Dict[str, Any]
    outcome: str                        # "success", "failure", "partial", "unknown"
    reward: float                       # Numerical reward signal
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    feedback: Optional[str] = None      # Optional human feedback
    duration_ms: int = 0
    follow_up_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "experience_id": self.experience_id,
            "input_text": self.input_text,
            "context": self.context,
            "action_taken": self.action_taken,
            "outcome": self.outcome,
            "reward": self.reward,
            "timestamp": self.timestamp,
            "feedback": self.feedback
        }


class LAMCore:
    """
    Language-Action Model Core Engine.
    
    The LAM is the daemon's learning center - it maps language inputs to actions
    and continuously improves through experience, feedback, and self-reflection.
    
    Key Capabilities:
    - Pattern learning from input-action pairs
    - Reinforcement learning from outcomes
    - Experience replay for offline learning
    - Skill composition and transfer
    - Context-aware action selection
    - Confidence-based exploration/exploitation
    """
    
    def __init__(self, data_path: str = "data/lam"):
        self.data_path = data_path
        self.patterns: Dict[str, LearnedPattern] = {}
        self.experiences: List[Experience] = []
        self.action_handlers: Dict[str, Callable] = {}
        self.learning_rate = 0.1
        self.exploration_rate = 0.2      # Probability of trying new actions
        self.min_confidence = 0.3        # Minimum confidence to use a pattern
        self.context_weight = 0.3        # Weight of context in matching
        self.statistics = {
            "total_actions": 0,
            "successful_actions": 0,
            "patterns_learned": 0,
            "experiences_recorded": 0,
            "training_sessions": 0
        }
        
        os.makedirs(data_path, exist_ok=True)
        self._load_patterns()
        self._load_experiences()
        print("[LAMCore] Language-Action Model initialized.")
        
    def _load_patterns(self):
        """Load learned patterns from disk."""
        patterns_file = os.path.join(self.data_path, "patterns.json")
        if os.path.exists(patterns_file):
            try:
                with open(patterns_file, "r") as f:
                    data = json.load(f)
                    for p in data.get("patterns", []):
                        pattern = LearnedPattern(
                            pattern_id=p["pattern_id"],
                            input_pattern=p["input_pattern"],
                            action_type=ActionType(p["action_type"]),
                            action_params=p["action_params"],
                            confidence=p.get("confidence", 0.5),
                            success_count=p.get("success_count", 0),
                            failure_count=p.get("failure_count", 0),
                            created_at=p.get("created_at", datetime.now().isoformat()),
                            last_used=p.get("last_used", datetime.now().isoformat()),
                            context_requirements=p.get("context_requirements", {})
                        )
                        self.patterns[pattern.pattern_id] = pattern
                print(f"[LAMCore] Loaded {len(self.patterns)} patterns")
            except Exception as e:
                print(f"[LAMCore] Error loading patterns: {e}")
                
    def _save_patterns(self):
        """Save learned patterns to disk."""
        patterns_file = os.path.join(self.data_path, "patterns.json")
        data = {
            "patterns": [p.to_dict() for p in self.patterns.values()],
            "saved_at": datetime.now().isoformat(),
            "statistics": self.statistics
        }
        with open(patterns_file, "w") as f:
            json.dump(data, f, indent=2)
            
    def _load_experiences(self):
        """Load recent experiences from disk."""
        exp_file = os.path.join(self.data_path, "experiences.json")
        if os.path.exists(exp_file):
            try:
                with open(exp_file, "r") as f:
                    data = json.load(f)
                    # Load last 1000 experiences
                    for e in data.get("experiences", [])[-1000:]:
                        exp = Experience(
                            experience_id=e["experience_id"],
                            input_text=e["input_text"],
                            context=e["context"],
                            action_taken=e["action_taken"],
                            outcome=e["outcome"],
                            reward=e["reward"],
                            timestamp=e.get("timestamp", ""),
                            feedback=e.get("feedback")
                        )
                        self.experiences.append(exp)
                print(f"[LAMCore] Loaded {len(self.experiences)} experiences")
            except Exception as e:
                print(f"[LAMCore] Error loading experiences: {e}")
                
    def _save_experiences(self):
        """Save experiences to disk."""
        exp_file = os.path.join(self.data_path, "experiences.json")
        data = {
            "experiences": [e.to_dict() for e in self.experiences[-1000:]],
            "saved_at": datetime.now().isoformat()
        }
        with open(exp_file, "w") as f:
            json.dump(data, f, indent=2)
            
    def register_action_handler(self, action_type: str, handler: Callable):
        """Register a handler for a specific action type."""
        self.action_handlers[action_type] = handler
        print(f"[LAMCore] Registered handler for action type: {action_type}")
        
    def _generate_pattern_id(self, input_pattern: str) -> str:
        """Generate a unique pattern ID."""
        hash_input = f"{input_pattern}_{time.time()}"
        return f"pat_{hashlib.md5(hash_input.encode()).hexdigest()[:12]}"
    
    def _compute_similarity(self, input_text: str, pattern: str) -> float:
        """
        Compute similarity between input text and a pattern.
        Uses a combination of exact matching, keyword overlap, and fuzzy matching.
        """
        input_lower = input_text.lower()
        pattern_lower = pattern.lower()
        
        # Exact match
        if input_lower == pattern_lower:
            return 1.0
            
        # Check if pattern is contained in input
        if pattern_lower in input_lower:
            return 0.9
            
        # Keyword overlap
        input_words = set(input_lower.split())
        pattern_words = set(pattern_lower.split())
        
        if not pattern_words:
            return 0.0
            
        overlap = len(input_words & pattern_words)
        keyword_sim = overlap / len(pattern_words)
        
        # Prefix matching for partial inputs
        prefix_sim = 0.0
        for word in input_words:
            for pword in pattern_words:
                if pword.startswith(word) or word.startswith(pword):
                    prefix_sim += 0.5 / len(pattern_words)
                    
        return max(keyword_sim, prefix_sim)
    
    def _match_context(self, current_context: Dict, required_context: Dict) -> float:
        """Check how well current context matches required context."""
        if not required_context:
            return 1.0
            
        matches = 0
        total = len(required_context)
        
        for key, value in required_context.items():
            if key in current_context:
                if current_context[key] == value:
                    matches += 1
                elif value == "*":  # Wildcard - just needs to exist
                    matches += 1
                    
        return matches / total if total > 0 else 1.0
    
    def find_matching_patterns(
        self,
        input_text: str,
        context: Dict[str, Any],
        top_k: int = 5
    ) -> List[Tuple[LearnedPattern, float]]:
        """
        Find patterns that match the input text and context.
        
        Returns list of (pattern, score) tuples sorted by score.
        """
        matches = []
        
        for pattern in self.patterns.values():
            # Compute text similarity
            text_sim = self._compute_similarity(input_text, pattern.input_pattern)
            
            # Compute context match
            context_match = self._match_context(context, pattern.context_requirements)
            
            # Combined score
            score = (1 - self.context_weight) * text_sim + self.context_weight * context_match
            
            # Weight by confidence
            score *= pattern.confidence
            
            if score > 0.1:  # Minimum threshold
                matches.append((pattern, score))
                
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:top_k]
    
    def learn_pattern(
        self,
        input_pattern: str,
        action_type: str,
        action_params: Dict[str, Any],
        context_requirements: Optional[Dict] = None,
        initial_confidence: float = 0.5
    ) -> LearnedPattern:
        """
        Learn a new input-action pattern.
        
        Args:
            input_pattern: The input pattern to match
            action_type: Type of action to take
            action_params: Parameters for the action
            context_requirements: Required context for this pattern
            initial_confidence: Starting confidence level
            
        Returns:
            The created LearnedPattern
        """
        pattern_id = self._generate_pattern_id(input_pattern)
        
        pattern = LearnedPattern(
            pattern_id=pattern_id,
            input_pattern=input_pattern,
            action_type=ActionType(action_type),
            action_params=action_params,
            confidence=initial_confidence,
            context_requirements=context_requirements or {}
        )
        
        self.patterns[pattern_id] = pattern
        self.statistics["patterns_learned"] += 1
        self._save_patterns()
        
        print(f"[LAMCore] Learned new pattern: '{input_pattern}' -> {action_type}")
        return pattern
    
    def reinforce_pattern(self, pattern_id: str, success: bool, reward: float = None):
        """
        Reinforce a pattern based on outcome.
        
        Args:
            pattern_id: ID of the pattern to reinforce
            success: Whether the action was successful
            reward: Optional numerical reward (overrides success boolean)
        """
        if pattern_id not in self.patterns:
            return
            
        pattern = self.patterns[pattern_id]
        pattern.update_stats(success)
        
        # Apply reward-based learning if provided
        if reward is not None:
            # Adjust confidence based on reward
            adjustment = self.learning_rate * (reward - 0.5)  # Centered around 0.5
            pattern.confidence = max(0.1, min(1.0, pattern.confidence + adjustment))
            
        self._save_patterns()
        print(f"[LAMCore] Reinforced pattern {pattern_id}: confidence={pattern.confidence:.2f}")
        
    def record_experience(
        self,
        input_text: str,
        context: Dict[str, Any],
        action_taken: Dict[str, Any],
        outcome: str,
        reward: float,
        feedback: Optional[str] = None
    ) -> Experience:
        """
        Record an experience for later learning.
        
        Args:
            input_text: The input that triggered the action
            context: The context at the time
            action_taken: The action that was taken
            outcome: "success", "failure", "partial", "unknown"
            reward: Numerical reward value
            feedback: Optional feedback string
            
        Returns:
            The recorded Experience
        """
        exp_id = f"exp_{int(time.time() * 1000)}"
        
        experience = Experience(
            experience_id=exp_id,
            input_text=input_text,
            context=context,
            action_taken=action_taken,
            outcome=outcome,
            reward=reward,
            feedback=feedback
        )
        
        self.experiences.append(experience)
        self.statistics["experiences_recorded"] += 1
        
        # Trim old experiences
        if len(self.experiences) > 2000:
            self.experiences = self.experiences[-1000:]
            
        self._save_experiences()
        return experience
    
    def select_action(
        self,
        input_text: str,
        context: Dict[str, Any]
    ) -> Tuple[Optional[Dict], Optional[str], float]:
        """
        Select the best action for the given input and context.
        
        Uses exploration/exploitation trade-off based on confidence levels.
        
        Args:
            input_text: The input text
            context: Current context
            
        Returns:
            Tuple of (action_dict, pattern_id, confidence)
        """
        import random
        
        # Find matching patterns
        matches = self.find_matching_patterns(input_text, context)
        
        if not matches:
            return None, None, 0.0
            
        # Exploration: sometimes try lower-ranked options
        if random.random() < self.exploration_rate and len(matches) > 1:
            # Weighted random selection
            weights = [m[1] for m in matches]
            total = sum(weights)
            if total > 0:
                probs = [w / total for w in weights]
                idx = random.choices(range(len(matches)), weights=probs)[0]
                pattern, score = matches[idx]
            else:
                pattern, score = matches[0]
        else:
            # Exploitation: use best match
            pattern, score = matches[0]
            
        # Check minimum confidence
        if score < self.min_confidence:
            return None, None, score
            
        action = {
            "type": pattern.action_type.value,
            "params": pattern.action_params,
            "pattern_id": pattern.pattern_id
        }
        
        self.statistics["total_actions"] += 1
        return action, pattern.pattern_id, score
    
    def execute_action(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[Any, bool, float]:
        """
        Execute an action using registered handlers.
        
        Args:
            action: Action dictionary with type and params
            context: Current context
            
        Returns:
            Tuple of (result, success, reward)
        """
        action_type = action.get("type")
        params = action.get("params", {})
        
        if action_type not in self.action_handlers:
            print(f"[LAMCore] No handler for action type: {action_type}")
            return None, False, -0.5
            
        try:
            handler = self.action_handlers[action_type]
            result = handler(params, context)
            
            # Assume success if no exception
            success = True
            reward = 0.7  # Default positive reward
            
            self.statistics["successful_actions"] += 1
            return result, success, reward
            
        except Exception as e:
            print(f"[LAMCore] Action execution error: {e}")
            return None, False, -0.5
    
    def process_input(
        self,
        input_text: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main entry point - process input and return action result.
        
        Args:
            input_text: User input text
            context: Current symbolic context
            
        Returns:
            Result dictionary with action taken and outcome
        """
        start_time = time.time()
        
        # Select action
        action, pattern_id, confidence = self.select_action(input_text, context)
        
        if action is None:
            # No matching pattern - return for fallback handling
            return {
                "matched": False,
                "confidence": confidence,
                "message": "[LAM] No matching action pattern found."
            }
            
        # Execute action
        result, success, reward = self.execute_action(action, context)
        
        # Reinforce pattern
        if pattern_id:
            self.reinforce_pattern(pattern_id, success, reward)
            
        # Record experience
        self.record_experience(
            input_text=input_text,
            context=context,
            action_taken=action,
            outcome="success" if success else "failure",
            reward=reward
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return {
            "matched": True,
            "action": action,
            "result": result,
            "success": success,
            "reward": reward,
            "confidence": confidence,
            "pattern_id": pattern_id,
            "duration_ms": duration_ms
        }
    
    def train_from_examples(
        self,
        examples: List[Dict[str, Any]],
        learning_mode: str = "supervised"
    ) -> Dict[str, Any]:
        """
        Train the LAM from a list of examples.
        
        Args:
            examples: List of {"input": str, "action_type": str, "action_params": dict}
            learning_mode: Type of learning to apply
            
        Returns:
            Training statistics
        """
        learned = 0
        updated = 0
        
        for example in examples:
            input_pattern = example.get("input")
            action_type = example.get("action_type")
            action_params = example.get("action_params", {})
            context_req = example.get("context_requirements", {})
            
            if not input_pattern or not action_type:
                continue
                
            # Check if similar pattern exists
            existing = None
            for p in self.patterns.values():
                if self._compute_similarity(input_pattern, p.input_pattern) > 0.9:
                    existing = p
                    break
                    
            if existing:
                # Update existing pattern
                existing.action_params.update(action_params)
                existing.confidence = min(1.0, existing.confidence + 0.1)
                updated += 1
            else:
                # Learn new pattern
                self.learn_pattern(
                    input_pattern=input_pattern,
                    action_type=action_type,
                    action_params=action_params,
                    context_requirements=context_req
                )
                learned += 1
                
        self.statistics["training_sessions"] += 1
        self._save_patterns()
        
        print(f"[LAMCore] Training complete: {learned} new patterns, {updated} updated")
        return {
            "learned": learned,
            "updated": updated,
            "total_patterns": len(self.patterns)
        }
    
    def experience_replay(self, batch_size: int = 32) -> Dict[str, Any]:
        """
        Perform experience replay learning from recorded experiences.
        
        Samples experiences and reinforces patterns based on outcomes.
        
        Args:
            batch_size: Number of experiences to replay
            
        Returns:
            Replay statistics
        """
        import random
        
        if len(self.experiences) < batch_size:
            batch = self.experiences
        else:
            batch = random.sample(self.experiences, batch_size)
            
        reinforced = 0
        new_patterns = 0
        
        for exp in batch:
            # Find pattern that was used
            action = exp.action_taken
            pattern_id = action.get("pattern_id") if action else None
            
            if pattern_id and pattern_id in self.patterns:
                # Reinforce existing pattern
                success = exp.outcome == "success"
                self.reinforce_pattern(pattern_id, success, exp.reward)
                reinforced += 1
            elif exp.outcome == "success" and exp.reward > 0.5:
                # Learn from successful experience without pattern
                self.learn_pattern(
                    input_pattern=exp.input_text,
                    action_type=action.get("type", "response"),
                    action_params=action.get("params", {}),
                    initial_confidence=0.6
                )
                new_patterns += 1
                
        print(f"[LAMCore] Experience replay: {reinforced} reinforced, {new_patterns} new patterns")
        return {
            "experiences_replayed": len(batch),
            "reinforced": reinforced,
            "new_patterns": new_patterns
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get LAM statistics."""
        return {
            **self.statistics,
            "total_patterns": len(self.patterns),
            "total_experiences": len(self.experiences),
            "avg_pattern_confidence": sum(p.confidence for p in self.patterns.values()) / len(self.patterns) if self.patterns else 0,
            "exploration_rate": self.exploration_rate,
            "learning_rate": self.learning_rate
        }
    
    def export_patterns(self) -> List[Dict]:
        """Export all patterns for inspection or transfer."""
        return [p.to_dict() for p in self.patterns.values()]
    
    def import_patterns(self, patterns_data: List[Dict], merge: bool = True) -> int:
        """
        Import patterns from external source.
        
        Args:
            patterns_data: List of pattern dictionaries
            merge: If True, merge with existing. If False, replace.
            
        Returns:
            Number of patterns imported
        """
        if not merge:
            self.patterns.clear()
            
        imported = 0
        for p in patterns_data:
            try:
                pattern = LearnedPattern(
                    pattern_id=p.get("pattern_id", self._generate_pattern_id(p["input_pattern"])),
                    input_pattern=p["input_pattern"],
                    action_type=ActionType(p["action_type"]),
                    action_params=p["action_params"],
                    confidence=p.get("confidence", 0.5),
                    success_count=p.get("success_count", 0),
                    failure_count=p.get("failure_count", 0),
                    context_requirements=p.get("context_requirements", {})
                )
                self.patterns[pattern.pattern_id] = pattern
                imported += 1
            except Exception as e:
                print(f"[LAMCore] Failed to import pattern: {e}")
                
        self._save_patterns()
        print(f"[LAMCore] Imported {imported} patterns")
        return imported
