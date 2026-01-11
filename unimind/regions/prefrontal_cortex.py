# unimind/regions/prefrontal_cortex.py
# Prefrontal Cortex - Executive function, planning, decision-making, inhibition

import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque


class ExecutiveFunction(Enum):
    """Executive functions of the prefrontal cortex."""
    PLANNING = "planning"
    DECISION_MAKING = "decision_making"
    WORKING_MEMORY = "working_memory"
    INHIBITION = "inhibition"
    COGNITIVE_FLEXIBILITY = "cognitive_flexibility"
    GOAL_MANAGEMENT = "goal_management"


@dataclass
class Plan:
    """Represents a multi-step plan."""
    plan_id: str
    goal: str
    steps: List[Dict[str, Any]]
    current_step: int = 0
    status: str = "pending"  # pending, executing, completed, failed
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = 0.5
    
    def get_current_step(self) -> Optional[Dict]:
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None
    
    def advance(self) -> bool:
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            return True
        self.status = "completed"
        return False
    
    def to_dict(self) -> Dict:
        return {
            "plan_id": self.plan_id,
            "goal": self.goal,
            "steps": self.steps,
            "current_step": self.current_step,
            "status": self.status,
            "progress": (self.current_step + 1) / len(self.steps) if self.steps else 0
        }


@dataclass
class Decision:
    """Represents a decision to be made."""
    decision_id: str
    question: str
    options: List[Dict[str, Any]]
    criteria: List[str]
    chosen_option: Optional[str] = None
    confidence: float = 0.0
    reasoning: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "decision_id": self.decision_id,
            "question": self.question,
            "options": self.options,
            "chosen": self.chosen_option,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }


