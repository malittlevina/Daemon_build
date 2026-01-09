import datetime
from .symbolic_state import global_symbolic_state

class PlanStep:
    def __init__(self, action_type, description, params=None):
        self.action_type = action_type
        self.description = description
        self.params = params or {}
        self.status = "pending"

    def to_dict(self):
        return {
            "action": self.action_type,
            "description": self.description,
            "params": self.params,
            "status": self.status
        }

class LAMPlanner:
    def __init__(self):
        self.known_actions = [
            "study", "optimize", "reflect", "code", "search", "write"
        ]

    def generate_plan(self, goal_text):
        print(f"[LAM] Generating plan for goal: {goal_text}")
        global_symbolic_state.set_goal(goal_text)
        
        plan = []
        goal_lower = goal_text.lower()

        # Rule-based Planning Heuristics
        if "study" in goal_lower or "learn" in goal_lower:
            topic = goal_text.replace("study", "").replace("learn", "").strip()
            plan.append(PlanStep("search", f"Gather information on {topic}", {"query": topic}))
            plan.append(PlanStep("study", f"Deep read and summarize {topic}", {"topic": topic}))
            plan.append(PlanStep("reflect", "Quiz self on material", {"topic": topic}))
            
        elif "optimize" in goal_lower:
            plan.append(PlanStep("analyze", "Run system diagnostics"))
            plan.append(PlanStep("optimize", "Apply auto-fixes"))
            plan.append(PlanStep("verify", "Check system stability"))
            
        elif "create" in goal_lower and "realm" in goal_lower:
             plan.append(PlanStep("write", "Draft realm description"))
             plan.append(PlanStep("code", "Register new realm in engine"))
             
        else:
            # Generic fallback plan
            plan.append(PlanStep("analyze", f"Analyze request: {goal_text}"))
            plan.append(PlanStep("execute", "Attempt best-effort execution"))
            
        return plan

    def execute_plan(self, plan):
        results = []
        for step in plan:
            print(f"[LAM] Executing step: {step.description}")
            step.status = "in_progress"
            # In a real system, this would call specific modules based on 'action_type'
            # For now, we simulate success
            result = f"Executed {step.action_type}: {step.description}"
            step.status = "completed"
            results.append(result)
        return "\n".join(results)

# Global helper
_planner = LAMPlanner()

def plan_next_action(input_text, symbolic_state=None):
    # Backward compatibility wrapper
    plan = _planner.generate_plan(input_text)
    if plan:
        # Return the description of the first step to satisfy the old API expectation of returning a string
        return f"[LAM] Plan generated with {len(plan)} steps. First step: {plan[0].description}"
    return "[LAM] No plan generated."
