from cognitive.predictive_model import PredictiveModel
from codex.ingestion import ingest_observation

class CuriosityModule:
    def __init__(self):
        self.model = PredictiveModel()
        self.surprise_threshold = 0.8  # If surprise > 0.8, pay attention

    def process_observation(self, context, event, outcome):
        surprise = self.model.calculate_surprise(context, event, outcome)
        
        # Always learn (update the model)
        self.model.observe(context, event, outcome)
        
        if surprise > self.surprise_threshold:
            self._trigger_learning_event(context, event, outcome, surprise)
            return True # Interesting
        return False # Boring

    def _trigger_learning_event(self, context, event, outcome, surprise):
        # 1. Log to Codex (Episodic Memory)
        observation_text = (
            f"Curiosity Triggered! Surprise Level: {surprise:.2f}\n"
            f"Context: {context}\n"
            f"Event: {event}\n"
            f"Outcome: {outcome}\n"
            f"Insight: This outcome was unexpected based on previous experiences."
        )
        print(f"[Curiosity] {observation_text}")
        ingest_observation(observation_text)
        
        # 2. In a full AGI, this would trigger an 'Experiment' to verify the new rule
        # e.g., "Try to reproduce 'event' in 'context' again."