class PrefrontalCortex:
    """
    Prefrontal Cortex module - The executive center.
    
    Responsible for:
    - Goal-directed planning
    - Decision making and evaluation
    - Inhibition of inappropriate responses
    - Cognitive flexibility (task switching)
    - Abstract reasoning
    - Self-monitoring
    """
    
    def __init__(self, neural_bus=None, cortex=None):
        self.neural_bus = neural_bus
        self.cortex = cortex
        
        # Active plans
        self.active_plans: Dict[str, Plan] = {}
        self.plan_history: deque = deque(maxlen=50)
        
        # Decision tracking
        self.pending_decisions: Dict[str, Decision] = {}
        self.decision_history: deque = deque(maxlen=100)
        
        # Inhibition
        self.inhibited_responses: List[str] = []
        self.inhibition_rules: Dict[str, str] = {}
        
        # Goal stack (for hierarchical goals)
        self.goal_stack: List[Dict] = []
        
        # AI model hook
        self.reasoning_model = None
        
        # Capabilities
        self.capabilities = [
            "planning", "decision_making", "inhibition",
            "goal_management", "reasoning", "task_switching"
        ]
        
        # Register with neural bus
        if self.neural_bus:
            self._register_with_bus()
            
        print("[PrefrontalCortex] Executive functions initialized.")
        
    def _register_with_bus(self):
        """Register with neural bus."""
        self.neural_bus.register_region(
            region_id="prefrontal_cortex",
            name="Prefrontal Cortex",
            module_type="cortex",
            capabilities=self.capabilities,
            handler=self._handle_signal
        )
        
    def _handle_signal(self, signal) -> Optional[Any]:
        """Handle incoming neural signals."""
        payload = signal.payload
        
        if signal.signal_type.value == "query":
            capability = payload.get("capability")
            if capability == "planning":
                return self._handle_planning_query(payload.get("data", {}))
            elif capability == "decision_making":
                return self._handle_decision_query(payload.get("data", {}))
                
        elif signal.signal_type.value == "excitatory":
            # Process stimulus
            if "goal" in payload:
                self.push_goal(payload["goal"])
            if "plan_request" in payload:
                return self.create_plan(payload["plan_request"])
                
        return None
        
    def _handle_planning_query(self, data: Dict) -> Any:
        """Handle planning queries."""
        from unimind.neural_bus import NeuralSignal, SignalType
        
        if "create" in data:
            plan = self.create_plan(data["create"])
            return NeuralSignal(
                signal_id=f"pfc_plan_{plan.plan_id}",
                signal_type=SignalType.RESPONSE,
                source="prefrontal_cortex",
                target=None,
                payload={"plan": plan.to_dict()}
            )
        elif "status" in data:
            plan_id = data["status"]
            plan = self.active_plans.get(plan_id)
            return NeuralSignal(
                signal_id=f"pfc_status_{plan_id}",
                signal_type=SignalType.RESPONSE,
                source="prefrontal_cortex",
                target=None,
                payload={"plan": plan.to_dict() if plan else None}
            )
        return None
        
    def _handle_decision_query(self, data: Dict) -> Any:
        """Handle decision queries."""
        if "evaluate" in data:
            return self.make_decision(
                question=data["evaluate"].get("question", ""),
                options=data["evaluate"].get("options", []),
                criteria=data["evaluate"].get("criteria", [])
            )
        return None
        
    def set_reasoning_model(self, model: Any):
        """Set the AI model for reasoning tasks."""
        self.reasoning_model = model
        print("[PrefrontalCortex] Reasoning model configured.")
        
    def create_plan(self, goal: str, context: Dict = None) -> Plan:
        """
        Create a plan to achieve a goal.
        
        Args:
            goal: The goal to achieve
            context: Additional context for planning
            
        Returns:
            Created Plan
        """
        plan_id = f"plan_{int(time.time() * 1000)}"
        
        # Generate steps (use AI model if available)
        steps = self._generate_plan_steps(goal, context)
        
        plan = Plan(
            plan_id=plan_id,
            goal=goal,
            steps=steps,
            status="pending",
            confidence=self._estimate_plan_confidence(steps)
        )
        
        self.active_plans[plan_id] = plan
        
        print(f"[PrefrontalCortex] Created plan: {goal} ({len(steps)} steps)")
        return plan
        
    def _generate_plan_steps(self, goal: str, context: Dict = None) -> List[Dict]:
        """Generate plan steps. Uses AI model if available."""
        # Default heuristic planning
        steps = []
        
        # Simple goal decomposition
        goal_lower = goal.lower()
        
        if "learn" in goal_lower or "study" in goal_lower:
            steps = [
                {"action": "gather_resources", "description": "Collect learning materials"},
                {"action": "analyze", "description": "Analyze and understand content"},
                {"action": "practice", "description": "Practice and apply knowledge"},
                {"action": "review", "description": "Review and consolidate"}
            ]
        elif "create" in goal_lower or "build" in goal_lower:
            steps = [
                {"action": "design", "description": "Design the solution"},
                {"action": "implement", "description": "Implement the design"},
                {"action": "test", "description": "Test the implementation"},
                {"action": "refine", "description": "Refine and improve"}
            ]
        elif "solve" in goal_lower or "fix" in goal_lower:
            steps = [
                {"action": "analyze", "description": "Analyze the problem"},
                {"action": "hypothesize", "description": "Generate hypotheses"},
                {"action": "test", "description": "Test solutions"},
                {"action": "verify", "description": "Verify the fix"}
            ]
        else:
            # Generic planning
            steps = [
                {"action": "understand", "description": "Understand the goal"},
                {"action": "plan", "description": "Break down into subtasks"},
                {"action": "execute", "description": "Execute subtasks"},
                {"action": "evaluate", "description": "Evaluate results"}
            ]
            
        # Add step numbers
        for i, step in enumerate(steps):
            step["step_number"] = i + 1
            step["status"] = "pending"
            
        return steps
        
    def _estimate_plan_confidence(self, steps: List[Dict]) -> float:
        """Estimate confidence in plan success."""
        if not steps:
            return 0.0
            
        # Base confidence
        confidence = 0.5
        
        # More detailed steps = higher confidence
        avg_desc_length = sum(len(s.get("description", "")) for s in steps) / len(steps)
        if avg_desc_length > 30:
            confidence += 0.1
            
        # Reasonable number of steps
        if 3 <= len(steps) <= 7:
            confidence += 0.1
            
        return min(1.0, confidence)
        
    def execute_plan_step(self, plan_id: str) -> Optional[Dict]:
        """Execute the current step of a plan."""
        plan = self.active_plans.get(plan_id)
        if not plan:
            return None
            
        current = plan.get_current_step()
        if not current:
            return None
            
        plan.status = "executing"
        current["status"] = "executing"
        
        # In a real system, this would dispatch to appropriate handlers
        result = {
            "plan_id": plan_id,
            "step": current,
            "status": "executing"
        }
        
        # Broadcast execution
        if self.neural_bus:
            self.neural_bus.emit_broadcast(
                source="prefrontal_cortex",
                payload={"plan_step": result},
                priority="normal"
            )
            
        return result
        
    def complete_plan_step(self, plan_id: str, success: bool = True) -> Optional[Dict]:
        """Mark current step as complete and advance."""
        plan = self.active_plans.get(plan_id)
        if not plan:
            return None
            
        current = plan.get_current_step()
        if current:
            current["status"] = "completed" if success else "failed"
            
        if success:
            if not plan.advance():
                # Plan completed
                self.plan_history.append(plan)
                del self.active_plans[plan_id]
                return {"plan_id": plan_id, "status": "completed"}
        else:
            plan.status = "failed"
            self.plan_history.append(plan)
            del self.active_plans[plan_id]
            return {"plan_id": plan_id, "status": "failed"}
            
        return {"plan_id": plan_id, "current_step": plan.current_step, "status": "in_progress"}
        
    def make_decision(
        self,
        question: str,
        options: List[Dict[str, Any]],
        criteria: List[str] = None
    ) -> Decision:
        """
        Make a decision by evaluating options against criteria.
        
        Args:
            question: The decision question
            options: List of options with properties
            criteria: Criteria to evaluate against
            
        Returns:
            Decision with chosen option
        """
        decision_id = f"dec_{int(time.time() * 1000)}"
        criteria = criteria or ["feasibility", "value", "risk"]
        
        decision = Decision(
            decision_id=decision_id,
            question=question,
            options=options,
            criteria=criteria
        )
        
        # Evaluate options
        scores = {}
        for option in options:
            option_id = option.get("id", str(options.index(option)))
            score = self._evaluate_option(option, criteria)
            scores[option_id] = score
            
        # Choose best option
        if scores:
            best = max(scores.keys(), key=lambda k: scores[k])
            decision.chosen_option = best
            decision.confidence = scores[best] / 3.0  # Normalize
            decision.reasoning = f"Selected based on highest score across criteria: {criteria}"
            
        self.decision_history.append(decision)
        
        print(f"[PrefrontalCortex] Decision: {question} -> {decision.chosen_option}")
        return decision
        
    def _evaluate_option(self, option: Dict, criteria: List[str]) -> float:
        """Evaluate an option against criteria."""
        score = 0.0
        
        for criterion in criteria:
            # Check if option has criterion value
            if criterion in option:
                score += float(option[criterion])
            else:
                # Default scoring based on criterion type
                if criterion == "feasibility":
                    score += 0.5  # Assume moderate feasibility
                elif criterion == "value":
                    score += 0.5
                elif criterion == "risk":
                    score += 0.3  # Lower is better for risk
                else:
                    score += 0.5
                    
        return score
        
    def add_inhibition_rule(self, trigger: str, reason: str):
        """Add an inhibition rule to prevent certain responses."""
        self.inhibition_rules[trigger.lower()] = reason
        print(f"[PrefrontalCortex] Added inhibition rule: {trigger}")
        
    def check_inhibition(self, response: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a response should be inhibited.
        
        Returns:
            Tuple of (should_inhibit, reason)
        """
        response_lower = response.lower()
        
        for trigger, reason in self.inhibition_rules.items():
            if trigger in response_lower:
                self.inhibited_responses.append({
                    "response": response,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                })
                return True, reason
                
        return False, None
        
    def push_goal(self, goal: Dict):
        """Push a goal onto the goal stack."""
        goal["pushed_at"] = datetime.now().isoformat()
        self.goal_stack.append(goal)
        
    def pop_goal(self) -> Optional[Dict]:
        """Pop the top goal from the stack."""
        if self.goal_stack:
            return self.goal_stack.pop()
        return None
        
    def get_current_goal(self) -> Optional[Dict]:
        """Get the current (top) goal."""
        if self.goal_stack:
            return self.goal_stack[-1]
        return None
        
    def task_switch(self, new_context: Dict) -> Dict:
        """
        Handle task switching (cognitive flexibility).
        
        Args:
            new_context: New task context
            
        Returns:
            Switch result
        """
        # Save current context
        old_goal = self.get_current_goal()
        
        # Clear working state for new task
        result = {
            "old_goal": old_goal,
            "new_context": new_context,
            "switch_time": datetime.now().isoformat()
        }
        
        if "goal" in new_context:
            self.push_goal(new_context["goal"])
            
        # Broadcast task switch
        if self.neural_bus:
            self.neural_bus.emit_broadcast(
                source="prefrontal_cortex",
                payload={"task_switch": result},
                priority="high"
            )
            
        print(f"[PrefrontalCortex] Task switched to: {new_context.get('goal', new_context)}")
        return result
        
    def get_status(self) -> Dict[str, Any]:
        """Get PFC status."""
        return {
            "active_plans": len(self.active_plans),
            "plan_history": len(self.plan_history),
            "pending_decisions": len(self.pending_decisions),
            "decision_history": len(self.decision_history),
            "goal_stack_depth": len(self.goal_stack),
            "current_goal": self.get_current_goal(),
            "inhibition_rules": len(self.inhibition_rules),
            "inhibited_count": len(self.inhibited_responses)
        }
