import os
import psutil
import socket
import platform
from .engine import Realm

class SystemMapper:
    def __init__(self, world_engine):
        self.world_engine = world_engine

    def map_filesystem(self, root_path, realm_name=None):
        """
        Maps a directory structure into a Story Realm.
        Folders become 'Regions' (in description/state), Files become 'Artifacts' (Entities).
        """
        if not os.path.exists(root_path):
            return f"[SystemMapper] Path not found: {root_path}"

        root_name = os.path.basename(os.path.abspath(root_path))
        if not realm_name:
            realm_name = f"System_{root_name}"

        description = f"A crystalline construct representing the file system at {root_path}."
        
        # Collect entities
        entities = []
        structure_map = {}
        
        # Limit depth for performance
        max_depth = 3
        root_depth = root_path.rstrip(os.sep).count(os.sep)

        for root, dirs, files in os.walk(root_path):
            current_depth = root.count(os.sep) - root_depth
            if current_depth > max_depth:
                del dirs[:] # Don't go deeper
                continue

            rel_path = os.path.relpath(root, root_path)
            if rel_path == ".": rel_path = "Root"
            
            # Map folders
            structure_map[rel_path] = {
                "type": "Region",
                "subregions": dirs,
                "artifacts": files
            }

            # Create entities for interesting files
            for f in files:
                if f.endswith(('.py', '.rs', '.js', '.c', '.cpp', '.h', '.md', '.txt')):
                    file_path = os.path.join(root, f)
                    size = os.path.getsize(file_path)
                    
                    # Basic "Lore" extraction (read header/first lines)
                    lore = ""
                    try:
                        with open(file_path, 'r', errors='ignore') as code_file:
                            head = [next(code_file) for _ in range(5)]
                            lore = "".join(head).strip()
                    except:
                        lore = "Unreadable ancient script."

                    entity = {
                        "name": f,
                        "type": "Artifact",
                        "location": rel_path,
                        "description": lore,
                        "properties": {
                            "size": size,
                            "extension": f.split('.')[-1],
                            "path": file_path
                        }
                    }
                    entities.append(entity)

        # Create Realm
        realm = self.world_engine.create_realm(realm_name, description)
        realm.entities = entities
        realm.state["structure"] = structure_map
        realm.state["origin_path"] = os.path.abspath(root_path)
        
        self.world_engine.save_realm(realm)
        return f"[SystemMapper] Mapped filesystem '{root_path}' to Realm '{realm_name}'."

    def map_active_runtime(self):
        """
        Maps the currently running OS processes and network into a Realm.
        """
        hostname = socket.gethostname()
        realm_name = f"Runtime_{hostname}"
        description = f"The living, breathing runtime environment of {hostname}."
        
        entities = []
        
        # Map Processes as 'Spirits' or 'Constructs'
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                pinfo = proc.info
                entity = {
                    "name": pinfo['name'],
                    "type": "Construct",
                    "id": pinfo['pid'],
                    "properties": {
                        "username": pinfo['username']
                    }
                }
                entities.append(entity)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Map Network Interfaces as 'Gateways'
        addrs = psutil.net_if_addrs()
        for nic, snics in addrs.items():
            for snic in snics:
                if snic.family == socket.AF_INET:
                    entity = {
                        "name": nic,
                        "type": "Gateway",
                        "properties": {
                            "ip": snic.address,
                            "netmask": snic.netmask
                        }
                    }
                    entities.append(entity)

        # Create Realm
        realm = self.world_engine.create_realm(realm_name, description)
        realm.entities = entities
        realm.state["os_info"] = {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine()
        }
        
        self.world_engine.save_realm(realm)
        return f"[SystemMapper] Mapped runtime to Realm '{realm_name}'."

    def diff_realms(self, realm_a_name, realm_b_name):
        """
        Compares two Realms (presumably snapshots of the same system at different times)
        to detect anomalies, intruders, or mutations.
        """
        if realm_a_name not in self.world_engine.realms or realm_b_name not in self.world_engine.realms:
            return "[SystemMapper] One or both realms not found."

        realm_a = self.world_engine.realms[realm_a_name]
        realm_b = self.world_engine.realms[realm_b_name]

        report = [f"--- Anomaly Report: {realm_a_name} vs {realm_b_name} ---"]
        
        # 1. Compare Entities (Constructs/Artifacts)
        entities_a = {e["name"]: e for e in realm_a.entities}
        entities_b = {e["name"]: e for e in realm_b.entities}
        
        added = set(entities_b.keys()) - set(entities_a.keys())
        removed = set(entities_a.keys()) - set(entities_b.keys())
        
        if added:
            report.append(f"\n[!] New Entities Detected ({len(added)}):")
            for name in added:
                report.append(f"  + {name} ({entities_b[name].get('type', 'Unknown')})")

        if removed:
            report.append(f"\n[-] Entities Vanished ({len(removed)}):")
            for name in removed:
                report.append(f"  - {name}")

        # 2. Compare Properties of Common Entities
        common = set(entities_a.keys()) & set(entities_b.keys())
        mutated = []
        for name in common:
            ea = entities_a[name]
            eb = entities_b[name]
            
            # Simple size check
            size_a = ea.get("properties", {}).get("size", 0)
            size_b = eb.get("properties", {}).get("size", 0)
            
            if size_a != size_b:
                mutated.append(f"  ~ {name}: Mass changed {size_a} -> {size_b}")
                
        if mutated:
            report.append(f"\n[~] Mutations Detected ({len(mutated)}):")
            for m in mutated:
                report.append(m)

        if not added and not removed and not mutated:
            report.append("\nNo anomalies detected. Systems are identical.")

        return "\n".join(report)

    def materialize_realm(self, realm_name, target_path):
        """
        Reconstructs a Realm back into a physical directory structure.
        Useful for procedural generation or restoring backups.
        """
        if realm_name not in self.world_engine.realms:
            return f"[SystemMapper] Realm '{realm_name}' not found."
            
        realm = self.world_engine.realms[realm_name]
        
        if not os.path.exists(target_path):
            os.makedirs(target_path)
            
        log = []
        
        # 1. Recreate Structure (Regions)
        structure = realm.state.get("structure", {})
        for rel_path, data in structure.items():
            if rel_path == "Root": continue
            full_path = os.path.join(target_path, rel_path)
            os.makedirs(full_path, exist_ok=True)
            
        # 2. Recreate Artifacts (Empty placeholders or restore if content saved)
        # Currently we only save "Lore" (snippets), so we can't fully restore code unless we upgrade the mapper.
        # But we can create the scaffolding.
        for entity in realm.entities:
            if entity.get("type") == "Artifact":
                rel_loc = entity.get("location", "")
                name = entity.get("name", "artifact")
                
                # Handle Root case
                if rel_loc == "Root":
                    full_path = os.path.join(target_path, name)
                else:
                    full_path = os.path.join(target_path, rel_loc, name)
                
                # Create file
                with open(full_path, "w") as f:
                    description = entity.get("description", "")
                    f.write(f"# Restored Artifact: {name}\n# Lore: {description}\n\n# [Content Reconstruct Pending]")
                log.append(f"Materialized: {name}")

        return f"[SystemMapper] Realm materialized at {target_path}. Created {len(log)} artifacts."
