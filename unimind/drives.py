import time
import json
import os
from typing import Dict, List

class Drive:
    def __init__(self, name: str, decay_rate: float = 0.1, recovery_action: str = None):
        self.name = name
        self.value = 1.0  # 0.0 to 1.0 (1.0 is fully satisfied)
        self.decay_rate = decay_rate # per hour approx
        self.recovery_action = recovery_action

    def update(self, time_delta_hours: float):
        self.value = max(0.0, self.value - (self.decay_rate * time_delta_hours))

    def satisfy(self, amount: float):
        self.value = min(1.0, self.value + amount)

    def is_critical(self, threshold: float = 0.3):
        return self.value < threshold

class DriveSystem:
    def __init__(self, storage_path="config/drives.json"):
        self.storage_path = storage_path
        self.drives: Dict[str, Drive] = {
            "Curiosity": Drive("Curiosity", decay_rate=0.2, recovery_action="explore world"),
            "Competence": Drive("Competence", decay_rate=0.05, recovery_action="optimize self"),
            "Coherence": Drive("Coherence", decay_rate=0.01, recovery_action="reflect")
        }
        self.last_update_time = time.time()
        self.load()

    def update(self):
        current_time = time.time()
        delta_hours = (current_time - self.last_update_time) / 3600.0
        self.last_update_time = current_time
        
        for drive in self.drives.values():
            drive.update(delta_hours)
        
        self.save()

    def get_most_urgent_drive(self) -> Drive:
        # Return the drive with the lowest value
        return min(self.drives.values(), key=lambda d: d.value)

    def satisfy_drive(self, drive_name: str, amount: float):
        if drive_name in self.drives:
            self.drives[drive_name].satisfy(amount)
            self.save()

    def save(self):
        data = {
            "last_update_time": self.last_update_time,
            "drives": {k: {"value": d.value} for k, d in self.drives.items()}
        }
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                self.last_update_time = data.get("last_update_time", time.time())
                for k, v in data.get("drives", {}).items():
                    if k in self.drives:
                        self.drives[k].value = v.get("value", 1.0)
