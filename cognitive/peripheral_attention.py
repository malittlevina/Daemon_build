class PeripheralAttention:
    def __init__(self, curiosity_module=None):
        self.curiosity = curiosity_module
        self.current_user_focus = None # From XR Gaze
        self.background_events = []

    def update_user_focus(self, focus_object):
        """
        Updates what the user is currently paying attention to (from XR).
        """
        self.current_user_focus = focus_object

    def process_environmental_event(self, source, description):
        """
        Analyzes a background event to see if it's worth alerting the user.
        """
        # If the user is focusing on X, and the event involves X, it's not "Peripheral" (it's attended).
        # If the event is distinct from X, it might be a "Missed Event".
        
        is_ignored = True
        if self.current_user_focus and self.current_user_focus.lower() in description.lower():
            is_ignored = False
            
        if is_ignored:
            # It's a peripheral event
            print(f"[PeripheralAttention] ⚠️  User ignored: {description} (Focusing on: {self.current_user_focus})")
            
            # Feed to curiosity as a special "Unattended" context
            if self.curiosity:
                self.curiosity.process_observation("PeripheralReality", f"Unattended_{source}", description)
                
            return True # Flag as a peripheral alert
            
        return False
