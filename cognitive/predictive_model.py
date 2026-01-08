import json
import os
from collections import defaultdict
import math

class PredictiveModel:
    def __init__(self, memory_path="cognitive/predictive_memory.json"):
        self.memory_path = memory_path
        # Structure: transitions[context_key][event_type] = {outcome_key: count}
        self.transitions = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.load()

    def _get_context_key(self, world_state):
        # Simplify world state into a hashable key for pattern matching
        # For now, we use weather and time of day as context
        weather = "Unknown"
        time_phase = "Day"
        
        # Extract from summary if available
        if isinstance(world_state, dict):
            # This is a simplification; in a real AGI this would be a rich vector
            # We'll try to extract global weather if possible, or just ignore
            pass
            
        return f"{time_phase}"

    def observe(self, context, event, outcome):
        """
        Learns from a single experience triplet.
        Context: The state before the event.
        Event: The action or trigger.
        Outcome: The result or state change.
        """
        # outcome_key: string representation of what changed
        self.transitions[str(context)][str(event)][str(outcome)] += 1
        self.last_triplet = (str(context), str(event), str(outcome)) # Store for reinforcement
        self.save()

    def reinforce_last_observation(self, weight_delta):
        """
        Adjusts the weight of the last observed transition.
        """
        if not hasattr(self, 'last_triplet'):
            return False
            
        context, event, outcome = self.last_triplet
        
        # Apply weight
        current = self.transitions[context][event][outcome]
        # Ensure we don't drop below 0
        new_val = max(0, current + weight_delta)
        self.transitions[context][event][outcome] = new_val
        self.save()
        return True

    def predict(self, context, event):
        """
        Returns a dictionary of {outcome: probability}
        """
        outcomes = self.transitions[str(context)][str(event)]
        total = sum(outcomes.values())
        if total == 0:
            return {}
        
        return {k: v / total for k, v in outcomes.items()}

    def calculate_surprise(self, context, event, actual_outcome):
        """
        Returns a surprise value (0.0 to 1.0).
        High surprise means the actual outcome was unlikely according to the model.
        """
        predictions = self.predict(context, event)
        probability = predictions.get(str(actual_outcome), 0.0)
        
        # Information Theory: Self-Information / Surprisal
        # Surprise = -log2(p). If p=1, surprise=0. If p=0, surprise is infinite (we cap it).
        # For this usage, let's just use (1 - p) for linear simplicity in this demo
        return 1.0 - probability

    def save(self):
        # Convert to standard dict for JSON
        data = {
            k: {
                ek: dict(ev) 
                for ek, ev in v.items()
            }
            for k, v in self.transitions.items()
        }
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        with open(self.memory_path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r") as f:
                data = json.load(f)
                for context, events in data.items():
                    for event, outcomes in events.items():
                        for outcome, count in outcomes.items():
                            self.transitions[context][event][outcome] = count
