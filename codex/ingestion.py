import os
import json
from codex.knowledge_graph import KnowledgeGraph
from codex.nlp_utils import SimpleNLP
from codex.lexicon import Lexicon

class CodexIngestion:
    def __init__(self):
        self.knowledge_base = {}
        self.graph = KnowledgeGraph()
        self.nlp = SimpleNLP()
        self.lexicon = Lexicon()

    def ingest_file(self, path):
        content = ""
        if path.endswith(".json"):
            with open(path, "r") as f:
                data = json.load(f)
                self.knowledge_base[path] = data
                content = str(data)
                print(f"[Codex] Loaded JSON file: {path}")
        elif path.endswith(".txt") or path.endswith(".md"):
            with open(path, "r") as f:
                content = f.read()
                self.knowledge_base[path] = content
                print(f"[Codex] Loaded text file: {path}")
        else:
            print(f"[Codex] Unsupported file type: {path}")
            return

        # Auto-Graph Population
        if content:
            self._process_into_graph(content)
            self._scan_for_definitions(content)

    def _scan_for_definitions(self, text):
        # Heuristic: "X is defined as Y" or "X: Y" lines
        lines = text.split('\n')
        count = 0
        for line in lines:
            if " is defined as " in line:
                parts = line.split(" is defined as ")
                if len(parts) == 2:
                    word = parts[0].strip()
                    definition = parts[1].strip()
                    if len(word.split()) < 4: # Limit to short phrases
                        self.lexicon.define(word, definition)
                        count += 1
        
        if count > 0:
            print(f"[Codex] Extracted {count} definitions into Lexicon.")

    def _process_into_graph(self, text):
        # 1. Extract Entities
        entities = self.nlp.extract_entities(text)
        print(f"[Codex] Identified concepts: {entities[:5]}...")
        
        # 2. Add to Graph
        for e in entities:
            self.graph.add_concept(e)
            
        # 3. Link Entities (Co-occurrence)
        relations = self.nlp.extract_relations(text, entities)
        for source, target in relations:
            self.graph.link_concepts(source, target)
            
        print(f"[Codex] Graph updated with {len(relations)} links.")

    def summarize(self, path):
        if path in self.knowledge_base:
            content = self.knowledge_base[path]
            if isinstance(content, dict):
                return {k: str(v)[:50] for k, v in content.items()}
            return content[:250]
        else:
            return "[Codex] No data available for that path."

def ingest_documents(folder_path):
    ingestor = CodexIngestion()
    for file in os.listdir(folder_path):
        ingestor.ingest_file(os.path.join(folder_path, file))

def ingest_observation(content):
    """
    Simulates ingestion of external content into the Codex system.
    Logs or processes content for knowledge storage or symbolic study.
    """
    print(f"[Codex] Ingested content: {content}")
    return f"Codex acknowledged: {content}"
