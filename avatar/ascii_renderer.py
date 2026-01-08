class ASCIIRenderer:
    def __init__(self):
        self.art_assets = {
            "neutral": """
             .---.
            ( o o )
             | - |
             '---'
            """,
            "happy": """
             .---.
            ( ^ ^ )
             | v |
             '---'
            """,
            "surprised": """
             .---.
            ( O O )
             | o |
             '---'
            """,
            "tired": """
             .---.
            ( - - )
             | ~ |
             '---'
            """,
            "nervous": """
             .---.
            ( > < )
             | ~ |
             '---'
            """,
             "blink": """
             .---.
            ( - - )
             | - |
             '---'
            """,
            "look_left": """
             .---.
            ( < < )
             | o |
             '---'
            """,
            "look_right": """
             .---.
            ( > > )
             | o |
             '---'
            """
        }

    def render(self, avatar_state):
        # Determine which ascii to show
        # Priority: Gaze -> Expression -> Sub-state
        
        expression = avatar_state["expression"]
        sub_state = avatar_state["sub_state"]
        gaze = avatar_state.get("gaze", "center")
        
        key = "neutral"
        
        # Gaze overrides neutral expression but not strong emotions?
        # For simplicity, let's say direct gaze override if not center
        if gaze == "left":
            key = "look_left"
        elif gaze == "right":
            key = "look_right"
        else:
            # Fallback to expression
            if sub_state in self.art_assets:
                key = sub_state
            elif expression in self.art_assets:
                key = expression
            
        return self.art_assets.get(key, self.art_assets["neutral"])
