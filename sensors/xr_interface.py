from interop.spatial_server import EVENT_XR_UPDATE
import time

class XRInterface:
    def __init__(self, spatial_server, curiosity_module=None, avatar_engine=None, sensor_manager=None):
        self.spatial_server = spatial_server
        self.curiosity = curiosity_module
        self.avatar = avatar_engine
        self.sensor_manager = sensor_manager
        
        # Subscribe to XR events
        self.spatial_server.on(EVENT_XR_UPDATE, self._on_xr_data)
        
        self.last_gaze_object = None
        self.last_update_time = 0

    def _on_xr_data(self, payload):
        """
        Payload Schema:
        {
            "gaze_vector": [x, y, z],
            "looked_at_object": "cat",
            "confidence": 0.95
        }
        """
        current_time = time.time()
        looked_at = payload.get("looked_at_object")
        gaze_vector = payload.get("gaze_vector", [0, 0, 1])

        # 0. Sync Focus with Sensor Manager (Peripheral Awareness)
        if self.sensor_manager and looked_at:
            self.sensor_manager.update_user_focus(looked_at)

        # 1. Update Avatar Gaze (Embodiment)
        if self.avatar:
            # Map 3D vector to simple 2D direction for ASCII avatar
            # Assuming x is left/right (-1 to 1), y is up/down (-1 to 1)
            x = gaze_vector[0]
            direction = "center"
            if x < -0.3: direction = "left"
            elif x > 0.3: direction = "right"
            
            self.avatar.set_gaze(direction)

        # 2. Trigger Curiosity (Cognition)
        if looked_at and looked_at != self.last_gaze_object:
            self.last_gaze_object = looked_at
            
            if self.curiosity:
                context = "XR_Reality"
                event = "UserGaze"
                outcome = f"User looked at {looked_at}"
                
                is_interesting = self.curiosity.process_observation(context, event, outcome)
                if is_interesting:
                    print(f"[XRInterface] 💡 User is focusing on: {looked_at}")
