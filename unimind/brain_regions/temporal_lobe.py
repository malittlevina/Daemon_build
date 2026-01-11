from .base_region import BrainRegion

class TemporalLobe(BrainRegion):
    """
    Responsible for Auditory Processing.
    """
    def __init__(self):
        super().__init__("TemporalLobe", "Auditory Processing")

    def process(self, input_data, task="listen", **kwargs):
        if task == "listen":
            print(f"[{self.name}] Processing audio input...")
            return "Transcribed text"
        elif task == "speak":
            print(f"[{self.name}] Generating audio output...")
            return "Audio stream"
        return None
