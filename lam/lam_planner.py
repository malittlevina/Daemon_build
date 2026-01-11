# lam/lam_planner.py
"""
Large Action Model (LAM) Planner - Intelligent action planning and execution

The LAM bridges high-level intentions to concrete executable actions by:
- Decomposing goals into actionable steps
- Selecting appropriate tools and methods
- Sequencing actions with dependency awareness
- Monitoring execution and adapting plans
"""

from typing import Dict, Any, Optional, List, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading


class ActionType(Enum):
    """Types of actions the LAM can plan."""
    SCROLL = "scroll"           # Invoke a scroll/routine
    API_CALL = "api_call"       # External API invocation
    TOOL_USE = "tool_use"       # Use an internal tool
    MEMORY_OP = "memory_op"     # Memory read/write
    REASONING = "reasoning"     # Trigger reasoning chain
    USER_PROMPT = "user_prompt" # Request user input
    SYSTEM = "system"           # System-level operation
    COMPOSITE = "composite"     # Group of actions


class ActionStatus(Enum):
    """Status of a planned action."""
    PENDING = "pending"
    READY = "ready"
    BLOCKED = "blocked"  # Waiting on dependencies
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PlannedAction:
    """Represents a single action in an execution plan."""
    action_id: str
    action_type: ActionType
    name: str
    description: str
    handler: Optional[str] = None  # Module/function to handle this action
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # Action IDs this depends on
    status: ActionStatus = ActionStatus.PENDING
    priority: int = 1
    estimated_duration_ms: int = 1000
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.action_id,
            "type": self.action_type.value,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "priority": self.priority
        }


@dataclass
class ExecutionPlan:
    """A complete plan for achieving a goal."""
    plan_id: str
    goal: str
    actions: List[PlannedAction] = field(default_factory=list)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def get_ready_actions(self) -> List[PlannedAction]:
        """Get actions that are ready to execute."""
        ready = []
        completed_ids = {a.action_id for a in self.actions if a.status == ActionStatus.COMPLETED}
        
        for action in self.actions:
            if action.status == ActionStatus.PENDING:
                # Check if all dependencies are met
                if all(dep in completed_ids for dep in action.dependencies):
                    ready.append(action)
        
        return ready
    
    def is_complete(self) -> bool:
        """Check if plan is complete."""
        return all(
            a.status in (ActionStatus.COMPLETED, ActionStatus.SKIPPED)
            for a in self.actions
        )
    
    def has_failed(self) -> bool:
        """Check if plan has failed."""
        return any(a.status == ActionStatus.FAILED for a in self.actions)


