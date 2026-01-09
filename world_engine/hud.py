from world_engine.ecs import System
from world_engine.components import Transform, UIWindow, Name

class HUDSystem(System):
    def update(self, delta_time: float):
        # Find the user avatar (mocked for now, usually entity with tag 'player')
        # We assume the camera is at (0,0,0) or tracked by XRServer
        # For this prototype, we'll just orbit UI windows around 0,0,0
        
        windows = self.world.entity_manager.get_entities_with(UIWindow, Transform)
        
        # Simple layout logic: Arrange in a semi-circle
        import math
        radius = 2.0
        count = len(windows)
        
        for i, entity in enumerate(windows):
            angle = (i - count/2) * 0.5 # Spread by 0.5 radians
            
            # Position relative to user (0,0,0)
            target_x = math.sin(angle) * radius
            target_z = math.cos(angle) * radius
            target_y = 1.5 # Eye height
            
            # Smoothly interpolate to target
            t = entity.get_component(Transform)
            t.position[0] += (target_x - t.position[0]) * 5 * delta_time
            t.position[1] += (target_y - t.position[1]) * 5 * delta_time
            t.position[2] += (target_z - t.position[2]) * 5 * delta_time
            
            # Look at user
            t.rotation = [0, angle + 3.14159, 0] # Face inwards
