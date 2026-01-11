# nlu/entity_linking.py
# Named Entity Linking Module

"""
Named Entity Linking Module

Links extracted entities to knowledge base entries:
- Entity disambiguation
- Knowledge base lookup
- Entity relationship extraction
- Fact extraction
"""

from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum


class EntityCategory(Enum):
    """Entity categories for knowledge base."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    EVENT = "event"
    PRODUCT = "product"
    CONCEPT = "concept"
    DATE = "date"
    NUMBER = "number"
    TECHNOLOGY = "technology"
    LANGUAGE = "language"


@dataclass
class KnowledgeEntry:
    """Entry in the knowledge base."""
    id: str
    name: str
    category: EntityCategory
    aliases: List[str] = field(default_factory=list)
    description: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    related: List[str] = field(default_factory=list)


@dataclass
class LinkedEntity:
    """Entity linked to knowledge base."""
    text: str
    kb_entry: Optional[KnowledgeEntry]
    confidence: float
    start: int
    end: int
    alternatives: List[KnowledgeEntry] = field(default_factory=list)


class KnowledgeBase:
    """
    Simple knowledge base for entity linking.
    
    Contains entries for common entities that the system knows about.
    """
    
    def __init__(self):
        self.entries: Dict[str, KnowledgeEntry] = {}
        self.alias_map: Dict[str, str] = {}  # alias -> entry_id
        
        # Load built-in knowledge
        self._load_builtin_knowledge()
        
    def _load_builtin_knowledge(self):
        """Load built-in knowledge entries."""
        # Programming languages
        self._add_entry(KnowledgeEntry(
            id="python", name="Python", category=EntityCategory.TECHNOLOGY,
            aliases=["python3", "py"],
            description="High-level programming language",
            properties={"type": "programming_language", "paradigm": ["object-oriented", "functional"], "year": 1991}
        ))
        self._add_entry(KnowledgeEntry(
            id="javascript", name="JavaScript", category=EntityCategory.TECHNOLOGY,
            aliases=["js", "ecmascript", "node.js", "nodejs"],
            description="Web scripting language",
            properties={"type": "programming_language", "paradigm": ["functional", "event-driven"], "year": 1995}
        ))
        self._add_entry(KnowledgeEntry(
            id="java", name="Java", category=EntityCategory.TECHNOLOGY,
            aliases=["jdk", "jvm"],
            description="Object-oriented programming language",
            properties={"type": "programming_language", "paradigm": ["object-oriented"], "year": 1995}
        ))
        self._add_entry(KnowledgeEntry(
            id="cpp", name="C++", category=EntityCategory.TECHNOLOGY,
            aliases=["c plus plus", "cplusplus"],
            description="Systems programming language",
            properties={"type": "programming_language", "paradigm": ["object-oriented", "procedural"], "year": 1983}
        ))
        self._add_entry(KnowledgeEntry(
            id="rust", name="Rust", category=EntityCategory.TECHNOLOGY,
            aliases=["rustlang"],
            description="Systems programming language focused on safety",
            properties={"type": "programming_language", "paradigm": ["functional", "concurrent"], "year": 2010}
        ))
        
        # AI/ML terms
        self._add_entry(KnowledgeEntry(
            id="ai", name="Artificial Intelligence", category=EntityCategory.CONCEPT,
            aliases=["ai", "artificial intelligence", "machine intelligence"],
            description="Intelligence demonstrated by machines",
            properties={"field": "computer_science"}
        ))
        self._add_entry(KnowledgeEntry(
            id="ml", name="Machine Learning", category=EntityCategory.CONCEPT,
            aliases=["ml", "machine learning"],
            description="Study of algorithms that improve through experience",
            properties={"field": "artificial_intelligence", "parent": "ai"}
        ))
        self._add_entry(KnowledgeEntry(
            id="deep_learning", name="Deep Learning", category=EntityCategory.CONCEPT,
            aliases=["deep learning", "dl", "neural networks"],
            description="Machine learning based on artificial neural networks",
            properties={"field": "machine_learning", "parent": "ml"}
        ))
        self._add_entry(KnowledgeEntry(
            id="nlp", name="Natural Language Processing", category=EntityCategory.CONCEPT,
            aliases=["nlp", "natural language processing", "computational linguistics"],
            description="AI focused on human language understanding",
            properties={"field": "artificial_intelligence", "parent": "ai"}
        ))
        self._add_entry(KnowledgeEntry(
            id="llm", name="Large Language Model", category=EntityCategory.CONCEPT,
            aliases=["llm", "large language model", "language model"],
            description="Neural network trained on large text corpus",
            properties={"field": "natural_language_processing", "parent": "nlp"}
        ))
        
        # Companies
        self._add_entry(KnowledgeEntry(
            id="google", name="Google", category=EntityCategory.ORGANIZATION,
            aliases=["alphabet", "google inc", "google llc"],
            description="Technology company",
            properties={"industry": "technology", "founded": 1998, "type": "company"}
        ))
        self._add_entry(KnowledgeEntry(
            id="apple", name="Apple", category=EntityCategory.ORGANIZATION,
            aliases=["apple inc", "apple computer"],
            description="Technology company",
            properties={"industry": "technology", "founded": 1976, "type": "company"}
        ))
        self._add_entry(KnowledgeEntry(
            id="microsoft", name="Microsoft", category=EntityCategory.ORGANIZATION,
            aliases=["microsoft corporation", "msft"],
            description="Technology company",
            properties={"industry": "technology", "founded": 1975, "type": "company"}
        ))
        self._add_entry(KnowledgeEntry(
            id="amazon", name="Amazon", category=EntityCategory.ORGANIZATION,
            aliases=["amazon.com", "aws", "amazon web services"],
            description="E-commerce and cloud computing company",
            properties={"industry": "technology", "founded": 1994, "type": "company"}
        ))
        self._add_entry(KnowledgeEntry(
            id="openai", name="OpenAI", category=EntityCategory.ORGANIZATION,
            aliases=["open ai"],
            description="AI research laboratory",
            properties={"industry": "artificial_intelligence", "founded": 2015, "type": "research_lab"}
        ))
        self._add_entry(KnowledgeEntry(
            id="anthropic", name="Anthropic", category=EntityCategory.ORGANIZATION,
            aliases=[],
            description="AI safety company",
            properties={"industry": "artificial_intelligence", "founded": 2021, "type": "company"}
        ))
        
        # Languages
        self._add_entry(KnowledgeEntry(
            id="english", name="English", category=EntityCategory.LANGUAGE,
            aliases=["en"],
            description="West Germanic language",
            properties={"family": "Germanic", "speakers": 1500000000}
        ))
        self._add_entry(KnowledgeEntry(
            id="spanish", name="Spanish", category=EntityCategory.LANGUAGE,
            aliases=["español", "castellano", "es"],
            description="Romance language",
            properties={"family": "Romance", "speakers": 500000000}
        ))
        self._add_entry(KnowledgeEntry(
            id="chinese", name="Chinese", category=EntityCategory.LANGUAGE,
            aliases=["mandarin", "中文", "zh"],
            description="Sino-Tibetan language",
            properties={"family": "Sino-Tibetan", "speakers": 1100000000}
        ))
        
        # Locations
        self._add_entry(KnowledgeEntry(
            id="usa", name="United States", category=EntityCategory.LOCATION,
            aliases=["us", "usa", "america", "united states of america"],
            description="Country in North America",
            properties={"type": "country", "continent": "North America", "capital": "Washington D.C."}
        ))
        self._add_entry(KnowledgeEntry(
            id="uk", name="United Kingdom", category=EntityCategory.LOCATION,
            aliases=["britain", "great britain", "england", "uk"],
            description="Country in Europe",
            properties={"type": "country", "continent": "Europe", "capital": "London"}
        ))
        self._add_entry(KnowledgeEntry(
            id="china", name="China", category=EntityCategory.LOCATION,
            aliases=["prc", "people's republic of china", "中国"],
            description="Country in East Asia",
            properties={"type": "country", "continent": "Asia", "capital": "Beijing"}
        ))
        
        # Products/Technologies
        self._add_entry(KnowledgeEntry(
            id="chatgpt", name="ChatGPT", category=EntityCategory.PRODUCT,
            aliases=["chat gpt", "gpt-4", "gpt-3.5", "gpt4", "gpt3"],
            description="AI chatbot by OpenAI",
            properties={"creator": "openai", "type": "ai_chatbot", "year": 2022}
        ))
        self._add_entry(KnowledgeEntry(
            id="claude", name="Claude", category=EntityCategory.PRODUCT,
            aliases=["claude ai", "claude-3", "claude-2"],
            description="AI assistant by Anthropic",
            properties={"creator": "anthropic", "type": "ai_assistant", "year": 2023}
        ))
        self._add_entry(KnowledgeEntry(
            id="tensorflow", name="TensorFlow", category=EntityCategory.TECHNOLOGY,
            aliases=["tf"],
            description="Machine learning framework by Google",
            properties={"type": "ml_framework", "creator": "google", "year": 2015}
        ))
        self._add_entry(KnowledgeEntry(
            id="pytorch", name="PyTorch", category=EntityCategory.TECHNOLOGY,
            aliases=["torch"],
            description="Machine learning framework",
            properties={"type": "ml_framework", "creator": "meta", "year": 2016}
        ))
        
    def _add_entry(self, entry: KnowledgeEntry):
        """Add an entry to the knowledge base."""
        self.entries[entry.id] = entry
        
        # Map name and aliases
        self.alias_map[entry.name.lower()] = entry.id
        for alias in entry.aliases:
            self.alias_map[alias.lower()] = entry.id
            
    def lookup(self, text: str) -> Optional[KnowledgeEntry]:
        """Look up an entity by name or alias."""
        text_lower = text.lower().strip()
        
        if text_lower in self.alias_map:
            entry_id = self.alias_map[text_lower]
            return self.entries.get(entry_id)
            
        # Partial match
        for alias, entry_id in self.alias_map.items():
            if text_lower in alias or alias in text_lower:
                return self.entries.get(entry_id)
                
        return None
        
    def search(self, query: str, n: int = 5) -> List[KnowledgeEntry]:
        """Search for entries matching query."""
        query_lower = query.lower()
        results = []
        
        for entry in self.entries.values():
            score = 0
            
            # Name match
            if query_lower in entry.name.lower():
                score += 2
            if entry.name.lower() == query_lower:
                score += 3
                
            # Alias match
            for alias in entry.aliases:
                if query_lower in alias.lower():
                    score += 1
                if alias.lower() == query_lower:
                    score += 2
                    
            # Description match
            if query_lower in entry.description.lower():
                score += 0.5
                
            if score > 0:
                results.append((score, entry))
                
        results.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in results[:n]]
        
    def get_related(self, entry_id: str) -> List[KnowledgeEntry]:
        """Get related entries."""
        entry = self.entries.get(entry_id)
        if not entry:
            return []
            
        related = []
        for rel_id in entry.related:
            if rel_id in self.entries:
                related.append(self.entries[rel_id])
                
        return related
        
    def add_entry(self, entry: KnowledgeEntry):
        """Add a new entry to the knowledge base."""
        self._add_entry(entry)
        
    def size(self) -> int:
        """Get number of entries."""
        return len(self.entries)


class EntityLinker:
    """
    Entity linking engine.
    
    Links extracted entities to knowledge base entries.
    """
    
    def __init__(self, knowledge_base: KnowledgeBase = None):
        self.kb = knowledge_base or KnowledgeBase()
        
    def link(self, text: str, entities: List[dict] = None) -> List[LinkedEntity]:
        """
        Link entities in text to knowledge base.
        
        Args:
            text: Input text
            entities: Optional list of pre-extracted entities with 'text', 'start', 'end'
            
        Returns:
            List of LinkedEntity objects
        """
        if entities is None:
            entities = self._extract_entities(text)
            
        linked = []
        for entity in entities:
            entity_text = entity.get('text', '')
            start = entity.get('start', 0)
            end = entity.get('end', len(entity_text))
            
            # Look up in knowledge base
            kb_entry = self.kb.lookup(entity_text)
            
            # Calculate confidence
            confidence = 0.9 if kb_entry else 0.0
            
            # Get alternatives
            alternatives = []
            if not kb_entry:
                alternatives = self.kb.search(entity_text, n=3)
                if alternatives:
                    kb_entry = alternatives[0]
                    confidence = 0.6
                    alternatives = alternatives[1:]
                    
            linked.append(LinkedEntity(
                text=entity_text,
                kb_entry=kb_entry,
                confidence=confidence,
                start=start,
                end=end,
                alternatives=alternatives
            ))
            
        return linked
        
    def _extract_entities(self, text: str) -> List[dict]:
        """Simple entity extraction for linking."""
        import re
        entities = []
        
        # Extract capitalized words/phrases
        pattern = r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b'
        for match in re.finditer(pattern, text):
            # Skip sentence starts
            if match.start() > 0 and text[match.start()-1] not in '.!?':
                entities.append({
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
                
        # Also try lowercase known entities
        for alias in self.kb.alias_map:
            idx = text.lower().find(alias)
            if idx >= 0:
                # Check if not already captured
                already = any(e['start'] <= idx < e['end'] for e in entities)
                if not already:
                    entities.append({
                        'text': text[idx:idx+len(alias)],
                        'start': idx,
                        'end': idx + len(alias)
                    })
                    
        return entities
        
    def enrich_text(self, text: str) -> str:
        """
        Enrich text with entity information.
        
        Args:
            text: Input text
            
        Returns:
            Text with entity annotations
        """
        linked = self.link(text)
        
        # Sort by position (descending to avoid offset issues)
        linked.sort(key=lambda x: x.start, reverse=True)
        
        result = text
        for entity in linked:
            if entity.kb_entry:
                annotation = f"[{entity.text}]({entity.kb_entry.id})"
                result = result[:entity.start] + annotation + result[entity.end:]
                
        return result
        
    def get_facts(self, text: str) -> List[Dict]:
        """
        Extract facts about entities in text.
        
        Args:
            text: Input text
            
        Returns:
            List of fact dictionaries
        """
        linked = self.link(text)
        facts = []
        
        for entity in linked:
            if entity.kb_entry:
                facts.append({
                    'entity': entity.text,
                    'name': entity.kb_entry.name,
                    'category': entity.kb_entry.category.value,
                    'description': entity.kb_entry.description,
                    'properties': entity.kb_entry.properties
                })
                
        return facts


# =============================================================================
# SINGLETON & HELPER FUNCTIONS
# =============================================================================

_kb: Optional[KnowledgeBase] = None
_linker: Optional[EntityLinker] = None


def get_knowledge_base() -> KnowledgeBase:
    """Get the global knowledge base instance."""
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb


def get_entity_linker() -> EntityLinker:
    """Get the global entity linker instance."""
    global _linker
    if _linker is None:
        _linker = EntityLinker(get_knowledge_base())
    return _linker


def link_entities(text: str) -> List[LinkedEntity]:
    """Link entities in text to knowledge base."""
    return get_entity_linker().link(text)


def lookup_entity(name: str) -> Optional[KnowledgeEntry]:
    """Look up an entity in the knowledge base."""
    return get_knowledge_base().lookup(name)


def search_knowledge_base(query: str, n: int = 5) -> List[KnowledgeEntry]:
    """Search the knowledge base."""
    return get_knowledge_base().search(query, n)


def get_entity_facts(text: str) -> List[Dict]:
    """Extract facts about entities in text."""
    return get_entity_linker().get_facts(text)
