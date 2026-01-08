import json
import os
import numpy as np
from cognitive.predictive_model import PredictiveModel
from cognitive.brain.neural_net import NeuralNet

class Trainer:
    def __init__(self):
        self.model = PredictiveModel()
        self.feedback_log = "training/feedback_history.json"
        
        # Initialize the "Real" Brain (Neural Net)
        # Input: Context Vector (Placeholder size 10)
        # Output: Predicted Outcome Vector (Placeholder size 5)
        self.brain = NeuralNet(input_size=10, hidden_size=16, output_size=5)
        self.brain_path = "training/brain_weights.json"
        self.brain.load(self.brain_path)

    def train_on_last_action(self, reward: float):
        """
        Reinforces the last significant action taken by the system.
        Reward: 1.0 (Positive), -1.0 (Negative)
        """
        success = self.model.reinforce_last_observation(reward)
        
        # Train Neural Net (Simulated Context)
        # In a real impl, we'd fetch the vector representation of the last state
        mock_input = np.random.rand(1, 10) 
        mock_target = np.random.rand(1, 5) # We would target the 'good' outcome
        
        if reward > 0:
            loss = self.brain.train(mock_input, mock_target)
            self.brain.save(self.brain_path)
            # print(f"[Trainer] Neural Net trained. Loss: {loss:.4f}")

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
