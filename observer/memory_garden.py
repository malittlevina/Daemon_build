# observer/memory_garden.py
"""
Memory Garden
=============
An organic metaphor for memory growth and nurturing.

Memories are planted as seeds, nurtured through recall and reflection,
and grow into flowers that bear fruit (insights, connections).

The garden has different plots for different types of memories,
seasons that affect growth, and a natural ecosystem where
memories can cross-pollinate and create new understanding.
"""

import os
import json
import time
import random
import threading
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

from .moment import Moment, MomentType, Significance


class GrowthStage(Enum):
    """Stages of memory growth in the garden."""
    SEED = 0           # Just planted, fragile
    SPROUT = 1         # Starting to take root
    GROWING = 2        # Developing, being strengthened
    FLOWERING = 3      # Fully formed, producing connections
    FRUITING = 4       # Mature, generating insights
    PERENNIAL = 5      # Permanently established, always accessible


class Season(Enum):
    """Seasons affect how memories grow."""
    SPRING = "spring"  # New growth, planting time
    SUMMER = "summer"  # Active growth, high energy
    AUTUMN = "autumn"  # Harvest insights, consolidation
    WINTER = "winter"  # Dormancy, deep reflection


class PlotType(Enum):
    """Different areas of the garden for different memory types."""
    CONVERSATION_GROVE = "conversation_grove"
    INSIGHT_MEADOW = "insight_meadow"
    EVENT_ORCHARD = "event_orchard"
    REFLECTION_POND = "reflection_pond"
    DISCOVERY_CLEARING = "discovery_clearing"
    MILESTONE_MONUMENT = "milestone_monument"
    FEELING_FLOWERS = "feeling_flowers"
    PATTERN_MAZE = "pattern_maze"
    GENERAL_GARDEN = "general_garden"


@dataclass
class MemorySeed:
    """A memory that has been planted but not yet grown."""
    moment_id: str
    planted_at: float = field(default_factory=time.time)
    plot: PlotType = PlotType.GENERAL_GARDEN
    water_count: int = 0       # Times it's been nurtured
    sunlight: float = 0.5      # Attention received (0-1)
    nutrients: float = 0.5     # Connections to other memories
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['plot'] = self.plot.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MemorySeed':
        data['plot'] = PlotType(data['plot'])
        return cls(**data)


@dataclass
class MemoryFlower:
    """A fully grown memory that can produce insights."""
    moment_id: str
    stage: GrowthStage = GrowthStage.FLOWERING
    plot: PlotType = PlotType.GENERAL_GARDEN
    bloom_date: float = field(default_factory=time.time)
    pollen: List[str] = field(default_factory=list)  # Tags/concepts it shares
    connections: List[str] = field(default_factory=list)  # Related flower IDs
    fruits: List[str] = field(default_factory=list)  # Insights generated
    beauty: float = 0.5        # How meaningful/aesthetic
    fragrance: float = 0.5     # How memorable/distinctive
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['stage'] = self.stage.value
        data['plot'] = self.plot.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MemoryFlower':
        data['stage'] = GrowthStage(data['stage'])
        data['plot'] = PlotType(data['plot'])
        return cls(**data)


