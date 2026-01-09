from core.module import Module
import time
import threading
from datetime import datetime, date

class Scheduler(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.tasks = []
        self._stop_event = threading.Event()
        self._thread = None

    def initialize(self):
        self.kernel.log("Scheduler", "Initialized.")

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self.kernel.log("Scheduler", "Started task loop.")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        self.kernel.log("Scheduler", "Stopped.")

    def schedule_daily(self, hour, minute, task_name, callback):
        """Schedule a task to run daily at a specific time."""
        self.tasks.append({
            "type": "daily",
            "hour": hour,
            "minute": minute,
            "name": task_name,
            "callback": callback,
            "last_run": None
        })
        self.kernel.log("Scheduler", f"Scheduled daily task '{task_name}' at {hour:02d}:{minute:02d}")

    def schedule_interval(self, seconds, task_name, callback):
        """Schedule a task to run every X seconds."""
        self.tasks.append({
            "type": "interval",
            "seconds": seconds,
            "name": task_name,
            "callback": callback,
            "last_run": time.time()
        })
        self.kernel.log("Scheduler", f"Scheduled interval task '{task_name}' every {seconds}s")

    def _run_loop(self):
        while not self._stop_event.is_set():
            now = datetime.now()
            today_str = str(date.today())
            
            for task in self.tasks:
                if task["type"] == "daily":
                    # Check if it's time and haven't run today
                    if now.hour == task["hour"] and now.minute == task["minute"]:
                        if task["last_run"] != today_str:
                            self._execute_task(task)
                            task["last_run"] = today_str
                            
                elif task["type"] == "interval":
                    if time.time() - task["last_run"] >= task["seconds"]:
                        self._execute_task(task)
                        task["last_run"] = time.time()

            time.sleep(1)

    def _execute_task(self, task):
        self.kernel.log("Scheduler", f"Executing task: {task['name']}")
        try:
            task["callback"]()
        except Exception as e:
            self.kernel.log("Scheduler", f"Task '{task['name']}' failed: {e}", level="error")
