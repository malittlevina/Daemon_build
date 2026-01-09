import networkx as nx
import os
import json

class Synapse:
    def __init__(self, storage_path="codex/synapse_graph.json"):
        self.storage_path = storage_path
        self.graph = nx.DiGraph()
        self.load()

    def load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
            except Exception as e:
                print(f"[Synapse] Error loading graph: {e}")
                self.graph = nx.DiGraph()

    def save(self):
        data = nx.node_link_data(self.graph)
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def connect(self, concept_a, concept_b, relation="related_to", weight=1.0):
        self.graph.add_edge(concept_a, concept_b, relation=relation, weight=weight)
        self.save()
        print(f"[Synapse] Connected '{concept_a}' --[{relation}]--> '{concept_b}'")

    def get_related(self, concept):
        if concept in self.graph:
            return list(self.graph.neighbors(concept))
        return []

    def ingest_memory_log(self, memories):
        """Builds connections from raw memory logs."""
        # Simple heuristic: Connect consecutive memories or common keywords
        previous_concept = None
        for mem in memories:
            # Extract basic concept (e.g., first noun or keyword - placeholder)
            # For now, use the 'type' or a simple hash of content
            content = mem.get("content", "")
            if not content: continue
            
            # Simplified: Use the first 3 words as a "node"
            concept = " ".join(content.split()[:3]).lower()
            
            if previous_concept:
                self.connect(previous_concept, concept, relation="sequence")
            
            previous_concept = concept

# Singleton
synapse = Synapse()
