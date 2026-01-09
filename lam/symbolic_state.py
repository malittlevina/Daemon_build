import json
from datetime import datetime

class SymbolicStateManager:
    def __init__(self):
        self.state = {
            "beliefs": {},      # Facts the system believes to be true
            "goals": [],        # Active goals
            "intentions": [],   # Immediate next steps
            "history": [],      # Interaction history
            "context": {        # Current environmental context
                "mode": "idle",
                "active_realm": None,
                "emotional_state": None
            },
            "flags": {}
        }
        
    def update_context(self, key, value):
        self.state["context"][key] = value

    def add_belief(self, subject, predicate, object_):
        # Triplet store: (Subject, Predicate, Object)
        key = f"{subject}:{predicate}"
        self.state["beliefs"][key] = object_
        print(f"[SymbolicState] Belief added: {subject} {predicate} {object_}")

    def set_goal(self, goal_description):
        goal = {
            "id": int(datetime.now().timestamp()),
            "description": goal_description,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        self.state["goals"].append(goal)
        print(f"[SymbolicState] Goal set: {goal_description}")
        return goal["id"]

    def update_from_input(self, user_input, source="user"):
        self.state["history"].append({
            "source": source,
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Heuristic state updates
        lower_input = user_input.lower()
        if "learn" in lower_input:
            self.state["context"]["mode"] = "learning"
        elif "task" in lower_input or "do" in lower_input:
            self.state["context"]["mode"] = "execution"
        elif "stop" in lower_input:
            self.state["context"]["mode"] = "idle"
            
        return self.state

    def get_state_snapshot(self):
        return json.dumps(self.state, indent=2)

# Global Instance
global_symbolic_state = SymbolicStateManager()

def update_state_with_input(user_input, source="user"):
    return global_symbolic_state.update_from_input(user_input, source)
