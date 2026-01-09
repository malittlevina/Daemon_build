# world_engine/physics/materials.py
"""
Materials - Physical material properties.

Provides:
- Material definitions (friction, restitution, density)
- Material interactions (what happens when materials collide)
- Narrative material properties (symbolic meanings)
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto


class MaterialState(Enum):
    """Physical states of matter."""
    SOLID = auto()
    LIQUID = auto()
    GAS = auto()
    PLASMA = auto()
    ETHEREAL = auto()  # Non-physical (narrative only)


@dataclass
class Material:
    """
    Physical material properties.
    
    Defines how objects interact with the world and each other.
    """
    
    name: str = "default"
    
    # Physical properties
    density: float = 1.0              # kg/m³
    friction: float = 0.5             # Static friction coefficient
    dynamic_friction: float = 0.4     # Kinetic friction
    restitution: float = 0.3          # Bounciness (0-1)
    
    # State
    state: MaterialState = MaterialState.SOLID
    
    # Thermal properties
    thermal_conductivity: float = 1.0
    specific_heat: float = 1.0
    melting_point: float = 1000.0
    boiling_point: float = 2000.0
    
    # Structural properties
    hardness: float = 5.0             # 1-10 (Mohs-like scale)
    tensile_strength: float = 100.0   # Breaking force
    elasticity: float = 0.5           # How much it deforms
    
    # Audio properties
    sound_speed: float = 343.0        # m/s (speed of sound in material)
    resonance_frequency: float = 440.0
    
    # Visual properties (for rendering hints)
    color: Tuple[float, float, float] = (0.5, 0.5, 0.5)
    opacity: float = 1.0
    reflectivity: float = 0.1
    roughness: float = 0.5
    
    # Narrative properties
    symbolic_weight: float = 1.0      # Narrative importance
    elemental_affinity: str = ""      # fire, water, earth, air, etc.
    magical_conductivity: float = 0.0 # For fantasy settings
    
    # Tags for special behaviors
    tags: set = field(default_factory=set)
    
    def combine_friction(self, other: 'Material') -> float:
        """Calculate friction between two materials."""
        # Geometric mean
        return (self.friction * other.friction) ** 0.5
    
    def combine_restitution(self, other: 'Material') -> float:
        """Calculate restitution between two materials."""
        # Minimum of the two
        return min(self.restitution, other.restitution)
    
    def get_collision_sound(self, other: 'Material', impact_force: float) -> Dict[str, Any]:
        """Get sound properties for a collision."""
        return {
            "frequency": (self.resonance_frequency + other.resonance_frequency) / 2,
            "volume": min(1.0, impact_force / 100.0),
            "material_a": self.name,
            "material_b": other.name
        }


class MaterialLibrary:
    """
    Library of predefined materials.
    """
    
    _materials: Dict[str, Material] = {}
    
    @classmethod
    def register(cls, material: Material):
        """Register a material."""
        cls._materials[material.name] = material
    
    @classmethod
    def get(cls, name: str) -> Optional[Material]:
        """Get a material by name."""
        return cls._materials.get(name)
    
    @classmethod
    def list_all(cls) -> Dict[str, Material]:
        """List all materials."""
        return dict(cls._materials)
    
    @classmethod
    def initialize_defaults(cls):
        """Initialize default materials."""
        # Basic materials
        cls.register(Material(
            name="stone",
            density=2500,
            friction=0.7,
            restitution=0.1,
            hardness=7,
            color=(0.5, 0.5, 0.5),
            elemental_affinity="earth"
        ))
        
        cls.register(Material(
            name="wood",
            density=600,
            friction=0.5,
            restitution=0.3,
            hardness=4,
            color=(0.6, 0.4, 0.2),
            elemental_affinity="earth"
        ))
        
        cls.register(Material(
            name="metal",
            density=7800,
            friction=0.4,
            restitution=0.5,
            hardness=8,
            color=(0.7, 0.7, 0.8),
            reflectivity=0.8,
            sound_speed=5000,
            resonance_frequency=880
        ))
        
        cls.register(Material(
            name="glass",
            density=2500,
            friction=0.3,
            restitution=0.2,
            hardness=6,
            color=(0.9, 0.95, 1.0),
            opacity=0.2,
            reflectivity=0.5,
            tensile_strength=20
        ))
        
        cls.register(Material(
            name="rubber",
            density=1100,
            friction=0.9,
            restitution=0.8,
            hardness=2,
            elasticity=0.9,
            color=(0.1, 0.1, 0.1)
        ))
        
        cls.register(Material(
            name="ice",
            density=917,
            friction=0.05,
            restitution=0.3,
            hardness=3,
            color=(0.8, 0.9, 1.0),
            opacity=0.7,
            elemental_affinity="water"
        ))
        
        cls.register(Material(
            name="water",
            density=1000,
            friction=0.0,
            restitution=0.0,
            state=MaterialState.LIQUID,
            color=(0.2, 0.4, 0.8),
            opacity=0.5,
            elemental_affinity="water"
        ))
        
        cls.register(Material(
            name="sand",
            density=1600,
            friction=0.6,
            restitution=0.1,
            hardness=3,
            color=(0.9, 0.8, 0.6),
            elemental_affinity="earth"
        ))
        
        cls.register(Material(
            name="flesh",
            density=1050,
            friction=0.4,
            restitution=0.2,
            hardness=1,
            elasticity=0.6,
            color=(0.9, 0.7, 0.6),
            symbolic_weight=2.0
        ))
        
        cls.register(Material(
            name="cloth",
            density=300,
            friction=0.6,
            restitution=0.1,
            hardness=1,
            elasticity=0.7,
            color=(0.8, 0.8, 0.8)
        ))
        
        # Fantasy/Narrative materials
        cls.register(Material(
            name="ethereal",
            density=0,
            friction=0.0,
            restitution=0.0,
            state=MaterialState.ETHEREAL,
            opacity=0.3,
            magical_conductivity=1.0,
            symbolic_weight=3.0
        ))
        
        cls.register(Material(
            name="crystal",
            density=2200,
            friction=0.2,
            restitution=0.4,
            hardness=7,
            color=(0.8, 0.5, 1.0),
            opacity=0.4,
            reflectivity=0.7,
            magical_conductivity=0.8,
            symbolic_weight=2.0
        ))
        
        cls.register(Material(
            name="obsidian",
            density=2400,
            friction=0.3,
            restitution=0.2,
            hardness=5,
            color=(0.1, 0.1, 0.15),
            reflectivity=0.6,
            elemental_affinity="fire",
            symbolic_weight=1.5
        ))
        
        cls.register(Material(
            name="mithril",
            density=3000,
            friction=0.3,
            restitution=0.6,
            hardness=9,
            color=(0.85, 0.9, 1.0),
            reflectivity=0.9,
            tensile_strength=500,
            magical_conductivity=0.5,
            symbolic_weight=3.0
        ))


# Initialize default materials on module load
MaterialLibrary.initialize_defaults()


# Material interaction rules
class MaterialInteractions:
    """
    Defines special interactions between materials.
    """
    
    _interactions: Dict[Tuple[str, str], Dict[str, Any]] = {}
    
    @classmethod
    def register(cls, material_a: str, material_b: str, effects: Dict[str, Any]):
        """Register an interaction between two materials."""
        key = tuple(sorted([material_a, material_b]))
        cls._interactions[key] = effects
    
    @classmethod
    def get(cls, material_a: str, material_b: str) -> Optional[Dict[str, Any]]:
        """Get interaction effects between two materials."""
        key = tuple(sorted([material_a, material_b]))
        return cls._interactions.get(key)
    
    @classmethod
    def initialize_defaults(cls):
        """Initialize default material interactions."""
        # Fire and water
        cls.register("fire", "water", {
            "effect": "steam",
            "fire_extinguished": True,
            "water_evaporated": True,
            "sound": "hiss"
        })
        
        # Fire and wood
        cls.register("fire", "wood", {
            "effect": "burn",
            "propagation_rate": 0.1,
            "damage_per_second": 5.0
        })
        
        # Metal and metal (clang)
        cls.register("metal", "metal", {
            "sound": "clang",
            "spark_chance": 0.3
        })
        
        # Glass and hard surfaces
        cls.register("glass", "stone", {
            "break_threshold": 10.0,
            "sound": "shatter"
        })


MaterialInteractions.initialize_defaults()
