# lam/behavior_trainer.py
# Behavior Trainer - Reinforcement learning and behavior shaping for the daemon

import json
import os
import time
import random
import math
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


class TrainingMode(Enum):
    """Training modes for behavior learning."""
    REINFORCEMENT = "reinforcement"     # Learn from rewards
    IMITATION = "imitation"             # Learn from demonstrations
    CURRICULUM = "curriculum"           # Structured curriculum learning
    SELF_PLAY = "self_play"             # Learn through self-practice
    INTERACTIVE = "interactive"         # Learn from real-time feedback
    OFFLINE = "offline"                 # Learn from logged experiences


class RewardType(Enum):
    """Types of reward signals."""
    SUCCESS = "success"                 # Task completed successfully
    PARTIAL = "partial"                 # Partial success
    FAILURE = "failure"                 # Task failed
    TIMEOUT = "timeout"                 # Task timed out
    FEEDBACK = "feedback"               # Explicit user feedback
    IMPLICIT = "implicit"               # Implicit signal (e.g., user continued)


@dataclass
class TrainingExample:
    """A single training example."""
    example_id: str
    input_text: str
    context: Dict[str, Any]
    target_action: Dict[str, Any]
    reward: float
    reward_type: RewardType
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "example_id": self.example_id,
            "input_text": self.input_text,
            "context": self.context,
            "target_action": self.target_action,
            "reward": self.reward,
            "reward_type": self.reward_type.value,
            "timestamp": self.timestamp
        }


@dataclass
class TrainingSession:
    """A training session."""
    session_id: str
    mode: TrainingMode
    started_at: str
    examples_trained: int = 0
    total_reward: float = 0.0
    policy_updates: int = 0
    ended_at: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        duration = 0
        if self.ended_at:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.ended_at)
            duration = (end - start).total_seconds()
            
        return {
            "session_id": self.session_id,
            "mode": self.mode.value,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_seconds": duration,
            "examples_trained": self.examples_trained,
            "avg_reward": self.total_reward / max(self.examples_trained, 1),
            "policy_updates": self.policy_updates,
            "metrics": self.metrics
        }


@dataclass
class Policy:
    """A learned policy (action selection strategy)."""
    policy_id: str
    name: str
    context_rules: Dict[str, Any]       # Rules for when to apply
    action_weights: Dict[str, float]    # Weights for different actions
    exploration_rate: float = 0.1
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    update_count: int = 0
    success_rate: float = 0.5
    
    def select_action(self, available_actions: List[str]) -> str:
        """Select an action using this policy."""
        # Exploration
        if random.random() < self.exploration_rate:
            return random.choice(available_actions)
            
        # Exploitation - weighted selection
        weighted = []
        for action in available_actions:
            weight = self.action_weights.get(action, 0.5)
            weighted.append((action, weight))
            
        total = sum(w for _, w in weighted)
        if total == 0:
            return random.choice(available_actions)
            
        r = random.random() * total
        cumulative = 0
        for action, weight in weighted:
            cumulative += weight
            if r <= cumulative:
                return action
                
        return weighted[-1][0]
    
    def update(self, action: str, reward: float, learning_rate: float = 0.1):
        """Update policy weights based on reward."""
        current = self.action_weights.get(action, 0.5)
        # Q-learning style update
        self.action_weights[action] = current + learning_rate * (reward - current)
        self.update_count += 1
        
    def to_dict(self) -> Dict:
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "context_rules": self.context_rules,
            "action_weights": self.action_weights,
            "exploration_rate": self.exploration_rate,
            "update_count": self.update_count,
            "success_rate": self.success_rate
        }


