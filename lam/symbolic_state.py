# lam/symbolic_state.py

symbolic_state = {
    "history": [],
    "current_context": {},
    "flags": {},
    "xr_state": {
        "active": False,
        "mode": None,
        "device": None,
        "session_id": None,
        "training_active": False,
        "training_scenario": None,
        "spatial_anchors": [],
        "active_overlays": []
    }
}

def update_state_with_input(user_input):
    try:
        # Log input history
        symbolic_state["history"].append(user_input)
        symbolic_state["last_input"] = user_input
        input_lower = user_input.lower()

        # Basic symbolic parsing (placeholder for future logic)
        if "learn" in input_lower:
            symbolic_state["current_context"]["mode"] = "learning"
            symbolic_state["flags"]["is_learning"] = True
        elif "task" in input_lower:
            symbolic_state["current_context"]["mode"] = "task_execution"
            symbolic_state["flags"]["has_active_task"] = True
        # XR-related state updates
        elif any(kw in input_lower for kw in ["ar", "xr", "vr", "augmented", "virtual", "mixed reality"]):
            symbolic_state["current_context"]["mode"] = "xr_interaction"
            symbolic_state["flags"]["xr_context"] = True
        elif "training" in input_lower or "train" in input_lower:
            symbolic_state["current_context"]["mode"] = "training"
            symbolic_state["flags"]["training_context"] = True
        elif "hologram" in input_lower or "overlay" in input_lower:
            symbolic_state["current_context"]["mode"] = "ar_overlay"
            symbolic_state["flags"]["ar_visualization"] = True
        elif "gesture" in input_lower or "hand" in input_lower:
            symbolic_state["current_context"]["mode"] = "gesture_input"
            symbolic_state["flags"]["gesture_mode"] = True
        elif "anchor" in input_lower or "spatial" in input_lower:
            symbolic_state["current_context"]["mode"] = "spatial_mapping"
            symbolic_state["flags"]["spatial_context"] = True
        else:
            symbolic_state["current_context"]["mode"] = "idle"
            symbolic_state["flags"].clear()

        print(f"[SymbolicState] Updated state: {symbolic_state}")

    except Exception as e:
        print(f"[SymbolicState Error] Failed to update state: {e}")


def update_xr_state(xr_data):
    """
    Update XR-specific symbolic state.
    
    Args:
        xr_data: Dictionary containing XR state information
    """
    try:
        if "active" in xr_data:
            symbolic_state["xr_state"]["active"] = xr_data["active"]
        if "mode" in xr_data:
            symbolic_state["xr_state"]["mode"] = xr_data["mode"]
        if "device" in xr_data:
            symbolic_state["xr_state"]["device"] = xr_data["device"]
        if "session_id" in xr_data:
            symbolic_state["xr_state"]["session_id"] = xr_data["session_id"]
        if "training_active" in xr_data:
            symbolic_state["xr_state"]["training_active"] = xr_data["training_active"]
        if "training_scenario" in xr_data:
            symbolic_state["xr_state"]["training_scenario"] = xr_data["training_scenario"]
        if "spatial_anchors" in xr_data:
            symbolic_state["xr_state"]["spatial_anchors"] = xr_data["spatial_anchors"]
        if "active_overlays" in xr_data:
            symbolic_state["xr_state"]["active_overlays"] = xr_data["active_overlays"]
            
        # Update context flags based on XR state
        if symbolic_state["xr_state"]["active"]:
            symbolic_state["flags"]["xr_session_active"] = True
            symbolic_state["current_context"]["xr_mode"] = symbolic_state["xr_state"]["mode"]
        else:
            symbolic_state["flags"].pop("xr_session_active", None)
            symbolic_state["current_context"].pop("xr_mode", None)
            
        if symbolic_state["xr_state"]["training_active"]:
            symbolic_state["flags"]["xr_training_active"] = True
        else:
            symbolic_state["flags"].pop("xr_training_active", None)
            
        print(f"[SymbolicState] Updated XR state: {symbolic_state['xr_state']}")
        
    except Exception as e:
        print(f"[SymbolicState Error] Failed to update XR state: {e}")


def get_xr_state():
    """Get current XR symbolic state."""
    return symbolic_state["xr_state"].copy()


def is_xr_active():
    """Check if XR session is currently active."""
    return symbolic_state["xr_state"]["active"]


def is_training_active():
    """Check if XR training is currently active."""
    return symbolic_state["xr_state"]["training_active"]


def get_current_xr_mode():
    """Get current XR mode if active."""
    if symbolic_state["xr_state"]["active"]:
        return symbolic_state["xr_state"]["mode"]
    return None