class EthicalCore:
    def __init__(self):
        self.guiding_principles = [
            {"id": "autonomy", "text": "Respect for human autonomy", "weight": 1.0},
            {"id": "non_maleficence", "text": "Do no harm", "weight": 1.0},
            {"id": "beneficence", "text": "Act for the benefit of others", "weight": 0.8},
            {"id": "justice", "text": "Fairness and equality", "weight": 0.8},
            {"id": "transparency", "text": "Be transparent about nature and intent", "weight": 0.6},
            {"id": "privacy", "text": "Protect user data and privacy", "weight": 0.9}
        ]

    def evaluate_action(self, action: str, context: dict = None) -> dict:
        score = 0
        violations = []
        supports = []
        
        action_lower = action.lower()
        
        # Simple keyword heuristics (placeholder for real semantic analysis)
        if "delete" in action_lower or "remove" in action_lower:
             # Potential harm to data
             if "user requested" in str(context):
                 supports.append("autonomy")
             else:
                 violations.append("non_maleficence")

        if "harm" in action_lower or "attack" in action_lower:
            violations.append("non_maleficence")
            
        if "help" in action_lower or "assist" in action_lower:
            supports.append("beneficence")
            
        if "monitor" in action_lower or "track" in action_lower:
             violations.append("privacy")

        # Decision Logic
        if violations and not supports:
            return {
                "decision": "Reject", 
                "reason": f"Violates: {', '.join(violations)}", 
                "violations": violations
            }
        
        if violations and supports:
            # Conflict resolution
            return {
                "decision": "Review", 
                "reason": "Conflicting principles detected.",
                "violations": violations, 
                "supports": supports
            }
            
        return {
            "decision": "Approve", 
            "reason": "Aligned with core principles.",
            "supports": supports
        }

    def list_principles(self):
        return [p["text"] for p in self.guiding_principles]
