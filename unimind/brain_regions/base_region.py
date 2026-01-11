class BrainRegion:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.active_models = {}

    def load_model(self, model_key, model_instance):
        self.active_models[model_key] = model_instance
        print(f"[{self.name}] Loaded model: {model_key}")

    def process(self, input_data, **kwargs):
        raise NotImplementedError("Each brain region must implement a process method.")