class MemoryGarden:
    """
    The Memory Garden - where moments are planted, nurtured, and grown.
    
    Memories need care:
    - Water (recall/revisit) to grow
    - Sunlight (attention) to flourish
    - Nutrients (connections) to bear fruit
    - Pruning (forgetting) to stay healthy
    """
    
    def __init__(self, garden_path: str = "observer/garden"):
        self.garden_path = garden_path
        self.seeds_file = os.path.join(garden_path, "seeds.json")
        self.flowers_file = os.path.join(garden_path, "flowers.json")
        self.garden_state_file = os.path.join(garden_path, "garden_state.json")
        
        os.makedirs(garden_path, exist_ok=True)
        
        # Garden state
        self.seeds: Dict[str, MemorySeed] = {}
        self.flowers: Dict[str, MemoryFlower] = {}
        self.season: Season = self._determine_season()
        self.garden_age_days: int = 0
        self.total_planted: int = 0
        self.total_bloomed: int = 0
        self.total_pruned: int = 0
        
        # Moment storage (reference to moments)
        self.moments: Dict[str, Moment] = {}
        
        # Background growth thread
        self._growth_active = False
        self._growth_thread: Optional[threading.Thread] = None
        
        self._load_garden()
        print(f"[MemoryGarden] Garden awakened. Season: {self.season.value}")
        print(f"[MemoryGarden] {len(self.seeds)} seeds, {len(self.flowers)} flowers")
    
    def _determine_season(self) -> Season:
        """Determine current season based on time."""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return Season.SPRING
        elif month in [6, 7, 8]:
            return Season.SUMMER
        elif month in [9, 10, 11]:
            return Season.AUTUMN
        else:
            return Season.WINTER
    
    def _get_plot_for_moment(self, moment: Moment) -> PlotType:
        """Determine which garden plot suits a moment."""
        type_to_plot = {
            MomentType.CONVERSATION: PlotType.CONVERSATION_GROVE,
            MomentType.QUESTION: PlotType.CONVERSATION_GROVE,
            MomentType.ANSWER: PlotType.CONVERSATION_GROVE,
            MomentType.INSIGHT: PlotType.INSIGHT_MEADOW,
            MomentType.REALIZATION: PlotType.INSIGHT_MEADOW,
            MomentType.EVENT: PlotType.EVENT_ORCHARD,
            MomentType.MILESTONE: PlotType.MILESTONE_MONUMENT,
            MomentType.DISCOVERY: PlotType.DISCOVERY_CLEARING,
            MomentType.REFLECTION: PlotType.REFLECTION_POND,
            MomentType.FEELING: PlotType.FEELING_FLOWERS,
            MomentType.PATTERN: PlotType.PATTERN_MAZE,
        }
        return type_to_plot.get(moment.moment_type, PlotType.GENERAL_GARDEN)
    
    def _load_garden(self):
        """Load garden state from disk."""
        # Load seeds
        if os.path.exists(self.seeds_file):
            try:
                with open(self.seeds_file, 'r') as f:
                    data = json.load(f)
                    self.seeds = {k: MemorySeed.from_dict(v) for k, v in data.items()}
            except Exception as e:
                print(f"[MemoryGarden] Error loading seeds: {e}")
        
        # Load flowers
        if os.path.exists(self.flowers_file):
            try:
                with open(self.flowers_file, 'r') as f:
                    data = json.load(f)
                    self.flowers = {k: MemoryFlower.from_dict(v) for k, v in data.items()}
            except Exception as e:
                print(f"[MemoryGarden] Error loading flowers: {e}")
        
        # Load garden state
        if os.path.exists(self.garden_state_file):
            try:
                with open(self.garden_state_file, 'r') as f:
                    state = json.load(f)
                    self.garden_age_days = state.get('garden_age_days', 0)
                    self.total_planted = state.get('total_planted', 0)
                    self.total_bloomed = state.get('total_bloomed', 0)
                    self.total_pruned = state.get('total_pruned', 0)
            except Exception as e:
                print(f"[MemoryGarden] Error loading state: {e}")
    
    def _save_garden(self):
        """Save garden state to disk."""
        try:
            # Save seeds
            with open(self.seeds_file, 'w') as f:
                data = {k: v.to_dict() for k, v in self.seeds.items()}
                json.dump(data, f, indent=2)
            
            # Save flowers
            with open(self.flowers_file, 'w') as f:
                data = {k: v.to_dict() for k, v in self.flowers.items()}
                json.dump(data, f, indent=2)
            
            # Save state
            with open(self.garden_state_file, 'w') as f:
                state = {
                    'garden_age_days': self.garden_age_days,
                    'total_planted': self.total_planted,
                    'total_bloomed': self.total_bloomed,
                    'total_pruned': self.total_pruned,
                    'season': self.season.value,
                    'last_saved': time.time()
                }
                json.dump(state, f, indent=2)
                
        except Exception as e:
            print(f"[MemoryGarden] Error saving garden: {e}")
    
    def plant(self, moment: Moment) -> MemorySeed:
        """
        Plant a moment as a seed in the garden.
        
        Args:
            moment: The moment to plant
            
        Returns:
            The planted seed
        """
        plot = self._get_plot_for_moment(moment)
        
        # Initial nutrients based on significance
        initial_nutrients = moment.significance.value * 0.15
        
        # Sunlight based on emotional intensity
        initial_sunlight = abs(moment.emotional_context.valence) * 0.5 + 0.25
        
        seed = MemorySeed(
            moment_id=moment.id,
            plot=plot,
            sunlight=initial_sunlight,
            nutrients=initial_nutrients
        )
        
        self.seeds[moment.id] = seed
        self.moments[moment.id] = moment
        self.total_planted += 1
        
        # Mark moment as planted
        moment.planted_at = time.time()
        moment.growth_stage = 0
        
        print(f"[MemoryGarden] Planted seed in {plot.value}: {moment.content[:40]}...")
        self._save_garden()
        
        return seed
    
    def water(self, moment_id: str) -> bool:
        """
        Water a seed or flower (recall/revisit the memory).
        This strengthens the memory and promotes growth.
        """
        if moment_id in self.seeds:
            seed = self.seeds[moment_id]
            seed.water_count += 1
            
            # Check if ready to sprout
            if seed.water_count >= 3 and moment_id in self.moments:
                self._grow_seed(seed)
            
            self._save_garden()
            return True
            
        elif moment_id in self.flowers:
            flower = self.flowers[moment_id]
            
            # Watering flowers increases beauty
            flower.beauty = min(1.0, flower.beauty + 0.1)
            
            # May advance growth stage
            if flower.stage.value < GrowthStage.PERENNIAL.value:
                if random.random() < 0.3:
                    flower.stage = GrowthStage(flower.stage.value + 1)
            
            self._save_garden()
            return True
        
        return False
    
    def _grow_seed(self, seed: MemorySeed):
        """Grow a seed into a sprout, then flower."""
        moment = self.moments.get(seed.moment_id)
        if not moment:
            return
        
        # Calculate growth potential
        growth_score = (
            seed.water_count * 0.2 +
            seed.sunlight * 0.3 +
            seed.nutrients * 0.3 +
            moment.significance.value * 0.2
        )
        
        if growth_score > 0.5:
            # Graduate to flower
            flower = MemoryFlower(
                moment_id=seed.moment_id,
                stage=GrowthStage.FLOWERING,
                plot=seed.plot,
                pollen=moment.tags.copy(),
                beauty=seed.sunlight,
                fragrance=seed.nutrients
            )
            
            self.flowers[seed.moment_id] = flower
            del self.seeds[seed.moment_id]
            self.total_bloomed += 1
            
            moment.growth_stage = 3
            moment.consolidated = True
            
            print(f"[MemoryGarden] 🌸 Memory bloomed: {moment.content[:40]}...")
            
            # Try to cross-pollinate
            self._cross_pollinate(flower)
    
    def _cross_pollinate(self, flower: MemoryFlower):
        """Find connections between flowers based on shared concepts."""
        if not flower.pollen:
            return
        
        for other_id, other_flower in self.flowers.items():
            if other_id == flower.moment_id:
                continue
            
            # Check for shared pollen (tags)
            shared = set(flower.pollen) & set(other_flower.pollen)
            if shared:
                if other_id not in flower.connections:
                    flower.connections.append(other_id)
                if flower.moment_id not in other_flower.connections:
                    other_flower.connections.append(flower.moment_id)
                    
                print(f"[MemoryGarden] 🐝 Cross-pollination: connected via {shared}")
    
    def add_sunlight(self, moment_id: str, amount: float = 0.1):
        """Give attention to a memory."""
        if moment_id in self.seeds:
            self.seeds[moment_id].sunlight = min(1.0, self.seeds[moment_id].sunlight + amount)
        elif moment_id in self.flowers:
            self.flowers[moment_id].beauty = min(1.0, self.flowers[moment_id].beauty + amount)
    
    def add_nutrients(self, moment_id: str, connections: List[str]):
        """Add connections to other memories."""
        if moment_id in self.seeds:
            self.seeds[moment_id].nutrients = min(1.0, self.seeds[moment_id].nutrients + len(connections) * 0.1)
        elif moment_id in self.flowers:
            for conn in connections:
                if conn not in self.flowers[moment_id].connections:
                    self.flowers[moment_id].connections.append(conn)
    
    def prune(self, moment_id: str):
        """Remove a memory from the garden (forgetting)."""
        removed = False
        
        if moment_id in self.seeds:
            del self.seeds[moment_id]
            removed = True
        elif moment_id in self.flowers:
            del self.flowers[moment_id]
            removed = True
        
        if moment_id in self.moments:
            del self.moments[moment_id]
        
        if removed:
            self.total_pruned += 1
            self._save_garden()
            print(f"[MemoryGarden] Pruned memory: {moment_id}")
        
        return removed
    
    def harvest_insights(self, flower_id: str) -> List[str]:
        """Harvest insights (fruits) from a mature flower."""
        if flower_id not in self.flowers:
            return []
        
        flower = self.flowers[flower_id]
        moment = self.moments.get(flower_id)
        
        if flower.stage.value < GrowthStage.FRUITING.value:
            return []
        
        insights = []
        
        # Generate insights based on connections
        if flower.connections and moment:
            connected_moments = [
                self.moments.get(c) for c in flower.connections
                if self.moments.get(c)
            ]
            
            if connected_moments:
                # Simple insight: pattern recognition
                insight = f"Connection observed: {moment.content[:30]} relates to {len(connected_moments)} other memories"
                insights.append(insight)
                flower.fruits.append(insight)
        
        return insights
    
    def get_garden_view(self) -> Dict[str, Any]:
        """Get a visual representation of the garden state."""
        plots = {}
        for plot in PlotType:
            seeds_in_plot = [s for s in self.seeds.values() if s.plot == plot]
            flowers_in_plot = [f for f in self.flowers.values() if f.plot == plot]
            
            if seeds_in_plot or flowers_in_plot:
                plots[plot.value] = {
                    'seeds': len(seeds_in_plot),
                    'flowers': len(flowers_in_plot),
                    'blooming': len([f for f in flowers_in_plot if f.stage == GrowthStage.FLOWERING]),
                    'fruiting': len([f for f in flowers_in_plot if f.stage.value >= GrowthStage.FRUITING.value])
                }
        
        return {
            'season': self.season.value,
            'total_seeds': len(self.seeds),
            'total_flowers': len(self.flowers),
            'plots': plots,
            'garden_age_days': self.garden_age_days,
            'lifetime_stats': {
                'planted': self.total_planted,
                'bloomed': self.total_bloomed,
                'pruned': self.total_pruned
            }
        }
    
    def get_flowers_by_plot(self, plot: PlotType) -> List[Tuple[MemoryFlower, Optional[Moment]]]:
        """Get all flowers in a specific plot."""
        results = []
        for flower in self.flowers.values():
            if flower.plot == plot:
                moment = self.moments.get(flower.moment_id)
                results.append((flower, moment))
        return results
    
    def get_strongest_memories(self, limit: int = 10) -> List[Moment]:
        """Get the most well-established memories."""
        moments_with_score = []
        
        for flower in self.flowers.values():
            moment = self.moments.get(flower.moment_id)
            if moment:
                score = (
                    flower.stage.value * 0.3 +
                    flower.beauty * 0.2 +
                    flower.fragrance * 0.2 +
                    len(flower.connections) * 0.1 +
                    moment.recall_count * 0.1 +
                    moment.significance.value * 0.1
                )
                moments_with_score.append((moment, score))
        
        moments_with_score.sort(key=lambda x: x[1], reverse=True)
        return [m for m, _ in moments_with_score[:limit]]
    
    def tend_garden(self):
        """
        Periodic garden maintenance - should be called regularly.
        Handles natural growth, decay, seasonal changes.
        """
        self.season = self._determine_season()
        self.garden_age_days += 1
        
        # Growth based on season
        growth_modifier = {
            Season.SPRING: 1.2,
            Season.SUMMER: 1.5,
            Season.AUTUMN: 0.8,
            Season.WINTER: 0.5
        }[self.season]
        
        # Process seeds
        seeds_to_grow = []
        for seed_id, seed in self.seeds.items():
            # Natural sunlight
            seed.sunlight += 0.05 * growth_modifier
            
            # Check if ready to grow
            age_hours = (time.time() - seed.planted_at) / 3600
            if age_hours > 24 and seed.water_count >= 2:
                seeds_to_grow.append(seed)
        
        for seed in seeds_to_grow:
            self._grow_seed(seed)
        
        # Process flowers
        for flower in self.flowers.values():
            # Flowers in autumn may fruit
            if self.season == Season.AUTUMN and flower.stage == GrowthStage.FLOWERING:
                if random.random() < 0.2:
                    flower.stage = GrowthStage.FRUITING
            
            # Very old, well-connected flowers become perennial
            moment = self.moments.get(flower.moment_id)
            if moment and moment.age_days > 30 and len(flower.connections) >= 3:
                flower.stage = GrowthStage.PERENNIAL
        
        self._save_garden()
        print(f"[MemoryGarden] Garden tended. Season: {self.season.value}")
    
    def describe_garden(self) -> str:
        """Get a poetic description of the garden's current state."""
        view = self.get_garden_view()
        
        season_desc = {
            Season.SPRING: "The garden awakens with new growth",
            Season.SUMMER: "The garden flourishes under warm attention",
            Season.AUTUMN: "Golden memories ripen in the autumn light",
            Season.WINTER: "The garden rests, memories crystallized in frost"
        }[self.season]
        
        lines = [
            f"🌿 {season_desc}",
            f"",
            f"Seeds waiting to grow: {view['total_seeds']}",
            f"Flowers in bloom: {view['total_flowers']}",
        ]
        
        if view['plots']:
            lines.append("")
            lines.append("Garden plots:")
            for plot_name, stats in view['plots'].items():
                plot_display = plot_name.replace('_', ' ').title()
                lines.append(f"  🌱 {plot_display}: {stats['seeds']} seeds, {stats['flowers']} flowers")
        
        return "\n".join(lines)
