import datetime

last_intents = []

def plan_next_action(input_text, symbolic_state):
    now = datetime.datetime.now()
    intent_log = {
        "time": now.isoformat(),
        "input": input_text,
        "symbolic_state": symbolic_state
    }

    last_intents.append(intent_log)
    input_lower = input_text.lower()

    # Robotics intents
    if any(word in input_lower for word in ["robot", "companion", "bot"]):
        return _plan_robot_action(input_lower, symbolic_state)
    
    # Example hardcoded logic
    if "study" in input_lower:
        return "[LAM] Activate study protocol."
    elif "optimize" in input_lower:
        return "[LAM] Launch self-optimization scroll."
    elif "reflect" in input_lower:
        return "[LAM] Trigger introspective memory scan."

    return "[LAM] No matching protocol found. Logging intent and awaiting further input."


def _plan_robot_action(input_text, symbolic_state):
    """
    Plan robot-specific actions based on input and state.
    
    Args:
        input_text: Lowercased input text
        symbolic_state: Current symbolic state
        
    Returns:
        Action plan string
    """
    robotics_state = symbolic_state.get("robotics", {})
    is_connected = robotics_state.get("connected", False)
    current_mode = robotics_state.get("mode", "idle")
    
    # Check robot availability
    if "start" in input_text or "activate" in input_text or "wake" in input_text:
        return "[LAM] Invoke scroll: robot start"
    
    if not is_connected:
        return "[LAM] Robot not connected. Invoke scroll: robot start"
    
    # Movement commands
    if "follow" in input_text:
        return "[LAM] Invoke scroll: robot follow"
    elif "stop" in input_text or "halt" in input_text:
        return "[LAM] Invoke scroll: robot halt"
    elif "perch" in input_text or "attach" in input_text:
        location = "shoulder"  # Default
        if "arm" in input_text:
            location = "arm"
        elif "pocket" in input_text:
            location = "pocket"
        return f"[LAM] Invoke scroll: robot perch (location: {location})"
    elif "go to" in input_text or "navigate" in input_text:
        # Extract destination - get everything after "to" or "navigate"
        destination = None
        if " to " in input_text:
            parts = input_text.split(" to ", 1)
            if len(parts) > 1:
                # Get destination, removing common words
                dest_words = parts[1].strip().split()
                dest_words = [w for w in dest_words if w not in ["the", "a", "an", "my"]]
                destination = " ".join(dest_words) if dest_words else None
        elif "navigate " in input_text:
            parts = input_text.split("navigate ", 1)
            if len(parts) > 1:
                dest_words = parts[1].strip().split()
                dest_words = [w for w in dest_words if w not in ["to", "the", "a", "an", "my"]]
                destination = " ".join(dest_words) if dest_words else None
        
        if destination:
            return f"[LAM] Invoke scroll: robot navigate (target: {destination})"
        return "[LAM] Invoke scroll: robot navigate"
    elif "home" in input_text:
        return "[LAM] Invoke scroll: robot go home"
    elif "charge" in input_text:
        return "[LAM] Invoke scroll: robot charge"
    
    # Gesture/expression commands
    if "wave" in input_text:
        return "[LAM] Invoke scroll: robot gesture (name: wave)"
    elif "nod" in input_text:
        return "[LAM] Invoke scroll: robot gesture (name: nod)"
    elif any(emotion in input_text for emotion in ["happy", "sad", "curious", "excited"]):
        emotion = next(e for e in ["happy", "sad", "curious", "excited"] if e in input_text)
        return f"[LAM] Invoke scroll: robot express (emotion: {emotion})"
    
    # Status check
    if "status" in input_text or "how are you" in input_text:
        return "[LAM] Invoke scroll: robot status"
    
    # Calibration
    if "calibrate" in input_text:
        return "[LAM] Invoke scroll: robot calibrate"
    
    return "[LAM] Robot command not recognized. Available: follow, stop, perch, navigate, home, wave, status"


def get_robot_action_from_plan(plan_string):
    """
    Extract robot action from LAM plan string.
    
    Args:
        plan_string: Plan string from plan_next_action
        
    Returns:
        Tuple of (scroll_name, params_dict) or None
    """
    if "Invoke scroll:" not in plan_string:
        return None
    
    # Extract scroll name
    parts = plan_string.split("Invoke scroll:")
    if len(parts) < 2:
        return None
    
    scroll_part = parts[1].strip()
    
    # Check for parameters
    if "(" in scroll_part:
        scroll_name = scroll_part[:scroll_part.index("(")].strip()
        param_str = scroll_part[scroll_part.index("(")+1:scroll_part.index(")")]
        
        params = {}
        for param in param_str.split(","):
            if ":" in param:
                key, value = param.split(":", 1)
                params[key.strip()] = value.strip()
        
        return (scroll_name, params)
    else:
        return (scroll_part, {})


__all__ = ["plan_next_action", "get_robot_action_from_plan"]
