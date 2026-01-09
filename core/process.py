from core.module import Module
import uuid
import time
import threading

class Process:
    def __init__(self, pid, name, target, args=(), kwargs={}, owner="system"):
        self.pid = pid
        self.name = name
        self.owner = owner
        self.status = "pending" # pending, running, completed, failed, stopped
        self.start_time = None
        self.end_time = None
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.thread = None
        self.result = None
        self.error = None

    def run(self):
        self.status = "running"
        self.start_time = time.time()
        try:
            self.result = self.target(*self.args, **self.kwargs)
            self.status = "completed"
        except Exception as e:
            self.error = str(e)
            self.status = "failed"
        finally:
            self.end_time = time.time()

class ProcessManager(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.processes = {}
        self.lock = threading.Lock()

    def initialize(self):
        self.kernel.log("ProcessManager", "Initialized.")

    def start(self):
        pass

    def stop(self):
        # Kill all running processes?
        pass

    def spawn(self, name, target, args=(), kwargs={}, owner=None):
        """Spawn a new process (thread) and return PID."""
        if not owner:
            users = self.kernel.get_module("users")
            if users:
                owner = users.get_current_user().get("username", "system")
            else:
                owner = "system"

        pid = str(uuid.uuid4())[:8]
        process = Process(pid, name, target, args, kwargs, owner)
        
        with self.lock:
            self.processes[pid] = process
        
        # Start in thread
        t = threading.Thread(target=process.run, daemon=True)
        process.thread = t
        t.start()
        
        self.kernel.log("ProcessManager", f"Spawned process {pid} ({name}) for {owner}")
        return pid

    def list_processes(self):
        """Return a list of all process info."""
        info = []
        with self.lock:
            for pid, p in self.processes.items():
                runtime = 0
                if p.status == "running":
                    runtime = time.time() - p.start_time
                elif p.end_time:
                    runtime = p.end_time - p.start_time
                
                info.append({
                    "pid": pid,
                    "name": p.name,
                    "user": p.owner,
                    "status": p.status,
                    "runtime": f"{runtime:.2f}s"
                })
        return info

    def kill(self, pid):
        # Python threads cannot be force-killed easily without C-extensions.
        # We can set a flag if the process supports it, or just remove from table.
        # For this prototype, we just mark it as 'stopped' metadata-wise, 
        # but true termination requires cooperative multitasking (e.g. checking a stop_event).
        
        with self.lock:
            if pid in self.processes:
                self.processes[pid].status = "stopped" # Mock kill
                self.kernel.log("ProcessManager", f"Sent kill signal to {pid}")
                return True
        return False
        
    def get_result(self, pid):
        with self.lock:
            if pid in self.processes:
                p = self.processes[pid]
                if p.status == "completed":
                    return p.result
                elif p.status == "failed":
                    return f"Error: {p.error}"
                else:
                    return f"Status: {p.status}"
        return None
