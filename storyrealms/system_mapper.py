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

    def analyze_realm(self, realm_name):
        """
        Performs a structural analysis (breakdown) of a mapped System Realm.
        """
        if realm_name not in self.world_engine.realms:
            return f"[SystemMapper] Realm '{realm_name}' not found."

        realm = self.world_engine.realms[realm_name]
        entities = realm.entities
        
        # Aggregate stats
        types = {}
        extensions = {}
        total_size = 0
        
        for e in entities:
            etype = e.get("type", "Unknown")
            types[etype] = types.get(etype, 0) + 1
            
            props = e.get("properties", {})
            if "size" in props:
                total_size += props["size"]
            if "extension" in props:
                ext = props["extension"]
                extensions[ext] = extensions.get(ext, 0) + 1

        # Generate Report
        report = [
            f"--- Analysis Report: {realm_name} ---",
            f"Description: {realm.description}",
            f"Total Entities: {len(entities)}",
            f"Entity Types: {types}",
            f"Code Composition: {extensions}",
            f"Total Mass (Size): {total_size} bytes",
            "-----------------------------------"
        ]
        
        return "\n".join(report)
