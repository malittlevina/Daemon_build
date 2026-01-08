import threading
import time
import random
from codex.knowledge_graph import KnowledgeGraph

class Dreamer:
    def __init__(self):
        self.graph = KnowledgeGraph()
        self.active = False

    def start_dreaming(self):
        self.active = True
        threading.Thread(target=self._dream_loop, daemon=True, name="Dreamer").start()
        print("[Dreamer] Background consolidation started.")

    def _dream_loop(self):
        while self.active:
            time.sleep(60) # Dream every minute
            
            # 1. Load Graph
            if not self.graph.nodes:
                continue
                
            # 2. Pick a random concept
            concepts = list(self.graph.nodes.keys())
            if len(concepts) < 2:
                continue
                
            c1 = random.choice(concepts)
            c2 = random.choice(concepts)
            
            # 3. Try to find path
            path = self.graph.find_path(c1, c2)
            
            if path:
                # Reinforce? (Already connected)
                pass
            else:
                # GAP DETECTED
                print(f"[Dreamer] 💭 Knowledge Gap: How does '{c1}' relate to '{c2}'?")
                # In a full system, this would generate a "Curiosity Drive" boost
                # asking the user to explain the connection.
