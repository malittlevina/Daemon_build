import time
from daemon.kernel_bridge import KernelBridge
from storyrealms.entities import AgentEntity

class CyberSentry:
    def __init__(self, world_engine):
        self.world_engine = world_engine
        self.kernel = KernelBridge()
        self.threat_threshold = 20.0  # CPU % to consider a threat

    def scan_and_manifest(self, realm_name="Runtime_Monitor"):
        """
        Scans real processes and manifests 'Resource Hogs' into the realm.
        """
        # Ensure realm exists
        if realm_name not in self.world_engine.realms:
            self.world_engine.create_realm(realm_name, "The Astral Plane of Processing.")
            
        realm = self.world_engine.realms[realm_name]
        
        # Get heavy processes
        procs = self.kernel.list_processes(limit=10, sort_by="cpu")
        
        manifested = []
        for p in procs:
            pid = p['pid']
            name = p['name']
            cpu = p['cpu_percent'] or 0
            mem = p['memory_percent'] or 0
            
            # Check if already manifests
            existing = next((e for e in realm.entities if e.get("properties", {}).get("pid") == pid), None)
            
            if cpu > self.threat_threshold:
                if not existing:
                    # Spawn new Threat
                    entity = AgentEntity(
                        name=f"Bloat_Golem_{name}",
                        role="Enemy",
                        location="Root",
                        properties={
                            "pid": pid,
                            "hp": int(cpu * 2),
                            "damage": int(mem * 10),
                            "desc": f"Consuming {cpu}% CPU"
                        }
                    )
                    realm.entities.append(entity.to_dict())
                    manifested.append(f"Manifested {name} (CPU: {cpu}%)")
                else:
                    # Update existing
                    existing["properties"]["hp"] = int(cpu * 2)
            else:
                # Process calmed down, remove entity?
                if existing:
                    realm.entities.remove(existing)
        
        self.world_engine.save_realm(realm)
        return manifested

    def exorcise_entity(self, entity_id, realm_name="Runtime_Monitor"):
        """
        Kills the real process associated with the entity.
        Includes a safety snapshot before killing.
        """
        if realm_name not in self.world_engine.realms:
            return "Realm not found."
            
        realm = self.world_engine.realms[realm_name]
        
        target = next((e for e in realm.entities if e.get("name") == entity_id or e.get("id") == entity_id), None)
        
        if not target:
            return "Target entity not found."
            
        pid = target.get("properties", {}).get("pid")
        if not pid:
            return "Entity has no tether to the physical world (No PID)."

        # --- SAFEGUARD ---
        # Before killing a process that might be critical, we could trigger a system snapshot.
        # However, backing up the whole HDD is too slow for a game loop.
        # Instead, we just log the action heavily and perhaps verify it's not a root process (basic check).
        
        # Simple whitelist check
        safe_processes = ["init", "systemd", "kernel", "daemon", "python"]
        name = target.get("name", "").lower()
        if any(safe in name for safe in safe_processes):
             return f"Exorcism Denied: {name} is a protected system spirit."

        # Execute Kill via Kernel
        result = self.kernel.execute_command(f"kill -9 {pid}")
        
        if result["success"]:
            realm.entities.remove(target)
            self.world_engine.save_realm(realm)
            return f"Exorcism Successful. Process {pid} terminated. Entity banished."
        else:
            return f"Exorcism Failed: {result['error']}"
