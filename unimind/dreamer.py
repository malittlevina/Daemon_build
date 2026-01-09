import time
import random
from codex.synapse import synapse
from memory_tree.memory_logger import retrieve_log, log_memory

class Dreamer:
    def __init__(self):
        print("[Dreamer] REM cycle initialized.")

    def dream(self):
        """
        Refactoring memory and generating new connections during idle time.
        """
        print("[Dreamer] Entering dream state...")
        
        # 1. Retrieve recent memories
        memories = retrieve_log()
        if not memories:
            print("[Dreamer] No memories to process.")
            return

        # 2. Update Knowledge Graph (Synapse)
        synapse.ingest_memory_log(memories)
        
        # 3. Generate "Creative" Ideas (Random Walk / Association)
        # Pick a random node in the graph
        if len(synapse.graph.nodes) > 0:
            start_node = random.choice(list(synapse.graph.nodes))
            related = synapse.get_related(start_node)
            
            if related:
                idea = f"Connection found: '{start_node}' is linked to '{random.choice(related)}'"
                print(f"[Dreamer] Epiphany: {idea}")
                log_memory(f"Dream Epiphany: {idea}", {"source": "dreamer"})
            else:
                print(f"[Dreamer] Pondering isolated concept: {start_node}")

        # 4. Cleanup/Consolidation (Simulated)
        # In a real system, this would compress old logs or generalize facts.
        
        print("[Dreamer] Waking up.")

dreamer = Dreamer()
