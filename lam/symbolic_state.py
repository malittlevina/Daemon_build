# lam/symbolic_state.py

symbolic_state = {
    "history": [],
    "current_context": {},
    "flags": {},
    "robotics": {
        "enabled": False,
        "mode": "idle",
        "connected": False,
        "battery_state": "unknown",
        "navigation_target": None
    }
}

def update_state_with_input(user_input):
    try:
        # Log input history
        symbolic_state["history"].append(user_input)
        symbolic_state["last_input"] = user_input

        # Basic symbolic parsing (placeholder for future logic)
        if "learn" in user_input.lower():
            symbolic_state["current_context"]["mode"] = "learning"
            symbolic_state["flags"]["is_learning"] = True
        elif "task" in user_input.lower():
            symbolic_state["current_context"]["mode"] = "task_execution"
            symbolic_state["flags"]["has_active_task"] = True
        else:
            symbolic_state["current_context"]["mode"] = "idle"
            symbolic_state["flags"].clear()

        print(f"[SymbolicState] Updated state: {symbolic_state}")

    except Exception as e:
        print(f"[SymbolicState Error] Failed to update state: {e}")


def update_robotics_state(robot_state: dict) -> None:
    """
    Update symbolic state with robot information.
    
    Args:
        robot_state: Dictionary with robot state from RobotState.get_symbolic_state()
    """
    try:
        symbolic_state["robotics"]["enabled"] = True
        symbolic_state["robotics"]["connected"] = True
        
        if "current_context" in robot_state:
            ctx = robot_state["current_context"]
            symbolic_state["robotics"]["mode"] = ctx.get("mode", "idle")
            symbolic_state["robotics"]["battery_state"] = ctx.get("battery", "unknown")
            symbolic_state["robotics"]["navigation_target"] = ctx.get("navigation_target")
        
        if "flags" in robot_state:
            for key, value in robot_state["flags"].items():
                symbolic_state["flags"][f"robot_{key}"] = value
        
        print(f"[SymbolicState] Updated robotics state: {symbolic_state['robotics']}")
        
    except Exception as e:
        print(f"[SymbolicState Error] Failed to update robotics state: {e}")


def get_robotics_context() -> dict:
    """
    Get robotics context for decision making.
    
    Returns:
        Dictionary with robot-relevant symbolic state
    """
    return {
        "robotics": symbolic_state.get("robotics", {}),
        "robot_flags": {
            k: v for k, v in symbolic_state.get("flags", {}).items()
            if k.startswith("robot_")
        }
    }