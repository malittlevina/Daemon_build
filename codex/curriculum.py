import json
import os
from typing import Dict, List, Optional

class KnowledgePack:
    def __init__(self, name: str, domain: str, version: str = "1.0"):
        self.name = name
        self.domain = domain
        self.version = version
        self.topics: Dict[str, Dict[str, str]] = {} # topic_key -> {title, content, tags}

    def add_topic(self, key: str, title: str, content: str, tags: List[str] = None):
        self.topics[key] = {
            "title": title,
            "content": content,
            "tags": tags or []
        }

    def get_content(self, key: str) -> Optional[str]:
        return self.topics.get(key, {}).get("content")

    def search(self, query: str) -> List[Dict]:
        results = []
        q = query.lower()
        for key, data in self.topics.items():
            if q in key.lower() or q in data["title"].lower() or q in data["content"].lower():
                results.append(data)
        return results

    def to_dict(self):
        return {
            "meta": {"name": self.name, "domain": self.domain, "version": self.version},
            "topics": self.topics
        }

    @classmethod
    def from_dict(cls, data):
        meta = data.get("meta", {})
        pack = cls(meta.get("name", "Unknown"), meta.get("domain", "General"), meta.get("version", "1.0"))
        pack.topics = data.get("topics", {})
        return pack

class CurriculumManager:
    def __init__(self, storage_dir="codex/curriculums"):
        self.storage_dir = storage_dir
        self.packs: Dict[str, KnowledgePack] = {}
        self.load_all()

    def create_pack(self, name: str, domain: str) -> KnowledgePack:
        pack = KnowledgePack(name, domain)
        self.packs[name] = pack
        return pack

    def save_pack(self, pack_name: str):
        if pack_name not in self.packs: return
        pack = self.packs[pack_name]
        
        os.makedirs(self.storage_dir, exist_ok=True)
        filename = f"{pack_name.lower().replace(' ', '_')}.json"
        with open(os.path.join(self.storage_dir, filename), "w") as f:
            json.dump(pack.to_dict(), f, indent=2)
        print(f"[Curriculum] Saved pack: {pack_name}")

    def load_all(self):
        if not os.path.exists(self.storage_dir): return
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.storage_dir, filename), "r") as f:
                        data = json.load(f)
                        pack = KnowledgePack.from_dict(data)
                        self.packs[pack.name] = pack
                        print(f"[Curriculum] Loaded pack: {pack.name} ({pack.domain})")
                except Exception as e:
                    print(f"[Curriculum] Failed to load {filename}: {e}")

    def query(self, query_text: str, domain_filter: str = None) -> List[Dict]:
        """
        Searches across all (or specific) knowledge packs.
        """
        results = []
        for pack in self.packs.values():
            if domain_filter and pack.domain.lower() != domain_filter.lower():
                continue
            
            # Simple search
            matches = pack.search(query_text)
            for m in matches:
                # Add source metadata
                m["source_pack"] = pack.name
                results.append(m)
        return results
