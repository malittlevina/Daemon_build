import time
import math
import threading

class PerformanceProfiler:
    def __init__(self):
        self.score = 0
        self.classification = "Unknown"

    def run_benchmark(self):
        """
        Runs a quick CPU/Memory stress test to estimate system tier.
        Returns a score (higher is better).
        """
        print("[Profiler] Running system performance benchmark...")
        start_time = time.time()
        
        # CPU Stress: Matrix multiplication simulation
        size = 500
        matrix_a = [[random_val() for _ in range(size)] for _ in range(size)]
        # We won't actually do full mul to save time, just a heavy loop
        dummy = 0
        for i in range(1000000):
            dummy += math.sqrt(i) * math.sin(i)
            
        duration = time.time() - start_time
        
        # Heuristic scoring (Lower duration = Higher score)
        # Base score 1000 for 1 second.
        self.score = int(1000 / (duration + 0.001))
        
        if self.score > 2000:
            self.classification = "High-End Workstation"
        elif self.score > 1000:
            self.classification = "Gaming PC"
        elif self.score > 500:
            self.classification = "Standard Laptop"
        else:
            self.classification = "Budget/Embedded"
            
        print(f"[Profiler] Score: {self.score} ({self.classification})")
        return self.score

def random_val():
    import random
    return random.random()
