import random
from typing import Dict, Any, Tuple
from .world import Realm, Zone, Location
from .entity import Creature, Move, Stats, DaemonAvatar

class GameEngine:
    def __init__(self, realm: Realm):
        self.realm = realm

    def get_current_location(self) -> Location:
        zone = self.realm.zones[self.realm.current_zone_id]
        return zone.get_location(self.realm.player_location_id)

    def move_player(self, direction: str) -> Dict[str, Any]:
        location = self.get_current_location()
        if direction in location.exits:
            new_loc_id = location.exits[direction]
            self.realm.player_location_id = new_loc_id
            new_location = self.get_current_location()
            
            # Check for encounters
            encounter = self._check_encounter(new_location)
            
            return {
                "success": True,
                "message": f"Moved {direction} to {new_location.name}.",
                "location": new_location.to_dict(),
                "encounter": encounter
            }
        else:
            return {"success": False, "message": "You cannot go that way."}

    def _check_encounter(self, location: Location) -> Dict[str, Any]:
        # Simple random encounter logic if there are entities in the location
        wild_creatures = [e for e in location.entities if isinstance(e, Creature)]
        if wild_creatures and random.random() < 0.3:
            creature = random.choice(wild_creatures)
            return {
                "occurred": True,
                "type": "wild_battle",
                "entity": creature.to_dict()
            }
        return {"occurred": False}

    def scan_area(self) -> Dict[str, Any]:
        if not self.realm.daemon_avatar:
            return {"success": False, "message": "Daemon avatar not active."}
        
        location = self.get_current_location()
        return {
            "success": True,
            "analysis": self.realm.daemon_avatar.analyze_target(location),
            "entities": [e.name for e in location.entities],
            "items": location.items
        }

    def daemon_assist(self, context: str) -> str:
        # Placeholder for AI logic
        return f"Daemon: Analyzing situation regarding {context}..."

    def battle_turn(self, player_move_idx: int, target_creature: Creature) -> Dict[str, Any]:
        if not self.realm.player_team:
            return {"success": False, "message": "You have no creatures!"}
        
        active_creature = self.realm.player_team[0] # Simplification
        
        if player_move_idx >= len(active_creature.moves):
             return {"success": False, "message": "Invalid move."}

        move = active_creature.moves[player_move_idx]
        
        # Player attacks
        damage = move.damage # Simplification of damage calc
        is_fainted = target_creature.take_damage(damage)
        
        log = [f"{active_creature.name} used {move.name}! Dealt {damage} damage."]
        
        if is_fainted:
            log.append(f"{target_creature.name} fainted!")
            return {"success": True, "log": log, "battle_over": True, "win": True}

        # Enemy attacks back
        if target_creature.moves:
            enemy_move = random.choice(target_creature.moves)
            dmg_to_player = enemy_move.damage
            player_fainted = active_creature.take_damage(dmg_to_player)
            log.append(f"{target_creature.name} used {enemy_move.name}! Dealt {dmg_to_player} damage.")
            
            if player_fainted:
                 log.append(f"{active_creature.name} fainted!")
                 return {"success": True, "log": log, "battle_over": True, "win": False}
        
        return {
            "success": True, 
            "log": log, 
            "battle_over": False,
            "player_hp": active_creature.stats.hp,
            "enemy_hp": target_creature.stats.hp
        }
