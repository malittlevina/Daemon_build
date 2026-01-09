import random
import time
from sensors.vision import VisionSensor

class RealityOverlay:
    def __init__(self, world_engine):
        self.world_engine = world_engine
        try:
            self.vision = VisionSensor()
        except Exception as e:
            print(f"[RealityOverlay] Vision sensor unavailable: {e}")
            self.vision = None

    def scan_reality_for_encounter(self):
        """
        Uses camera/sensors to generate an encounter based on real-world conditions.
        """
        if not self.vision:
            return self._simulated_encounter("blind")

        # 1. Visual Context
        scene_type = self.vision.classify_scene() # Indoor / Outdoor
        print(f"[RealityOverlay] Visual Scan: {scene_type}")
        
        # 2. Determine Biome & Enemies
        if scene_type == "Outdoor":
            biome = "Wilderness"
            possible_enemies = ["Stray Dog", "Drone", "Solar Wisp"]
        else:
            biome = "Dungeon (Indoor)"
            possible_enemies = ["Dust Mite Giant", "Wi-Fi Poltergeist", "Roomba Beast"]

        # 3. Generate Entity
        enemy_name = random.choice(possible_enemies)
        entity = {
            "name": enemy_name,
            "type": "Enemy",
            "properties": {
                "origin": "Augmented Reality",
                "biome": biome,
                "hp": random.randint(20, 50)
            }
        }
        
        return {
            "biome": biome,
            "entity": entity,
            "description": f"The veil thins. A {enemy_name} manifests in the {biome} sector."
        }

    def _simulated_encounter(self, reason):
        # Fallback if sensors fail
        return {
            "biome": "Unknown Void",
            "entity": {"name": "Glitch Shadow", "type": "Enemy", "properties": {"hp": 10}},
            "description": f"Sensors offline ({reason}). A Glitch Shadow appears from the static."
        }

    def sync_weather_effects(self, city="London"): # Default city
        """
        Applies real-world weather modifiers to the current realm.
        """
        # Simulated weather call (avoiding API key requirement for this demo)
        # In prod: from thirdparty.weather import get_weather
        weather_conditions = ["Rain", "Clear", "Mist", "Thunderstorm"]
        current_weather = random.choice(weather_conditions) 
        
        effects = []
        if current_weather == "Rain":
            effects.append("Wet (+10% Lightning Dmg, -10% Fire Dmg)")
        elif current_weather == "Clear":
            effects.append("Sunny (+10% Fire Dmg)")
            
        return {
            "weather": current_weather,
            "effects": effects,
            "description": f"Real-world atmospheric resonance: {current_weather}."
        }
