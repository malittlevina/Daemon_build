# lam/lam_planner.py
# LAM Planner - Unified Language-Action Model interface with learning capabilities

import datetime
import os
from typing import Dict, List, Optional, Any, Tuple

# Import LAM components
from lam.lam_core import LAMCore, ActionType
from lam.action_registry import ActionRegistry, ActionCategory
from lam.experience_memory import ExperienceMemory
from lam.skill_tree import SkillTree
from lam.behavior_trainer import BehaviorTrainer
from lam.symbolic_state import symbolic_state, update_state_with_input, update_xr_state


class LAMPlanner:
    """
    Unified LAM Planner - Orchestrates all LAM subsystems.
    
    This is the main interface for the daemon's learning and action planning.
    
    Capabilities:
    - Pattern-based action selection
    - Reinforcement learning from outcomes
    - Episodic memory and recall
    - Skill progression and tracking
    - Curriculum-based training
    - Experience replay
    """
    
    def __init__(self, data_path: str = "data/lam"):
        self.data_path = data_path
        os.makedirs(data_path, exist_ok=True)
        
        # Initialize all subsystems
        self.core = LAMCore(data_path=data_path)
        self.registry = ActionRegistry(data_path=data_path)
        self.memory = ExperienceMemory(data_path=os.path.join(data_path, "memory"))
        self.skills = SkillTree(data_path=os.path.join(data_path, "skills"))
        self.trainer = BehaviorTrainer(
            lam_core=self.core,
            experience_memory=self.memory,
            skill_tree=self.skills,
            data_path=os.path.join(data_path, "training")
        )
        
        # Intent history
        self.last_intents: List[Dict] = []
        
        # Register action handlers
        self._register_default_handlers()
        
        print("[LAMPlanner] Initialized with all subsystems.")
        
    def _register_default_handlers(self):
        """Register default action handlers."""
        
        def handle_scroll(params: Dict, context: Dict) -> str:
            scroll_name = params.get("scroll", params.get("name", ""))
            return f"[LAM] Invoking scroll: {scroll_name}"
            
        def handle_response(params: Dict, context: Dict) -> str:
            text = params.get("text", params.get("response", ""))
            return text or "[LAM] Generated response."
            
        def handle_query(params: Dict, context: Dict) -> str:
            query = params.get("query", "")
            return f"[LAM] Querying knowledge: {query}"
            
        def handle_task(params: Dict, context: Dict) -> str:
            task = params.get("description", params.get("task", ""))
            return f"[LAM] Executing task: {task}"
            
        def handle_plan(params: Dict, context: Dict) -> str:
            goal = params.get("goal", "")
            return f"[LAM] Creating plan for: {goal}"
            
        def handle_xr(params: Dict, context: Dict) -> str:
            action = params.get("xr_action", params.get("action", ""))
            return f"[LAM] XR action: {action}"
            
        def handle_learn(params: Dict, context: Dict) -> str:
            topic = params.get("topic", "")
            return f"[LAM] Learning about: {topic}"
            
        # Register handlers
        self.core.register_action_handler("scroll", handle_scroll)
        self.core.register_action_handler("response", handle_response)
        self.core.register_action_handler("query", handle_query)
        self.core.register_action_handler("task", handle_task)
        self.core.register_action_handler("plan", handle_plan)
        self.core.register_action_handler("xr_action", handle_xr)
        self.core.register_action_handler("learn", handle_learn)
        
    def plan_next_action(
        self,
        input_text: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Plan the next action based on input and context.
        
        Args:
            input_text: User input
            context: Optional context override (uses symbolic_state if not provided)
            
        Returns:
            Action plan with result
        """
        now = datetime.datetime.now()
        
        # Use global symbolic state if no context provided
        if context is None:
            context = {
                "mode": symbolic_state.get("current_context", {}).get("mode", "idle"),
                "flags": symbolic_state.get("flags", {}),
                "xr_state": symbolic_state.get("xr_state", {}),
                "history_length": len(symbolic_state.get("history", []))
            }
            
        # Update symbolic state with input
        update_state_with_input(input_text)
        
        # Log intent
        intent_log = {
            "time": now.isoformat(),
            "input": input_text,
            "context": context
        }
        self.last_intents.append(intent_log)
        if len(self.last_intents) > 100:
            self.last_intents = self.last_intents[-100:]
            
        # Try to find matching pattern
        result = self.core.process_input(input_text, context)
        
        if result.get("matched"):
            # Successful match - train skill
            action_type = result.get("action", {}).get("type", "")
            skill_mapping = {
                "scroll": "act_scroll",
                "response": "lang_generation",
                "query": "know_retrieval",
                "task": "act_task",
                "plan": "cog_planning",
                "xr_action": "xr_root",
                "learn": "know_integration"
            }
            skill_id = skill_mapping.get(action_type)
            if skill_id:
                self.skills.train_skill(skill_id, 5, success=result.get("success", True))
                
            return {
                "status": "matched",
                "action": result.get("action"),
                "result": result.get("result"),
                "confidence": result.get("confidence"),
                "message": result.get("result") or "[LAM] Action executed."
            }
        else:
            # No match - use fallback logic
            return self._fallback_planning(input_text, context)
            
    def _fallback_planning(self, input_text: str, context: Dict) -> Dict[str, Any]:
        """Fallback planning when no pattern matches."""
        input_lower = input_text.lower()
        
        # Hardcoded fallback rules
        if "study" in input_lower:
            return {
                "status": "fallback",
                "action": {"type": "scroll", "params": {"scroll": "study topic"}},
                "message": "[LAM] Activate study protocol."
            }
        elif "optimize" in input_lower:
            return {
                "status": "fallback",
                "action": {"type": "scroll", "params": {"scroll": "optimize self"}},
                "message": "[LAM] Launch self-optimization scroll."
            }
        elif "reflect" in input_lower:
            return {
                "status": "fallback",
                "action": {"type": "scroll", "params": {"scroll": "reflect"}},
                "message": "[LAM] Trigger introspective memory scan."
            }
        elif any(kw in input_lower for kw in ["xr", "ar", "vr", "training"]):
            if "start" in input_lower and "training" in input_lower:
                return {
                    "status": "fallback",
                    "action": {"type": "xr_action", "params": {"action": "start_training"}},
                    "message": "[LAM] Starting XR training mode."
                }
            elif "start" in input_lower:
                return {
                    "status": "fallback",
                    "action": {"type": "xr_action", "params": {"action": "start_session"}},
                    "message": "[LAM] Starting XR session."
                }
                
        return {
            "status": "no_match",
            "action": None,
            "message": "[LAM] No matching protocol found. Logging intent and awaiting further input."
        }
        
    def provide_feedback(
        self,
        reward: float,
        feedback_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Provide feedback for the last action.
        
        Args:
            reward: Reward value (-1 to 1)
            feedback_text: Optional textual feedback
            
        Returns:
            Feedback processing result
        """
        if not self.last_intents:
            return {"error": "No recent actions to provide feedback for"}
            
        last_intent = self.last_intents[-1]
        
        # Get the action from the last intent if stored
        action = last_intent.get("action", {"type": "unknown"})
        context = last_intent.get("context", {})
        
        # Provide reward through trainer
        result = self.trainer.provide_reward(
            action_taken=action,
            reward=reward,
            context=context,
            feedback=feedback_text
        )
        
        # Record correction if negative feedback with text
        if reward < 0 and feedback_text:
            self.memory.record_correction(
                original_input=last_intent.get("input", ""),
                original_action=action,
                correct_action={"type": "corrected", "feedback": feedback_text},
                feedback=feedback_text
            )
            
        return result
    
    def learn_from_demonstration(
        self,
        input_text: str,
        correct_action: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Learn from a demonstration of correct behavior.
        
        Args:
            input_text: Input that should trigger the action
            correct_action: The correct action to take
            context: Optional context requirements
            
        Returns:
            Learning result
        """
        # Learn in core
        pattern = self.core.learn_pattern(
            input_pattern=input_text,
            action_type=correct_action.get("type", "response"),
            action_params=correct_action.get("params", {}),
            context_requirements=context or {},
            initial_confidence=0.7
        )
        
        # Record as positive experience
        self.memory.record(
            input_text=input_text,
            context=context or {},
            action_taken=correct_action,
            outcome="success",
            reward=0.9,
            importance="high",
            tags=["demonstration", "learned"]
        )
        
        # Train relevant skill
        action_type = correct_action.get("type", "")
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
            self.skills.train_skill(skill_id, 20, success=True, source="demonstration")
            
        return {
            "pattern_id": pattern.pattern_id,
            "learned": True,
            "message": f"[LAM] Learned: '{input_text}' -> {correct_action.get('type')}"
        }
    
    def recall_similar_experiences(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        """Recall similar past experiences."""
        memories = self.memory.recall(query, top_k=top_k)
        return [m.to_dict() for m in memories]
    
    def get_skill_summary(self) -> Dict[str, Any]:
        """Get summary of current skills."""
        return self.skills.get_statistics()
    
    def get_recommended_training(self) -> List[Dict]:
        """Get recommended skills to train."""
        skills = self.skills.get_recommended_training(top_k=5)
        return [s.to_dict() for s in skills]
    
    def run_training_session(
        self,
        mode: str = "curriculum",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a training session.
        
        Args:
            mode: Training mode (curriculum, reinforcement, imitation, replay)
            **kwargs: Additional mode-specific arguments
            
        Returns:
            Training results
        """
        if mode == "curriculum":
            return self.trainer.run_curriculum_training(**kwargs)
        elif mode == "replay":
            return self.trainer.run_experience_replay(**kwargs)
        elif mode == "imitation":
            demonstrations = kwargs.get("demonstrations", [])
            return self.trainer.run_imitation_learning(demonstrations)
        else:
            self.trainer.start_session(mode=mode)
            return {"message": f"Started {mode} training session"}
    
    def get_training_progress(self) -> Dict[str, Any]:
        """Get current training progress."""
        return {
            "curriculum_stage": self.trainer.get_current_curriculum_stage(),
            "skill_progress": self.skills.get_statistics(),
            "training_stats": self.trainer.get_statistics(),
            "memory_stats": self.memory.get_statistics(),
            "patterns_learned": len(self.core.patterns)
        }
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze overall LAM performance."""
        # Get memory analysis
        memory_analysis = self.memory.analyze_for_patterns()
        
        # Get skill gaps
        locked = self.skills.get_locked_skills()
        skill_gaps = [(s.name, missing) for s, missing in locked[:5]]
        
        # Get action statistics
        core_stats = self.core.get_statistics()
        
        return {
            "success_rate": core_stats.get("successful_actions", 0) / max(core_stats.get("total_actions", 1), 1),
            "patterns_learned": core_stats.get("patterns_learned", 0),
            "avg_confidence": core_stats.get("avg_pattern_confidence", 0),
            "failure_patterns": memory_analysis.get("common_failure_contexts", []),
            "successful_patterns": memory_analysis.get("successful_patterns", []),
            "areas_for_improvement": memory_analysis.get("areas_for_improvement", []),
            "skill_gaps": skill_gaps,
            "recommendations": self._generate_recommendations(memory_analysis, skill_gaps)
        }
    
    def _generate_recommendations(
        self,
        memory_analysis: Dict,
        skill_gaps: List
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Based on failures
        failures = memory_analysis.get("areas_for_improvement", [])
        for item in failures[:2]:
            if isinstance(item, dict):
                action = item.get("action", "")
                recommendations.append(f"Practice '{action}' actions more to improve success rate")
                
        # Based on skill gaps
        for skill_name, missing in skill_gaps[:2]:
            recommendations.append(f"Develop prerequisite skills for '{skill_name}'")
            
        # General recommendations
        if len(self.core.patterns) < 20:
            recommendations.append("Learn more input-action patterns through demonstrations")
            
        if self.trainer.curriculum_level < 3:
            recommendations.append("Continue curriculum training to advance to higher levels")
            
        return recommendations
    
    def export_knowledge(self) -> Dict[str, Any]:
        """Export all learned knowledge."""
        return {
            "patterns": self.core.export_patterns(),
            "skills": self.skills.export_tree(),
            "training": self.trainer.export_training_data(),
            "memory_stats": self.memory.get_statistics()
        }
    
    def import_knowledge(self, knowledge: Dict, merge: bool = True) -> Dict[str, Any]:
        """Import knowledge from export."""
        results = {}
        
        if "patterns" in knowledge:
            count = self.core.import_patterns(knowledge["patterns"], merge=merge)
            results["patterns_imported"] = count
            
        return results


# Global instance for backward compatibility
_planner_instance: Optional[LAMPlanner] = None


def get_planner() -> LAMPlanner:
    """Get or create the global LAM planner instance."""
    global _planner_instance
    if _planner_instance is None:
        _planner_instance = LAMPlanner()
    return _planner_instance


def plan_next_action(input_text: str, symbolic_state: Dict = None) -> str:
    """
    Legacy function for backward compatibility.
    
    Args:
        input_text: User input
        symbolic_state: Symbolic state dictionary
        
    Returns:
        Action result message
    """
    planner = get_planner()
    result = planner.plan_next_action(input_text, context=symbolic_state)
    return result.get("message", "[LAM] No matching protocol found.")


__all__ = [
    "LAMPlanner",
    "get_planner",
    "plan_next_action"
]
