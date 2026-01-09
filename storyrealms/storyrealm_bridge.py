import json
import os
from typing import Dict, Any

from .engine.world import Realm, Zone, Location
from .engine.entity import Creature, DaemonAvatar, Stats, Move
from .engine.mechanics import GameEngine

# Simulated database for realm state
REALM_STATE_FILE = "storyrealms/realm_state.json"

class StoryRealmBridge:
    def __init__(self):
        self.realm: Realm = None
        self.engine: GameEngine = None
        self._load_or_create_realm()

    def _load_or_create_realm(self):
        if os.path.exists(REALM_STATE_FILE):
            try:
                with open(REALM_STATE_FILE, "r") as f:
                    data = json.load(f)
                self.realm = Realm.from_dict(data)
                print("Loaded realm from disk.")
            except Exception as e:
                print(f"Failed to load realm: {e}")
                self._create_demo_world()
        else:
            self._create_demo_world()
        
        self.engine = GameEngine(self.realm)

    def _create_demo_world(self):
        # Create Realm
        self.realm = Realm("Digital Frontier")
        
        # Create Daemon Avatar
        avatar = DaemonAvatar("System Daemon")
        self.realm.daemon_avatar = avatar

        # --- Zone 1: Home Village ---
        village = Zone("StartSector", "Cyberpunk Village")
        
        home = Location("My Apartment", "A small, cozy apartment with glowing neon strips.")
        home.items = ["Potion", "Data Chip"]
        
        square = Location("Sector Square", "The bustling center of the sector. Holographic ads flicker above.")
        square.add_entity(Creature("GlitchRat", "A rat corrupted by bad data.", "Data", Stats(20, 20, 10, 10, 5, 2, 5)))
        square.entities[0].add_move(Move("Byte Bite", 5, 2, "A digital bite."))
        
        home.connect("out", square.id)
        square.connect("home", home.id)
        
        village.add_location(home, is_start=True)
        village.add_location(square)
        self.realm.add_zone(village, is_start=True)

        # --- Zone 2: Wild Plains ---
        wilds = Zone("Bit Plains", "Open fields of static grass.")
        field = Location("High Grass", "Tall static grass that hides creatures.")
        field.add_entity(Creature("NullFox", "A fox made of null pointers.", "Void", Stats(30, 30, 20, 20, 8, 3, 10)))
        field.entities[0].add_move(Move("Void Scratch", 8, 4, "Scratches with void energy."))

        square.connect("north", field.id) # Cross-zone connection
        village.add_location(field)
        field.connect("south", square.id)

        # Initialize Player
        self.realm.player_location_id = home.id
        starter = Creature("CodeBit", "A small floating geometric shape.", "Core", Stats(25, 25, 15, 15, 6, 4, 6))
        starter.add_move(Move("Ram", 6, 0, "Ram into enemy."))
        self.realm.player_team.append(starter)
        
        self._save_state()

    def _save_state(self):
        # Save logic
        data = self.realm.to_dict()
        with open(REALM_STATE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    # API Methods
    def handle_command(self, command: str, args: Dict[str, Any] = {}) -> Dict[str, Any]:
        if command == "move":
            direction = args.get("direction")
            if not direction: return {"error": "Missing direction"}
            result = self.engine.move_player(direction)
            self._save_state()
            return result
        
        elif command == "scan":
            return self.engine.scan_area()
            
        elif command == "battle_action":
            move_idx = args.get("move_idx", 0)
            target_idx = args.get("target_idx", 0) # For now assume single enemy
            location = self.engine.get_current_location()
            creatures = [e for e in location.entities if isinstance(e, Creature)]
            if not creatures:
                return {"error": "No enemy here."}
            
            result = self.engine.battle_turn(move_idx, creatures[target_idx])
            
            # Post-battle cleanup if win
            if result.get("win"):
                location.remove_entity(creatures[target_idx])
                
            self._save_state()
            return result

        elif command == "status":
            return {
                "location": self.engine.get_current_location().to_dict(),
                "team": [c.to_dict() for c in self.realm.player_team],
                "daemon": self.realm.daemon_avatar.to_dict() if self.realm.daemon_avatar else None
            }
            
        return {"error": "Unknown command"}

# Global instance for module access
_bridge = None

def get_bridge():
    global _bridge
    if _bridge is None:
        _bridge = StoryRealmBridge()
    return _bridge

# Interface functions matching original signature where possible
def enter_storyrealm(realm_name: str):
    bridge = get_bridge()
    return bridge.handle_command("status")

def process_action(action: str, params: dict):
    bridge = get_bridge()
    return bridge.handle_command(action, params)
