from core.module import Module

class ViewManager(Module):
    """
    A Headless Window Manager. 
    It tracks 'Windows' and 'Layouts' even if it can't render pixels.
    """
    def __init__(self, kernel):
        super().__init__(kernel)
        self.windows = {} # pid -> {title, x, y, w, h, content}
        self.active_window = None
        self.resolution = (80, 24) # Virtual terminal size

    def initialize(self):
        self.kernel.log("ViewManager", "Initialized (Headless GUI).")

    def start(self):
        pass

    def stop(self):
        pass

    def create_window(self, pid, title, content=""):
        self.windows[pid] = {
            "title": title,
            "x": 0, "y": 0, "w": 40, "h": 10,
            "content": content,
            "minimized": False
        }
        self.active_window = pid
        self.kernel.log("ViewManager", f"Created window for PID {pid}: {title}")

    def update_window(self, pid, content):
        if pid in self.windows:
            self.windows[pid]["content"] = content

    def close_window(self, pid):
        if pid in self.windows:
            del self.windows[pid]
            if self.active_window == pid:
                self.active_window = list(self.windows.keys())[-1] if self.windows else None

    def render(self):
        """
        Returns a JSON representation of the screen state.
        A real display server (web or terminal) would draw this.
        """
        return {
            "resolution": self.resolution,
            "active_window": self.active_window,
            "windows": self.windows
        }