class LAMPlanner:
    """
    Large Action Model Planner - Plans and coordinates action execution.
    
    The planner works by:
    1. Analyzing the goal to identify required actions
    2. Building a dependency graph of actions
    3. Scheduling actions for execution
    4. Monitoring progress and adapting as needed
    """
    
    module_name = "lam_planner"
    dependencies = ["unimind"]
    
    def __init__(self):
        self._kernel = None
        self._lock = threading.RLock()
        
        # Active and completed plans
        self._active_plans: Dict[str, ExecutionPlan] = {}
        self._completed_plans: List[ExecutionPlan] = []
        
        # Action handlers registry
        self._handlers: Dict[ActionType, Dict[str, Callable]] = {
            action_type: {} for action_type in ActionType
        }
        
        # Intent tracking for context
        self._last_intents: List[Dict] = []
        self._max_intents = 50
        
        # Planning templates for common goals
        self._templates: Dict[str, List[Dict]] = self._init_templates()
        
        print("[LAMPlanner] Initialized.")
    
    def _init_templates(self) -> Dict[str, List[Dict]]:
        """Initialize planning templates for common goals."""
        return {
            "study": [
                {"type": ActionType.REASONING, "name": "analyze_topic", "desc": "Understand the topic structure"},
                {"type": ActionType.MEMORY_OP, "name": "recall_related", "desc": "Recall related knowledge"},
                {"type": ActionType.API_CALL, "name": "fetch_resources", "desc": "Gather learning resources"},
                {"type": ActionType.SCROLL, "name": "execute_study", "desc": "Execute study protocol"},
                {"type": ActionType.MEMORY_OP, "name": "store_knowledge", "desc": "Store new knowledge"}
            ],
            "optimize": [
                {"type": ActionType.REASONING, "name": "analyze_system", "desc": "Analyze current system state"},
                {"type": ActionType.TOOL_USE, "name": "run_diagnostics", "desc": "Run diagnostic checks"},
                {"type": ActionType.REASONING, "name": "identify_improvements", "desc": "Identify optimization opportunities"},
                {"type": ActionType.SCROLL, "name": "apply_optimizations", "desc": "Apply selected optimizations"},
                {"type": ActionType.MEMORY_OP, "name": "log_changes", "desc": "Log optimization changes"}
            ],
            "task": [
                {"type": ActionType.REASONING, "name": "understand_task", "desc": "Parse and understand the task"},
                {"type": ActionType.REASONING, "name": "plan_execution", "desc": "Create execution plan"},
                {"type": ActionType.TOOL_USE, "name": "execute_steps", "desc": "Execute task steps"},
                {"type": ActionType.MEMORY_OP, "name": "record_result", "desc": "Record task result"}
            ],
            "reflect": [
                {"type": ActionType.MEMORY_OP, "name": "gather_history", "desc": "Gather recent interaction history"},
                {"type": ActionType.REASONING, "name": "analyze_patterns", "desc": "Analyze behavior patterns"},
                {"type": ActionType.REASONING, "name": "generate_insights", "desc": "Generate self-insights"},
                {"type": ActionType.MEMORY_OP, "name": "store_reflection", "desc": "Store reflection results"}
            ]
        }
    
    def initialize(self, kernel) -> bool:
        """Initialize with kernel reference."""
        self._kernel = kernel
        
        if kernel:
            kernel.subscribe("lam.plan_goal", self._handle_plan_request)
            kernel.subscribe("lam.execute", self._handle_execute_request)
        
        print("[LAMPlanner] Connected to kernel.")
        return True
    
    def start(self) -> bool:
        """Start the planner."""
        return True
    
    def stop(self) -> bool:
        """Stop the planner."""
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "status": "healthy",
            "active_plans": len(self._active_plans),
            "completed_plans": len(self._completed_plans),
            "registered_handlers": sum(len(h) for h in self._handlers.values())
        }
    
    def register_handler(
        self,
        action_type: ActionType,
        name: str,
        handler: Callable
    ):
        """Register a handler for an action type."""
        self._handlers[action_type][name] = handler
        print(f"[LAMPlanner] Registered handler: {action_type.value}/{name}")
    
    def plan_next_action(
        self,
        input_text: str,
        symbolic_state: Dict[str, Any] = None
    ) -> str:
        """
        Analyze input and determine next action.
        
        This is a quick planning method for immediate responses.
        """
        now = datetime.now()
        intent_log = {
            "time": now.isoformat(),
            "input": input_text,
            "symbolic_state": symbolic_state
        }
        
        self._last_intents.append(intent_log)
        if len(self._last_intents) > self._max_intents:
            self._last_intents = self._last_intents[-self._max_intents:]
        
        input_lower = input_text.lower()
        
        # Intent detection with protocol mapping
        if "study" in input_lower or "learn" in input_lower:
            return "[LAM] Activate study protocol."
        elif "optimize" in input_lower or "improve" in input_lower:
            return "[LAM] Launch self-optimization scroll."
        elif "reflect" in input_lower or "think about" in input_lower:
            return "[LAM] Trigger introspective memory scan."
        elif "task" in input_lower or "run" in input_lower:
            return "[LAM] Execute task protocol."
        elif "plan" in input_lower:
            return "[LAM] Activate planning mode."
        elif "help" in input_lower or "what can" in input_lower:
            return "[LAM] Provide assistance guidance."
        
        return "[LAM] No matching protocol found. Logging intent and awaiting further input."
    
    def create_plan(
        self,
        goal: str,
        context: Dict[str, Any] = None
    ) -> ExecutionPlan:
        """
        Create an execution plan for a goal.
        
        Args:
            goal: The high-level goal to achieve
            context: Additional context for planning
            
        Returns:
            ExecutionPlan with sequenced actions
        """
        import uuid
        plan_id = str(uuid.uuid4())[:8]
        
        plan = ExecutionPlan(
            plan_id=plan_id,
            goal=goal,
            context=context or {}
        )
        
        # Determine which template to use
        goal_lower = goal.lower()
        template_key = None
        
        for key in self._templates.keys():
            if key in goal_lower:
                template_key = key
                break
        
        if template_key:
            # Build plan from template
            template = self._templates[template_key]
            prev_action_id = None
            
            for i, action_def in enumerate(template):
                action_id = f"{plan_id}_{i}"
                
                action = PlannedAction(
                    action_id=action_id,
                    action_type=action_def["type"],
                    name=action_def["name"],
                    description=action_def["desc"],
                    handler=action_def["name"],
                    dependencies=[prev_action_id] if prev_action_id else [],
                    priority=len(template) - i  # Higher priority for earlier actions
                )
                
                plan.actions.append(action)
                prev_action_id = action_id
        else:
            # Create a generic plan
            plan.actions = [
                PlannedAction(
                    action_id=f"{plan_id}_0",
                    action_type=ActionType.REASONING,
                    name="understand_goal",
                    description=f"Understand and analyze: {goal}",
                    priority=3
                ),
                PlannedAction(
                    action_id=f"{plan_id}_1",
                    action_type=ActionType.TOOL_USE,
                    name="execute_goal",
                    description=f"Execute: {goal}",
                    dependencies=[f"{plan_id}_0"],
                    priority=2
                ),
                PlannedAction(
                    action_id=f"{plan_id}_2",
                    action_type=ActionType.MEMORY_OP,
                    name="record_outcome",
                    description="Record the outcome",
                    dependencies=[f"{plan_id}_1"],
                    priority=1
                )
            ]
        
        with self._lock:
            self._active_plans[plan_id] = plan
        
        print(f"[LAMPlanner] Created plan '{plan_id}' with {len(plan.actions)} actions for goal: {goal}")
        
        # Notify kernel
        if self._kernel:
            self._kernel.publish(
                "lam.plan.created",
                {"plan_id": plan_id, "goal": goal, "action_count": len(plan.actions)},
                "lam_planner"
            )
        
        return plan
    
    def execute_plan(
        self,
        plan_id: str,
        async_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a plan.
        
        Args:
            plan_id: ID of plan to execute
            async_mode: If True, schedule for async execution
            
        Returns:
            Execution status
        """
        with self._lock:
            plan = self._active_plans.get(plan_id)
            if not plan:
                return {"error": f"Plan not found: {plan_id}"}
        
        plan.status = "running"
        plan.started_at = datetime.utcnow()
        
        if async_mode and self._kernel:
            # Schedule execution
            self._kernel.schedule_task(
                lambda: self._execute_plan_sync(plan),
                name=f"plan.{plan_id}",
                source_module="lam_planner"
            )
            return {"status": "scheduled", "plan_id": plan_id}
        else:
            return self._execute_plan_sync(plan)
    
    def _execute_plan_sync(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Execute a plan synchronously."""
        results = []
        
        while not plan.is_complete() and not plan.has_failed():
            ready_actions = plan.get_ready_actions()
            
            if not ready_actions:
                # No actions ready but plan not complete - might be blocked
                break
            
            for action in ready_actions:
                result = self._execute_action(action, plan.context)
                results.append(result)
                
                if action.status == ActionStatus.FAILED:
                    plan.status = "failed"
                    break
        
        if plan.is_complete():
            plan.status = "completed"
            plan.completed_at = datetime.utcnow()
            
            with self._lock:
                if plan.plan_id in self._active_plans:
                    del self._active_plans[plan.plan_id]
                    self._completed_plans.append(plan)
        
        return {
            "plan_id": plan.plan_id,
            "status": plan.status,
            "actions_completed": len([a for a in plan.actions if a.status == ActionStatus.COMPLETED]),
            "total_actions": len(plan.actions),
            "results": results
        }
    
    def _execute_action(
        self,
        action: PlannedAction,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single action."""
        action.status = ActionStatus.RUNNING
        action.started_at = datetime.utcnow()
        
        try:
            # Find handler
            handler = self._handlers.get(action.action_type, {}).get(action.handler)
            
            if handler:
                result = handler(action.parameters, context)
            else:
                # Default handling based on action type
                result = self._default_handler(action, context)
            
            action.status = ActionStatus.COMPLETED
            action.completed_at = datetime.utcnow()
            action.result = result
            
            print(f"[LAMPlanner] Action completed: {action.name}")
            
            return {
                "action_id": action.action_id,
                "name": action.name,
                "status": "completed",
                "result": result
            }
            
        except Exception as e:
            action.status = ActionStatus.FAILED
            action.completed_at = datetime.utcnow()
            action.error = str(e)
            
            print(f"[LAMPlanner] Action failed: {action.name} - {e}")
            
            return {
                "action_id": action.action_id,
                "name": action.name,
                "status": "failed",
                "error": str(e)
            }
    
    def _default_handler(
        self,
        action: PlannedAction,
        context: Dict[str, Any]
    ) -> Any:
        """Default handler for actions without registered handlers."""
        if action.action_type == ActionType.REASONING:
            # Use unimind for reasoning
            if self._kernel:
                unimind = self._kernel.get_module("unimind")
                if unimind:
                    return unimind.think(action.description)
            return {"reasoning": action.description, "status": "simulated"}
        
        elif action.action_type == ActionType.MEMORY_OP:
            # Log to memory
            if self._kernel:
                self._kernel.set_state(
                    f"memory.{action.name}",
                    {"description": action.description, "timestamp": datetime.utcnow().isoformat()}
                )
            return {"memory_op": action.name, "status": "logged"}
        
        elif action.action_type == ActionType.SCROLL:
            # Invoke scroll engine
            if self._kernel:
                scroll_engine = self._kernel.get_module("scroll_engine")
                if scroll_engine:
                    return scroll_engine.invoke(action.name, **action.parameters)
            return {"scroll": action.name, "status": "simulated"}
        
        else:
            return {"action": action.name, "status": "simulated"}
    
    def get_plan(self, plan_id: str) -> Optional[Dict]:
        """Get plan details."""
        with self._lock:
            plan = self._active_plans.get(plan_id)
            if not plan:
                # Check completed plans
                for p in self._completed_plans:
                    if p.plan_id == plan_id:
                        plan = p
                        break
            
            if plan:
                return {
                    "plan_id": plan.plan_id,
                    "goal": plan.goal,
                    "status": plan.status,
                    "actions": [a.to_dict() for a in plan.actions],
                    "created_at": plan.created_at.isoformat()
                }
            return None
    
    def list_active_plans(self) -> List[Dict]:
        """List all active plans."""
        with self._lock:
            return [
                {"plan_id": p.plan_id, "goal": p.goal, "status": p.status}
                for p in self._active_plans.values()
            ]
    
    def cancel_plan(self, plan_id: str) -> bool:
        """Cancel an active plan."""
        with self._lock:
            if plan_id in self._active_plans:
                plan = self._active_plans[plan_id]
                plan.status = "cancelled"
                
                for action in plan.actions:
                    if action.status in (ActionStatus.PENDING, ActionStatus.READY):
                        action.status = ActionStatus.SKIPPED
                
                self._completed_plans.append(plan)
                del self._active_plans[plan_id]
                
                print(f"[LAMPlanner] Plan cancelled: {plan_id}")
                return True
            return False
    
    def _handle_plan_request(self, message):
        """Handle plan creation request from kernel."""
        goal = message.payload.get("goal")
        context = message.payload.get("context", {})
        
        plan = self.create_plan(goal, context)
        
        if message.correlation_id and self._kernel:
            self._kernel.message_bus.respond(
                message.correlation_id,
                {"plan_id": plan.plan_id}
            )
    
    def _handle_execute_request(self, message):
        """Handle plan execution request from kernel."""
        plan_id = message.payload.get("plan_id")
        self.execute_plan(plan_id)
    
    def reflect(self) -> Dict[str, Any]:
        """Provide reflection data."""
        with self._lock:
            return {
                "active_plans": len(self._active_plans),
                "completed_plans": len(self._completed_plans),
                "recent_intents": self._last_intents[-5:],
                "templates_available": list(self._templates.keys())
            }


# Legacy compatibility
last_intents = []

def plan_next_action(input_text: str, symbolic_state: Dict[str, Any] = None) -> str:
    """Legacy function for backward compatibility."""
    planner = LAMPlanner()
    return planner.plan_next_action(input_text, symbolic_state)
