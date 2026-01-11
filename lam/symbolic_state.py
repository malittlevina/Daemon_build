# lam/symbolic_state.py

symbolic_state = {
    "history": [],
    "current_context": {},
    "flags": {}
}

def update_state_with_input(user_input, source=None):
    try:
        # Log input history
        symbolic_state["history"].append(user_input)
        symbolic_state["last_input"] = user_input
        if source is not None:
            symbolic_state["last_input_source"] = source

        # Robotics command routing (safe-by-default; simulation driver until hardware exists).
        try:
            from robotics.robotics_manager import get_robotics_manager
            mgr = get_robotics_manager()
            robot_result = mgr.handle_text_command(user_input, source=source or "symbolic_state")
            if robot_result is not None:
                symbolic_state["current_context"]["mode"] = "robotics"
                symbolic_state["flags"]["robotics_last_result"] = robot_result
                print(f"[SymbolicState] Robotics: {robot_result}")
                return robot_result
        except Exception as e:
            # Robotics should never break the rest of the daemon.
            print(f"[SymbolicState Robotics Error] {e}")

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