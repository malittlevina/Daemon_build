from .spatial_mapper import SpatialMapper
from .avatar import PersistentAvatar

class ARManager:
    def __init__(self, emotion_engine=None):
        self.active_apps = {}
        self.current_app = None
        self.spatial_mapper = SpatialMapper()
        self.overlay_enabled = False
        self.emotion_engine = emotion_engine
        self.avatar = None
        
        if self.emotion_engine:
            self.avatar = PersistentAvatar(self, self.emotion_engine)

    def start_avatar(self):
        if self.avatar:
            self.avatar.start()

    def stop_avatar(self):
        if self.avatar:
            self.avatar.stop()

    def register_app(self, app_name, app_config):
        self.active_apps[app_name] = app_config
        print(f"[ARManager] App '{app_name}' registered.")

    def launch_app(self, app_name):
        if app_name in self.active_apps:
            self.current_app = app_name
            self.overlay_enabled = True
            print(f"[ARManager] Launching AR app: {app_name}")
            return True
        else:
            print(f"[ARManager] App '{app_name}' not found.")
            return False

    def stop_app(self):
        if self.current_app:
            print(f"[ARManager] Stopping {self.current_app}")
            self.current_app = None
            self.overlay_enabled = False
        else:
            print("[ARManager] No active app to stop.")

    def update_overlay(self, vision_data):
        if self.overlay_enabled and self.current_app:
            # Logic to generate overlay based on app and vision data
            # Utilizing spatial mapper for anchor resolution
            pass
