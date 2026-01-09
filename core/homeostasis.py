from core.module import Module
import time

class Homeostasis(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.error_count = 0
        self.last_check = time.time()
        self.health_score = 100

    def initialize(self):
        self.kernel.log("Homeostasis", "Autonomic Nervous System Initialized.")
        # Listen to all logs to catch errors
        # Note: In a real system, we'd hook into the Logger directly or use a specific event.
        # For now, we assume modules dispatch 'system:error' or we poll status.

    def handle_error(self, module_name, exception):
        """Centralized Error Handler"""
        self.kernel.log(module_name, f"CRITICAL ERROR: {exception}", level="error")
        
        # Dispatch Panic Event
        self.kernel.dispatch("system:panic", {"module": module_name, "error": str(exception)})
        
        # Automatic Recovery Logic
        homeostasis = self.kernel.get_module("homeostasis")
        if homeostasis:
            homeostasis.error_count += 1
            homeostasis.health_score -= 10
            self.kernel.log("ErrorHandler", "Notified Homeostasis of failure.")
            # In future: homeostasis.attempt_restart(module_name)
        
    def start(self):
        # Register a background check
        scheduler = self.kernel.get_module("scheduler")
        if scheduler:
            scheduler.schedule_interval(60, "system_health_check", self.perform_check)

    def stop(self):
        pass

    def perform_check(self):
        """Analyze system state and heal if necessary."""
        self.kernel.log("Homeostasis", f"Performing health check. Current Score: {self.health_score}")
        
        # 1. Check Process Health
        pm = self.kernel.get_module("process_manager")
        if pm:
            processes = pm.list_processes()
            failed = [p for p in processes if p["status"] == "failed"]
            if failed:
                self.kernel.log("Homeostasis", f"Detected {len(failed)} failed processes. Cleaning up...")
                # Action: Clear failed logs? Restart?
                self.error_count += len(failed)
                self.health_score -= 5

        # 2. Check Database Size (Entropy)
        kg = self.kernel.get_module("knowledge_graph")
        # Stub logic

        # 3. Corrective Action
        if self.health_score < 80:
            self._trigger_healing()

        # Regenerate score slowly
        if self.health_score < 100:
            self.health_score += 1

    def _trigger_healing(self):
        self.kernel.log("Homeostasis", "Health Critical. Initiating Healing Trance.")
        
        # Example: Trigger Garbage Collection in Python
        import gc
        gc.collect()
        
        # Example: Clear caches
        net = self.kernel.get_module("network")
        if net:
            net.dns_cache.clear()
            
        self.kernel.log("Homeostasis", "Healing complete. Systems normalized.")
