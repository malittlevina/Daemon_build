import random
from typing import Dict, List, Any
from world_engine.state import WorldState, Location, Entity

class EnvironmentEngine:
    def __init__(self):
        self.weather_types = ["Clear", "Rain", "Storm", "Fog", "Snow"]
        self.weather_transitions = {
            "Clear": ["Clear", "Clear", "Rain", "Fog"],
            "Rain": ["Rain", "Clear", "Storm"],
            "Storm": ["Rain", "Storm"],
            "Fog": ["Fog", "Clear", "Rain"],
            "Snow": ["Snow", "Clear", "Storm"]
        }
        self.day_length_ticks = 24.0 # 1 tick = 1 hour abstractly
        
    def update(self, state: WorldState) -> List[str]:
        logs = []
        current_time_of_day = state.time % self.day_length_ticks
        
        # 1. Update Global Time of Day Effects
        is_day = 6 <= current_time_of_day <= 18
        global_light = 1.0 if is_day else 0.2
        
        # 2. Update Locations
        for loc in state.locations.values():
            # Update Light
            loc.properties["light_level"] = global_light
            
            # Update Weather (random chance to change)
            current_weather = loc.properties.get("weather", "Clear")
            if random.random() < 0.1: # 10% chance to change weather
                possible_next = self.weather_transitions.get(current_weather, ["Clear"])
                new_weather = random.choice(possible_next)
                if new_weather != current_weather:
                    loc.properties["weather"] = new_weather
                    logs.append(f"Weather in {loc.name} changed to {new_weather}")
            
            # Apply Weather Effects
            if loc.properties["weather"] == "Storm":
                loc.properties["light_level"] *= 0.5 # Darker
                if random.random() < 0.05:
                    logs.append(f"Lightning strikes in {loc.name}!")
            
        return logs
