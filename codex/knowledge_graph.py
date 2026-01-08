import json
import os
from collections import defaultdict

class KnowledgeGraph:
    def __init__(self, storage_path="codex/graph.json"):
        self.storage_path = storage_path
        # Adjacency list: nodes[concept] = {related_concept: weight}
        self.nodes = defaultdict(dict)
        self.load()

    def add_concept(self, concept):
        concept = concept.lower().strip()
        if concept not in self.nodes:
            self.nodes[concept] = {}

    def link_concepts(self, source, target, weight=1.0):
        source = source.lower().strip()
        target = target.lower().strip()
        
        self.add_concept(source)
        self.add_concept(target)
        
        # Undirected graph for association
        self.nodes[source][target] = weight
        self.nodes[target][source] = weight
        self.save()

    def get_related(self, concept, limit=5):
        concept = concept.lower().strip()
        if concept not in self.nodes:
            return []
        
        # Sort by weight
        related = sorted(self.nodes[concept].items(), key=lambda x: x[1], reverse=True)
        return [k for k, v in related[:limit]]

    def find_path(self, start, end, max_depth=3):
        """BFS to find connection between concepts"""
        start = start.lower()
        end = end.lower()
        
        queue = [(start, [start])]
        visited = set()
        
        while queue:
            node, path = queue.pop(0)
            if node == end:
                return path
            
            if len(path) > max_depth:
                continue
                
            visited.add(node)
            for neighbor in self.nodes.get(node, {}):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
                    
        return None

    def save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump(self.nodes, f, indent=2)

    def load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                self.nodes = json.load(f)
