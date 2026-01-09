from core.module import Module
import threading

class VoiceService(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.thread = None
        self.enabled = False

    def initialize(self):
        # Check config
        config = self.kernel.config.get("voice_listener_enabled", False)
        self.enabled = config
        if self.enabled:
            self.kernel.log("VoiceService", "Initialized (Enabled).")
        else:
            self.kernel.log("VoiceService", "Initialized (Disabled in config).")

    def start(self):
        if self.enabled:
            try:
                from voice.voice_listener import start_voice_listener
                self.thread = threading.Thread(target=start_voice_listener, daemon=True)
                self.thread.start()
                self.kernel.log("VoiceService", "Listener started.")
            except ImportError:
                self.kernel.log("VoiceService", "Voice module not found/installed.", level="warning")
            except Exception as e:
                self.kernel.log("VoiceService", f"Failed to start: {e}", level="error")

    def stop(self):
        pass
