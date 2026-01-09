from core.module import Module
import threading
from optimizer.auto_upgrade import run_auto_optimization

class OptimizerService(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.thread = None

    def initialize(self):
        self.kernel.log("Optimizer", "Initialized.")

    def start(self):
        # We can use the ProcessManager if we want it tracked, or raw thread
        # Using thread for now to keep it simple, but managed
        self.thread = threading.Thread(target=run_auto_optimization, daemon=True)
        self.thread.start()
        self.kernel.log("Optimizer", "Self-optimization loop started.")

    def stop(self):
        # The legacy run_auto_optimization might not have a stop flag, 
        # so we rely on daemon thread killing
        pass
