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
            """
        }

    def render(self, avatar_state):
        # Determine which ascii to show
        # Priority: Expression -> Sub-state (animation)
        
        expression = avatar_state["expression"]
        sub_state = avatar_state["sub_state"]
        
        # If animation sub-state overrides expression (like blinking), use it
        key = expression
        if sub_state in self.art_assets:
            key = sub_state
        elif expression in self.art_assets:
            key = expression
        else:
            key = "neutral"
            
        return self.art_assets.get(key, self.art_assets["neutral"])
