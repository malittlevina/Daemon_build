import json
import os
from cognitive.predictive_model import PredictiveModel

class Trainer:
    def __init__(self):
        self.model = PredictiveModel()
        self.feedback_log = "training/feedback_history.json"

    def train_on_last_action(self, reward: float):
        """
        Reinforces the last significant action taken by the system.
        Reward: 1.0 (Positive), -1.0 (Negative)
        """
        # In a real RL system, we would have a 'trace' of the last (State, Action) pair.
        # For this prototype, we will simulate reinforcing the 'PredictiveModel' 
        # by artificially boosting or reducing the weight of the last recorded transition.
        
        # We need the model to expose a 'last_observation' or similar.
        # Since the current PredictiveModel is simple, we will add a 'reinforce_last' method to it.
        
        success = self.model.reinforce_last_observation(reward)
        self._log_feedback(reward, success)
        return success

    def _log_feedback(self, reward, success):
        entry = {
            "reward": reward, 
            "success": success,
            "timestamp": os.path.getmtime(self.model.memory_path) if os.path.exists(self.model.memory_path) else 0
        }
        os.makedirs(os.path.dirname(self.feedback_log), exist_ok=True)
        # Simple append to JSON list
        data = []
        if os.path.exists(self.feedback_log):
            with open(self.feedback_log, "r") as f:
                try:
                    data = json.load(f)
                except: pass
        data.append(entry)
        with open(self.feedback_log, "w") as f:
            json.dump(data, f)