class BehaviorTrainer:
    """
    Behavior training system using reinforcement learning principles.
    
    Provides:
    - Reward-based learning from outcomes
    - Imitation learning from demonstrations
    - Curriculum learning with difficulty progression
    - Policy optimization and management
    - Training session management
    - Performance tracking and analysis
    """
    
    def __init__(
        self,
        lam_core=None,
        experience_memory=None,
        skill_tree=None,
        data_path: str = "data/lam/training"
    ):
        self.lam_core = lam_core
        self.experience_memory = experience_memory
        self.skill_tree = skill_tree
        self.data_path = data_path
        
        # Training data
        self.examples: List[TrainingExample] = []
        self.sessions: List[TrainingSession] = []
        self.active_session: Optional[TrainingSession] = None
        
        # Policies
        self.policies: Dict[str, Policy] = {}
        self.default_policy: Optional[str] = None
        
        # Curriculum
        self.curriculum_level = 1
        self.curriculum_stages: List[Dict] = []
        
        # Training parameters
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.batch_size = 32
        self.min_examples_for_update = 10
        
        # Statistics
        self.stats = {
            "total_examples": 0,
            "total_sessions": 0,
            "total_updates": 0,
            "best_reward": 0.0,
            "avg_reward": 0.0
        }
        
        os.makedirs(data_path, exist_ok=True)
        self._load_training_data()
        self._initialize_curriculum()
        print("[BehaviorTrainer] Initialized.")
        
    def _load_training_data(self):
        """Load training data from disk."""
        data_file = os.path.join(self.data_path, "training_data.json")
        if os.path.exists(data_file):
            try:
                with open(data_file, "r") as f:
                    data = json.load(f)
                    
                    for p in data.get("policies", []):
                        policy = Policy(
                            policy_id=p["policy_id"],
                            name=p["name"],
                            context_rules=p.get("context_rules", {}),
                            action_weights=p.get("action_weights", {}),
                            exploration_rate=p.get("exploration_rate", 0.1),
                            update_count=p.get("update_count", 0),
                            success_rate=p.get("success_rate", 0.5)
                        )
                        self.policies[policy.policy_id] = policy
                        
                    self.default_policy = data.get("default_policy")
                    self.curriculum_level = data.get("curriculum_level", 1)
                    self.stats = data.get("stats", self.stats)
                    
                print(f"[BehaviorTrainer] Loaded {len(self.policies)} policies")
            except Exception as e:
                print(f"[BehaviorTrainer] Error loading data: {e}")
                
    def _save_training_data(self):
        """Save training data to disk."""
        data_file = os.path.join(self.data_path, "training_data.json")
        data = {
            "policies": [p.to_dict() for p in self.policies.values()],
            "default_policy": self.default_policy,
            "curriculum_level": self.curriculum_level,
            "stats": self.stats,
            "saved_at": datetime.now().isoformat()
        }
        with open(data_file, "w") as f:
            json.dump(data, f, indent=2)
            
    def _initialize_curriculum(self):
        """Initialize curriculum learning stages."""
        self.curriculum_stages = [
            {
                "level": 1,
                "name": "Basic Responses",
                "description": "Simple input-response patterns",
                "focus_skills": ["lang_intent", "comm_respond"],
                "max_complexity": "atomic",
                "example_types": ["simple_query", "greeting", "basic_command"]
            },
            {
                "level": 2,
                "name": "Task Execution",
                "description": "Single-step task execution",
                "focus_skills": ["act_task", "act_scroll"],
                "max_complexity": "atomic",
                "example_types": ["scroll_trigger", "single_task"]
            },
            {
                "level": 3,
                "name": "Context Awareness",
                "description": "Context-dependent responses",
                "focus_skills": ["lang_context", "cog_analysis"],
                "max_complexity": "conditional",
                "example_types": ["contextual_query", "follow_up"]
            },
            {
                "level": 4,
                "name": "Multi-Step Planning",
                "description": "Multi-step task planning and execution",
                "focus_skills": ["cog_planning", "act_sequence"],
                "max_complexity": "composite",
                "example_types": ["multi_step_task", "goal_achievement"]
            },
            {
                "level": 5,
                "name": "XR Integration",
                "description": "AR/VR/XR specific behaviors",
                "focus_skills": ["xr_overlay", "xr_training", "xr_gesture"],
                "max_complexity": "adaptive",
                "example_types": ["xr_session", "training_delivery"]
            },
            {
                "level": 6,
                "name": "Advanced Reasoning",
                "description": "Complex reasoning and problem solving",
                "focus_skills": ["cog_logic", "know_integration"],
                "max_complexity": "adaptive",
                "example_types": ["problem_solving", "knowledge_synthesis"]
            },
            {
                "level": 7,
                "name": "Self-Improvement",
                "description": "Meta-learning and self-optimization",
                "focus_skills": ["cog_learning", "meta_optimize"],
                "max_complexity": "adaptive",
                "example_types": ["self_reflection", "behavior_adaptation"]
            }
        ]
        
    def create_policy(
        self,
        name: str,
        context_rules: Dict[str, Any],
        initial_weights: Optional[Dict[str, float]] = None
    ) -> Policy:
        """Create a new policy."""
        policy_id = f"policy_{int(time.time())}_{name.lower().replace(' ', '_')}"
        
        policy = Policy(
            policy_id=policy_id,
            name=name,
            context_rules=context_rules,
            action_weights=initial_weights or {}
        )
        
        self.policies[policy_id] = policy
        
        if self.default_policy is None:
            self.default_policy = policy_id
            
        self._save_training_data()
        print(f"[BehaviorTrainer] Created policy: {name}")
        return policy
    
    def start_session(self, mode: str = "reinforcement") -> TrainingSession:
        """Start a new training session."""
        if self.active_session:
            self.end_session()
            
        session_id = f"train_{int(time.time())}"
        
        self.active_session = TrainingSession(
            session_id=session_id,
            mode=TrainingMode(mode),
            started_at=datetime.now().isoformat()
        )
        
        print(f"[BehaviorTrainer] Started {mode} training session: {session_id}")
        return self.active_session
    
    def end_session(self) -> Optional[Dict]:
        """End the current training session."""
        if not self.active_session:
            return None
            
        self.active_session.ended_at = datetime.now().isoformat()
        self.sessions.append(self.active_session)
        self.stats["total_sessions"] += 1
        
        summary = self.active_session.to_dict()
        
        # Save session log
        self._save_session_log(self.active_session)
        
        print(f"[BehaviorTrainer] Session ended: {summary['examples_trained']} examples, avg reward: {summary['avg_reward']:.2f}")
        
        self.active_session = None
        self._save_training_data()
        
        return summary
    
    def _save_session_log(self, session: TrainingSession):
        """Save session log to file."""
        log_dir = os.path.join(self.data_path, "sessions")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"{session.session_id}.json")
        with open(log_file, "w") as f:
            json.dump(session.to_dict(), f, indent=2)
            
    def add_training_example(
        self,
        input_text: str,
        target_action: Dict[str, Any],
        reward: float,
        reward_type: str = "success",
        context: Optional[Dict] = None
    ) -> TrainingExample:
        """
        Add a training example.
        
        Args:
            input_text: Input that should trigger the action
            target_action: The correct action to take
            reward: Reward value for this example
            reward_type: Type of reward signal
            context: Optional context
            
        Returns:
            Created TrainingExample
        """
        example = TrainingExample(
            example_id=f"ex_{int(time.time() * 1000)}",
            input_text=input_text,
            context=context or {},
            target_action=target_action,
            reward=reward,
            reward_type=RewardType(reward_type)
        )
        
        self.examples.append(example)
        self.stats["total_examples"] += 1
        
        if self.active_session:
            self.active_session.examples_trained += 1
            self.active_session.total_reward += reward
            
        # Trigger learning if enough examples
        if len(self.examples) >= self.min_examples_for_update:
            self._train_batch()
            
        return example
    
    def provide_reward(
        self,
        action_taken: Dict[str, Any],
        reward: float,
        context: Dict[str, Any],
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Provide reward signal for an action.
        
        Args:
            action_taken: The action that was taken
            reward: Reward value (-1 to 1)
            context: Context at the time
            feedback: Optional text feedback
            
        Returns:
            Update result
        """
        # Normalize reward to -1 to 1
        reward = max(-1.0, min(1.0, reward))
        
        # Update relevant policy
        policy = self._get_active_policy(context)
        if policy:
            action_type = action_taken.get("type", "unknown")
            policy.update(action_type, reward, self.learning_rate)
            
            # Update success rate
            if reward > 0:
                policy.success_rate = 0.95 * policy.success_rate + 0.05
            else:
                policy.success_rate = 0.95 * policy.success_rate
                
        # Update LAM core if available
        if self.lam_core:
            pattern_id = action_taken.get("pattern_id")
            if pattern_id:
                success = reward > 0
                self.lam_core.reinforce_pattern(pattern_id, success, reward)
                
        # Record in experience memory if available
        if self.experience_memory:
            self.experience_memory.record(
                input_text=context.get("last_input", ""),
                context=context,
                action_taken=action_taken,
                outcome="success" if reward > 0 else "failure",
                reward=reward,
                feedback=feedback
            )
            
        # Update skill tree if available
        if self.skill_tree:
            action_type = action_taken.get("type", "")
            skill_mapping = {
                "scroll": "act_scroll",
                "response": "lang_generation",
                "query": "know_retrieval",
                "task": "act_task",
                "plan": "cog_planning",
                "xr_action": "xr_root"
            }
            skill_id = skill_mapping.get(action_type)
            if skill_id:
                xp = int(50 * (reward + 1))  # 0-100 XP based on reward
                self.skill_tree.train_skill(skill_id, xp, success=reward > 0)
                
        # Track stats
        if self.active_session:
            self.active_session.total_reward += reward
            
        self.stats["avg_reward"] = (
            self.stats["avg_reward"] * 0.99 + reward * 0.01
        )
        if reward > self.stats["best_reward"]:
            self.stats["best_reward"] = reward
            
        self._save_training_data()
        
        return {
            "reward": reward,
            "policy_updated": policy.policy_id if policy else None,
            "current_success_rate": policy.success_rate if policy else 0
        }
    
    def _get_active_policy(self, context: Dict) -> Optional[Policy]:
        """Get the policy that applies to the current context."""
        # Find best matching policy
        for policy in self.policies.values():
            rules = policy.context_rules
            if not rules:  # Default policy
                continue
                
            matches = True
            for key, value in rules.items():
                if context.get(key) != value:
                    matches = False
                    break
                    
            if matches:
                return policy
                
        # Return default policy
        if self.default_policy and self.default_policy in self.policies:
            return self.policies[self.default_policy]
            
        return None
    
    def _train_batch(self):
        """Train on a batch of examples."""
        if len(self.examples) < self.batch_size:
            batch = self.examples
        else:
            batch = random.sample(self.examples, self.batch_size)
            
        # Group by context
        context_groups = defaultdict(list)
        for example in batch:
            context_key = str(sorted(example.context.items()))
            context_groups[context_key].append(example)
            
        # Update policies for each context
        for context_key, examples in context_groups.items():
            if examples:
                context = examples[0].context
                policy = self._get_active_policy(context)
                
                if policy:
                    for example in examples:
                        action_type = example.target_action.get("type", "unknown")
                        policy.update(action_type, example.reward, self.learning_rate)
                        
        # Train LAM core if available
        if self.lam_core:
            lam_examples = []
            for example in batch:
                if example.reward > 0.5:  # Only positive examples
                    lam_examples.append({
                        "input": example.input_text,
                        "action_type": example.target_action.get("type", "response"),
                        "action_params": example.target_action.get("params", {}),
                        "context_requirements": example.context
                    })
                    
            if lam_examples:
                self.lam_core.train_from_examples(lam_examples)
                
        # Clear processed examples
        self.examples = self.examples[-100:]  # Keep last 100
        
        self.stats["total_updates"] += 1
        if self.active_session:
            self.active_session.policy_updates += 1
            
        print(f"[BehaviorTrainer] Trained on {len(batch)} examples")
    
    def run_imitation_learning(
        self,
        demonstrations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Learn from demonstrations.
        
        Args:
            demonstrations: List of {input, action, context} demonstrations
            
        Returns:
            Learning results
        """
        self.start_session(mode="imitation")
        
        learned = 0
        for demo in demonstrations:
            input_text = demo.get("input", "")
            action = demo.get("action", {})
            context = demo.get("context", {})
            
            # Create training example with high reward
            self.add_training_example(
                input_text=input_text,
                target_action=action,
                reward=0.9,  # Demonstrations get high reward
                reward_type="feedback",
                context=context
            )
            
            # Also learn directly in LAM
            if self.lam_core:
                self.lam_core.learn_pattern(
                    input_pattern=input_text,
                    action_type=action.get("type", "response"),
                    action_params=action.get("params", {}),
                    context_requirements=context,
                    initial_confidence=0.8
                )
                
            learned += 1
            
        summary = self.end_session()
        
        return {
            "demonstrations_learned": learned,
            "session": summary
        }
    
    def run_curriculum_training(
        self,
        examples_per_level: int = 20,
        max_level: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run curriculum learning through progressive stages.
        
        Args:
            examples_per_level: Examples to train at each level
            max_level: Maximum curriculum level to reach
            
        Returns:
            Training results
        """
        self.start_session(mode="curriculum")
        max_level = max_level or len(self.curriculum_stages)
        
        results = {
            "levels_completed": [],
            "total_examples": 0,
            "final_level": self.curriculum_level
        }
        
        while self.curriculum_level <= max_level:
            stage = next(
                (s for s in self.curriculum_stages if s["level"] == self.curriculum_level),
                None
            )
            
            if not stage:
                break
                
            print(f"[BehaviorTrainer] Curriculum Level {self.curriculum_level}: {stage['name']}")
            
            # Generate synthetic training examples for this level
            # In a real system, these would come from data or be generated
            level_reward = 0.0
            for i in range(examples_per_level):
                # Simulated training (placeholder for actual curriculum data)
                synthetic_reward = random.uniform(0.4, 0.9)
                level_reward += synthetic_reward
                
                if self.skill_tree:
                    for skill_id in stage["focus_skills"]:
                        self.skill_tree.train_skill(skill_id, 10, success=synthetic_reward > 0.5)
                        
            avg_reward = level_reward / examples_per_level
            results["levels_completed"].append({
                "level": self.curriculum_level,
                "name": stage["name"],
                "avg_reward": avg_reward
            })
            
            # Advance if performance is good enough
            if avg_reward >= 0.6:
                self.curriculum_level += 1
                print(f"[BehaviorTrainer] Advanced to level {self.curriculum_level}")
            else:
                print(f"[BehaviorTrainer] Staying at level {self.curriculum_level} (avg reward: {avg_reward:.2f})")
                break
                
            results["total_examples"] += examples_per_level
            
        results["final_level"] = self.curriculum_level
        
        summary = self.end_session()
        results["session"] = summary
        
        self._save_training_data()
        return results
    
    def run_experience_replay(self, batch_size: int = 32) -> Dict[str, Any]:
        """
        Run experience replay learning from memory.
        
        Args:
            batch_size: Number of experiences to replay
            
        Returns:
            Replay results
        """
        if not self.experience_memory:
            return {"error": "Experience memory not available"}
            
        self.start_session(mode="offline")
        
        # Use LAM's experience replay
        result = {}
        if self.lam_core:
            result = self.lam_core.experience_replay(batch_size)
            
        # Also analyze experiences for patterns
        analysis = self.experience_memory.analyze_for_patterns()
        
        # Learn from failure patterns
        for action_type, fail_count in analysis.get("areas_for_improvement", [])[:5]:
            if isinstance(action_type, dict):
                action = action_type.get("action", "")
                # Could trigger focused training for this action type
                print(f"[BehaviorTrainer] Identified improvement area: {action}")
                
        summary = self.end_session()
        
        return {
            "replay_result": result,
            "pattern_analysis": analysis,
            "session": summary
        }
    
    def get_current_curriculum_stage(self) -> Dict[str, Any]:
        """Get the current curriculum stage."""
        stage = next(
            (s for s in self.curriculum_stages if s["level"] == self.curriculum_level),
            None
        )
        return stage or {"level": self.curriculum_level, "name": "Unknown"}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get training statistics."""
        policy_stats = []
        for policy in self.policies.values():
            policy_stats.append({
                "name": policy.name,
                "updates": policy.update_count,
                "success_rate": policy.success_rate
            })
            
        return {
            **self.stats,
            "active_session": self.active_session.to_dict() if self.active_session else None,
            "policies": policy_stats,
            "curriculum_level": self.curriculum_level,
            "total_policies": len(self.policies),
            "pending_examples": len(self.examples)
        }
    
    def export_training_data(self) -> Dict:
        """Export all training data."""
        return {
            "policies": [p.to_dict() for p in self.policies.values()],
            "curriculum_level": self.curriculum_level,
            "curriculum_stages": self.curriculum_stages,
            "stats": self.stats,
            "sessions_count": len(self.sessions)
        }
