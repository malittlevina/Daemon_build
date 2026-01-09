# storyrealms/procedural_gen.py
"""
Story Realms Procedural Generation

Generates dynamic content for Story Realms: locations, NPCs, quests,
items, and narrative elements. AI-native design for emergent storytelling.
"""

import random
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class GenerationType(Enum):
    LOCATION = "location"
    NPC = "npc"
    CREATURE = "creature"
    ITEM = "item"
    QUEST = "quest"
    EVENT = "event"
    DIALOG = "dialog"
    NAME = "name"


@dataclass
class GenerationTemplate:
    """Template for procedural generation."""
    id: str
    gen_type: GenerationType
    name: str
    patterns: List[Dict] = field(default_factory=list)
    attributes: Dict = field(default_factory=dict)
    weights: Dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


class ProceduralGenerator:
    """
    Procedural content generator for Story Realms.
    
    Provides:
    - Location generation (dungeons, towns, wilderness)
    - NPC generation with personalities and backstories
    - Quest generation with objectives and rewards
    - Item generation with properties
    - Name generation for entities and places
    - Event generation for world dynamics
    """
    
    def __init__(self, world_engine, seed: int = None):
        self.world_engine = world_engine
        self.seed = seed or int(time.time())
        self.rng = random.Random(self.seed)
        
        # Templates for generation
        self.templates: Dict[GenerationType, List[GenerationTemplate]] = {}
        
        # Generation history for coherence
        self.generation_history: List[Dict] = []
        
        # Name databases
        self.name_parts = self._load_default_name_parts()
        
        # Load default templates
        self._load_default_templates()
        
        print(f"[ProceduralGen] Initialized with seed: {self.seed}")
    
    # ─────────────────────────────────────────────────────────────────
    # GENERATION TRIGGERS
    # ─────────────────────────────────────────────────────────────────
    
    def check_generation_triggers(self):
        """Check if any procedural generation should occur."""
        # Check entity density
        if self.world_engine._entity_manager:
            entities = list(self.world_engine._entity_manager.entities.values())
            
            # Generate NPCs if population is low
            npc_count = sum(1 for e in entities if e.entity_type.value == "npc")
            if npc_count < 5:
                self.generate_npc()
            
            # Generate events based on world time
            world_time = self.world_engine.world_time
            if world_time > 0 and int(world_time) % 10 == 0:
                if self.rng.random() < 0.3:  # 30% chance
                    self.generate_event()
    
    # ─────────────────────────────────────────────────────────────────
    # LOCATION GENERATION
    # ─────────────────────────────────────────────────────────────────
    
    def generate_location(
        self,
        location_type: str = None,
        parent_location: str = None,
        **kwargs
    ) -> Dict:
        """
        Generate a new location.
        
        Args:
            location_type: Type of location (town, dungeon, wilderness, etc.)
            parent_location: ID of containing location
        """
        location_types = ["town", "village", "dungeon", "forest", "mountain", "cave", "ruins", "temple"]
        location_type = location_type or self.rng.choice(location_types)
        
        # Generate name
        name = self.generate_name("location", style=location_type)
        
        # Generate attributes based on type
        attributes = self._generate_location_attributes(location_type)
        
        # Create location entity
        if self.world_engine._entity_manager:
            from storyrealms.entity_system import EntityType
            
            location = self.world_engine._entity_manager.spawn(
                name=name,
                entity_type=EntityType.LOCATION,
                attributes={
                    "location_type": location_type,
                    "parent": parent_location,
                    **attributes
                }
            )
            
            result = {
                "type": "location",
                "id": location.id,
                "name": name,
                "location_type": location_type,
                "attributes": attributes
            }
            
            self._record_generation(result)
            return result
        
        return {"type": "location", "name": name, "location_type": location_type}
    
    def _generate_location_attributes(self, location_type: str) -> Dict:
        """Generate attributes for a location type."""
        attributes = {
            "danger_level": self.rng.randint(1, 10),
            "resources": [],
            "features": []
        }
        
        if location_type == "town":
            attributes["population"] = self.rng.randint(100, 5000)
            attributes["prosperity"] = self.rng.choice(["poor", "modest", "wealthy", "rich"])
            attributes["features"] = self.rng.sample(
                ["market", "inn", "temple", "blacksmith", "library", "guild_hall"],
                k=self.rng.randint(2, 5)
            )
            attributes["danger_level"] = self.rng.randint(1, 3)
        
        elif location_type == "dungeon":
            attributes["depth"] = self.rng.randint(1, 5)
            attributes["danger_level"] = self.rng.randint(5, 10)
            attributes["features"] = ["traps", "monsters", "treasure"]
            attributes["theme"] = self.rng.choice(["undead", "goblin", "dragon", "ancient", "cursed"])
        
        elif location_type == "forest":
            attributes["density"] = self.rng.choice(["sparse", "moderate", "dense", "ancient"])
            attributes["features"] = self.rng.sample(
                ["clearing", "stream", "wildlife", "ruins", "herbs"],
                k=self.rng.randint(1, 3)
            )
        
        return attributes
    
    # ─────────────────────────────────────────────────────────────────
    # NPC GENERATION
    # ─────────────────────────────────────────────────────────────────
    
    def generate_npc(
        self,
        role: str = None,
        location_id: str = None,
        **kwargs
    ) -> Dict:
        """
        Generate a new NPC with personality and backstory.
        
        Args:
            role: NPC role (merchant, guard, villager, etc.)
            location_id: Where to spawn the NPC
        """
        roles = ["merchant", "guard", "villager", "scholar", "adventurer", "craftsman", "innkeeper", "priest"]
        role = role or self.rng.choice(roles)
        
        # Generate name
        name = self.generate_name("npc")
        
        # Generate personality
        personality = self._generate_personality()
        
        # Generate backstory elements
        backstory = self._generate_backstory(role)
        
        # Generate attributes
        attributes = self._generate_npc_attributes(role)
        
        # Create NPC entity
        if self.world_engine._entity_manager:
            from storyrealms.entity_system import EntityType
            
            npc = self.world_engine._entity_manager.spawn(
                name=name,
                entity_type=EntityType.NPC,
                location_id=location_id,
                personality=personality,
                attributes={
                    "role": role,
                    "backstory": backstory,
                    **attributes
                }
            )
            
            # Add health component
            npc.add_component("health", {"current": 100, "max": 100})
            
            result = {
                "type": "npc",
                "id": npc.id,
                "name": name,
                "role": role,
                "personality": personality,
                "backstory": backstory
            }
            
            self._record_generation(result)
            return result
        
        return {"type": "npc", "name": name, "role": role, "personality": personality}
    
    def _generate_personality(self) -> Dict:
        """Generate a personality profile for an NPC."""
        traits = ["kind", "gruff", "curious", "suspicious", "jovial", "melancholy", "wise", "naive"]
        motivations = ["wealth", "knowledge", "power", "family", "adventure", "peace", "revenge", "love"]
        fears = ["death", "failure", "loneliness", "darkness", "betrayal", "the_unknown"]
        
        return {
            "primary_trait": self.rng.choice(traits),
            "secondary_trait": self.rng.choice([t for t in traits if t != traits[0]]),
            "motivation": self.rng.choice(motivations),
            "fear": self.rng.choice(fears),
            "greeting": self._generate_greeting(),
            "speech_style": self.rng.choice(["formal", "casual", "gruff", "poetic", "terse"])
        }
    
    def _generate_backstory(self, role: str) -> Dict:
        """Generate backstory elements for an NPC."""
        origins = ["local", "traveler", "refugee", "noble_fallen", "common_risen", "mysterious"]
        
        backstory = {
            "origin": self.rng.choice(origins),
            "years_in_role": self.rng.randint(1, 30),
            "notable_event": self._generate_notable_event(),
            "secret": self._generate_secret() if self.rng.random() < 0.3 else None
        }
        
        return backstory
    
    def _generate_notable_event(self) -> str:
        """Generate a notable event from the NPC's past."""
        events = [
            "survived a monster attack",
            "lost a loved one to illness",
            "discovered a hidden treasure",
            "was saved by a mysterious stranger",
            "witnessed a great battle",
            "made a deal they regret",
            "received a blessing from a deity",
            "escaped from a dangerous situation"
        ]
        return self.rng.choice(events)
    
    def _generate_secret(self) -> str:
        """Generate a secret for an NPC."""
        secrets = [
            "has a hidden stash of valuables",
            "is not who they claim to be",
            "knows the location of something important",
            "is being blackmailed",
            "has magical abilities they hide",
            "witnessed a crime and stayed silent",
            "is searching for a lost relative"
        ]
        return self.rng.choice(secrets)
    
    def _generate_greeting(self) -> str:
        """Generate a greeting for an NPC."""
        greetings = [
            "Well met, traveler.",
            "What brings you here?",
            "Ah, a new face!",
            "State your business.",
            "Welcome, friend.",
            "Haven't seen you around before.",
            "Good day to you.",
            "Hmm? What do you want?"
        ]
        return self.rng.choice(greetings)
    
    def _generate_npc_attributes(self, role: str) -> Dict:
        """Generate attributes based on NPC role."""
        base_attrs = {
            "level": self.rng.randint(1, 10),
            "gold": self.rng.randint(10, 500)
        }
        
        role_attrs = {
            "merchant": {"trade_skill": self.rng.randint(5, 10), "inventory_size": self.rng.randint(10, 50)},
            "guard": {"combat_skill": self.rng.randint(5, 10), "armor": self.rng.choice(["light", "medium", "heavy"])},
            "scholar": {"knowledge": self.rng.randint(5, 10), "research_topic": self.rng.choice(["history", "magic", "creatures", "artifacts"])},
            "adventurer": {"combat_skill": self.rng.randint(3, 8), "exploration": self.rng.randint(3, 8)},
        }
        
        base_attrs.update(role_attrs.get(role, {}))
        return base_attrs
    
    # ─────────────────────────────────────────────────────────────────
    # QUEST GENERATION
    # ─────────────────────────────────────────────────────────────────
    
    def generate_quest(
        self,
        quest_type: str = None,
        giver_id: str = None,
        difficulty: int = None,
        **kwargs
    ) -> Dict:
        """
        Generate a new quest.
        
        Args:
            quest_type: Type of quest (fetch, kill, escort, investigate, etc.)
            giver_id: Entity ID of quest giver
            difficulty: 1-10 difficulty rating
        """
        quest_types = ["fetch", "kill", "escort", "investigate", "deliver", "rescue", "explore"]
        quest_type = quest_type or self.rng.choice(quest_types)
        difficulty = difficulty or self.rng.randint(1, 10)
        
        # Generate quest details
        title = self._generate_quest_title(quest_type)
        description = self._generate_quest_description(quest_type)
        objectives = self._generate_quest_objectives(quest_type, difficulty)
        rewards = self._generate_quest_rewards(difficulty)
        
        result = {
            "type": "quest",
            "quest_type": quest_type,
            "title": title,
            "description": description,
            "objectives": objectives,
            "rewards": rewards,
            "difficulty": difficulty,
            "giver_id": giver_id
        }
        
        # Create narrative if engine available
        if self.world_engine._narrative_engine:
            narrative = self.world_engine._narrative_engine.create_quest(
                title=title,
                description=description,
                objectives=objectives,
                rewards=rewards
            )
            result["narrative_id"] = narrative.id
        
        self._record_generation(result)
        return result
    
    def _generate_quest_title(self, quest_type: str) -> str:
        """Generate a quest title."""
        templates = {
            "fetch": ["The Lost {item}", "Retrieve the {item}", "A {item} for {name}"],
            "kill": ["Slay the {creature}", "Hunt for {creature}s", "The {creature} Menace"],
            "escort": ["Safe Passage", "Protect {name}", "The Journey to {place}"],
            "investigate": ["Mystery of {place}", "Strange Happenings", "The {adjective} Secret"],
            "deliver": ["Special Delivery", "A Package for {name}", "Time-Sensitive Cargo"],
            "rescue": ["Save {name}", "The Captured {role}", "A Cry for Help"],
            "explore": ["Uncharted Territory", "Beyond the {place}", "Mapping the Unknown"]
        }
        
        template = self.rng.choice(templates.get(quest_type, ["A New Quest"]))
        
        # Fill in placeholders
        replacements = {
            "{item}": self.rng.choice(["Amulet", "Scroll", "Sword", "Ring", "Tome", "Crystal"]),
            "{creature}": self.rng.choice(["Wolf", "Goblin", "Troll", "Spider", "Bandit", "Ghost"]),
            "{name}": self.generate_name("npc"),
            "{place}": self.generate_name("location"),
            "{role}": self.rng.choice(["merchant", "scholar", "child", "noble"]),
            "{adjective}": self.rng.choice(["Ancient", "Dark", "Hidden", "Forbidden"])
        }
        
        for key, value in replacements.items():
            template = template.replace(key, value)
        
        return template
    
    def _generate_quest_description(self, quest_type: str) -> str:
        """Generate a quest description."""
        descriptions = {
            "fetch": "An important item has been lost and must be recovered.",
            "kill": "A dangerous threat must be eliminated to protect the people.",
            "escort": "Someone needs safe passage through dangerous territory.",
            "investigate": "Strange events require investigation by a capable adventurer.",
            "deliver": "An urgent package must reach its destination.",
            "rescue": "Someone has been captured and needs to be saved.",
            "explore": "Unknown lands await discovery by the brave."
        }
        return descriptions.get(quest_type, "A task awaits completion.")
    
    def _generate_quest_objectives(self, quest_type: str, difficulty: int) -> List[Dict]:
        """Generate objectives for a quest."""
        objectives = []
        
        if quest_type == "fetch":
            objectives.append({
                "description": "Find the target item",
                "type": "find_item",
                "conditions": [{"type": "has_item"}]
            })
            objectives.append({
                "description": "Return the item to the quest giver",
                "type": "return",
                "conditions": [{"type": "at_location"}]
            })
        
        elif quest_type == "kill":
            count = min(1 + difficulty // 2, 10)
            objectives.append({
                "description": f"Defeat {count} enemies",
                "type": "kill",
                "target_count": count,
                "conditions": [{"type": "kill_count", "count": count}]
            })
        
        elif quest_type == "escort":
            objectives.append({
                "description": "Escort the target to safety",
                "type": "escort",
                "conditions": [{"type": "escort_alive"}, {"type": "at_location"}]
            })
        
        else:
            objectives.append({
                "description": "Complete the objective",
                "type": "generic",
                "conditions": []
            })
        
        return objectives
    
    def _generate_quest_rewards(self, difficulty: int) -> List[Dict]:
        """Generate rewards for quest completion."""
        rewards = []
        
        # Gold reward
        base_gold = difficulty * 50
        rewards.append({
            "type": "gold",
            "amount": base_gold + self.rng.randint(0, base_gold // 2)
        })
        
        # Experience
        rewards.append({
            "type": "experience",
            "amount": difficulty * 100
        })
        
        # Chance for item reward
        if self.rng.random() < 0.3 + (difficulty * 0.05):
            rewards.append({
                "type": "item",
                "item_type": self.rng.choice(["weapon", "armor", "consumable", "artifact"])
            })
        
        return rewards
    
    # ─────────────────────────────────────────────────────────────────
    # EVENT GENERATION
    # ─────────────────────────────────────────────────────────────────
    
    def generate_event(self, event_type: str = None, **kwargs) -> Dict:
        """Generate a world event."""
        event_types = ["merchant_arrival", "monster_attack", "festival", "storm", "discovery", "visitor"]
        event_type = event_type or self.rng.choice(event_types)
        
        event = {
            "type": "event",
            "event_type": event_type,
            "timestamp": time.time(),
            "world_time": self.world_engine.world_time,
            "data": self._generate_event_data(event_type)
        }
        
        # Emit to world engine
        self.world_engine._emit_event("procedural_event", event)
        
        self._record_generation(event)
        return event
    
    def _generate_event_data(self, event_type: str) -> Dict:
        """Generate data for a specific event type."""
        data = {}
        
        if event_type == "merchant_arrival":
            data["merchant_name"] = self.generate_name("npc")
            data["goods"] = self.rng.sample(
                ["weapons", "armor", "potions", "scrolls", "exotic_goods", "food"],
                k=self.rng.randint(2, 4)
            )
            data["duration"] = self.rng.randint(1, 3)  # days
        
        elif event_type == "monster_attack":
            data["creature"] = self.rng.choice(["wolves", "goblins", "bandits", "undead"])
            data["strength"] = self.rng.randint(1, 5)
            data["target"] = "random_location"
        
        elif event_type == "festival":
            data["name"] = f"Festival of {self.rng.choice(['Harvest', 'Stars', 'Ancestors', 'Fortune'])}"
            data["duration"] = self.rng.randint(1, 3)
            data["effects"] = ["increased_trade", "happy_npcs"]
        
        elif event_type == "storm":
            data["severity"] = self.rng.choice(["light", "moderate", "severe"])
            data["duration"] = self.rng.randint(1, 6)  # hours
        
        return data
    
    # ─────────────────────────────────────────────────────────────────
    # NAME GENERATION
    # ─────────────────────────────────────────────────────────────────
    
    def generate_name(self, name_type: str = "npc", style: str = None) -> str:
        """
        Generate a name for an entity or place.
        
        Args:
            name_type: Type of name (npc, location, item, etc.)
            style: Style modifier (location_type for places, etc.)
        """
        if name_type == "npc":
            return self._generate_npc_name()
        elif name_type == "location":
            return self._generate_location_name(style)
        elif name_type == "item":
            return self._generate_item_name()
        else:
            return self._generate_generic_name()
    
    def _generate_npc_name(self) -> str:
        """Generate an NPC name."""
        first_names = self.name_parts.get("first_names", ["Unknown"])
        surnames = self.name_parts.get("surnames", [])
        
        name = self.rng.choice(first_names)
        if surnames and self.rng.random() < 0.7:
            name += " " + self.rng.choice(surnames)
        
        return name
    
    def _generate_location_name(self, location_type: str = None) -> str:
        """Generate a location name."""
        prefixes = self.name_parts.get("location_prefixes", ["Old"])
        roots = self.name_parts.get("location_roots", ["town"])
        suffixes = self.name_parts.get("location_suffixes", [""])
        
        name_parts = []
        
        if self.rng.random() < 0.4:
            name_parts.append(self.rng.choice(prefixes))
        
        name_parts.append(self.rng.choice(roots))
        
        if self.rng.random() < 0.5:
            name_parts.append(self.rng.choice(suffixes))
        
        return "".join(name_parts)
    
    def _generate_item_name(self) -> str:
        """Generate an item name."""
        adjectives = ["Ancient", "Shining", "Cursed", "Blessed", "Rusted", "Enchanted"]
        materials = ["Iron", "Silver", "Golden", "Crystal", "Obsidian", "Mithril"]
        items = ["Sword", "Shield", "Ring", "Amulet", "Staff", "Helm"]
        
        parts = []
        if self.rng.random() < 0.5:
            parts.append(self.rng.choice(adjectives))
        if self.rng.random() < 0.5:
            parts.append(self.rng.choice(materials))
        parts.append(self.rng.choice(items))
        
        return " ".join(parts)
    
    def _generate_generic_name(self) -> str:
        """Generate a generic fantasy name."""
        syllables = ["ar", "bel", "cor", "dan", "el", "fir", "gal", "hal", "il", "jor",
                     "kel", "lor", "mor", "nar", "or", "per", "quel", "ral", "sar", "tal"]
        
        length = self.rng.randint(2, 4)
        name = "".join(self.rng.choice(syllables) for _ in range(length))
        return name.capitalize()
    
    def _load_default_name_parts(self) -> Dict:
        """Load default name parts for generation."""
        return {
            "first_names": [
                "Aldric", "Brenna", "Cedric", "Dara", "Elwin", "Fiona", "Gareth", "Helena",
                "Ivan", "Jessa", "Kira", "Liam", "Mira", "Nolan", "Ophelia", "Pax",
                "Quinn", "Rowan", "Sera", "Thane", "Una", "Vex", "Wren", "Xander", "Yara", "Zara"
            ],
            "surnames": [
                "Blackwood", "Ironforge", "Stormwind", "Brightblade", "Shadowmend",
                "Thornhill", "Goldleaf", "Silverstream", "Darkhollow", "Lightbringer"
            ],
            "location_prefixes": [
                "Old", "New", "East", "West", "North", "South", "Upper", "Lower",
                "High", "Dark", "Bright", "Lost", "Ancient"
            ],
            "location_roots": [
                "haven", "hold", "dale", "ford", "vale", "wood", "stone", "bridge",
                "gate", "watch", "peak", "moor", "marsh", "glen", "cliff"
            ],
            "location_suffixes": [
                "ton", "ville", "burg", "keep", "fell", "shire", "land", "reach"
            ]
        }
    
    # ─────────────────────────────────────────────────────────────────
    # TEMPLATE MANAGEMENT
    # ─────────────────────────────────────────────────────────────────
    
    def add_template(self, template: GenerationTemplate):
        """Add a generation template."""
        if template.gen_type not in self.templates:
            self.templates[template.gen_type] = []
        self.templates[template.gen_type].append(template)
    
    def get_templates(self, gen_type: GenerationType) -> List[GenerationTemplate]:
        """Get templates for a generation type."""
        return self.templates.get(gen_type, [])
    
    def _load_default_templates(self):
        """Load default generation templates."""
        # Add some basic templates
        pass  # Templates can be added as needed
    
    # ─────────────────────────────────────────────────────────────────
    # HISTORY & COHERENCE
    # ─────────────────────────────────────────────────────────────────
    
    def _record_generation(self, result: Dict):
        """Record a generation for coherence tracking."""
        result["generated_at"] = time.time()
        result["world_time"] = self.world_engine.world_time
        self.generation_history.append(result)
        
        # Keep history bounded
        if len(self.generation_history) > 100:
            self.generation_history = self.generation_history[-100:]
    
    def get_generation_history(self, gen_type: str = None, limit: int = 10) -> List[Dict]:
        """Get recent generation history."""
        history = self.generation_history
        if gen_type:
            history = [h for h in history if h.get("type") == gen_type]
        return history[-limit:]
    
    def set_seed(self, seed: int):
        """Reset the random seed."""
        self.seed = seed
        self.rng = random.Random(seed)
        print(f"[ProceduralGen] Seed reset to: {seed}")
