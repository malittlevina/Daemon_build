# language/semantics.py
"""
Semantic Analysis
=================
Extracts meaning and understanding from language:
- Concept extraction and mapping
- Semantic relationships
- Intent and sentiment analysis
- Context understanding
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from collections import defaultdict

from .vocabulary import Vocabulary, Word, WordRelation


@dataclass
class Concept:
    """A semantic concept extracted from text."""
    name: str
    type: str  # entity, action, property, relation, etc.
    mentions: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    confidence: float = 1.0
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, Concept):
            return self.name == other.name
        return False


class ConceptGraph:
    """
    A graph of semantic concepts and their relationships.
    Used for understanding meaning and context.
    """
    
    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.relations: Dict[Tuple[str, str], str] = {}  # (concept1, concept2) -> relation_type
    
    def add_concept(self, concept: Concept):
        """Add or update a concept."""
        if concept.name in self.concepts:
            existing = self.concepts[concept.name]
            existing.mentions.extend(concept.mentions)
            existing.related_concepts.extend(concept.related_concepts)
        else:
            self.concepts[concept.name] = concept
    
    def add_relation(self, concept1: str, concept2: str, relation: str):
        """Add a relationship between concepts."""
        self.relations[(concept1, concept2)] = relation
    
    def get_related(self, concept_name: str) -> List[Tuple[str, str]]:
        """Get concepts related to a given concept."""
        related = []
        for (c1, c2), rel in self.relations.items():
            if c1 == concept_name:
                related.append((c2, rel))
            elif c2 == concept_name:
                related.append((c1, rel))
        return related
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'concepts': {k: {
                'name': v.name,
                'type': v.type,
                'mentions': v.mentions,
                'related': v.related_concepts
            } for k, v in self.concepts.items()},
            'relations': {f"{k[0]}->{k[1]}": v for k, v in self.relations.items()}
        }


class SemanticAnalyzer:
    """
    Analyzes text for semantic meaning.
    Integrates with vocabulary for deeper understanding.
    """
    
    # Semantic role patterns
    ACTION_VERBS = ['do', 'make', 'create', 'build', 'run', 'start', 'stop', 'help', 'show', 'find', 'get', 'give', 'take', 'put', 'send', 'learn', 'remember', 'forget', 'think', 'know']
    STATE_VERBS = ['is', 'are', 'was', 'were', 'be', 'become', 'seem', 'appear', 'feel', 'look', 'sound', 'taste', 'smell', 'remain', 'stay']
    MENTAL_VERBS = ['think', 'believe', 'know', 'understand', 'remember', 'forget', 'imagine', 'wonder', 'realize', 'recognize', 'feel', 'want', 'need', 'like', 'love', 'hate', 'prefer']
    
    # Entity patterns
    PERSON_INDICATORS = ['i', 'you', 'he', 'she', 'they', 'we', 'person', 'people', 'user', 'someone', 'anyone', 'everyone']
    TIME_INDICATORS = ['today', 'tomorrow', 'yesterday', 'now', 'later', 'soon', 'always', 'never', 'morning', 'evening', 'night', 'day', 'week', 'month', 'year']
    LOCATION_INDICATORS = ['here', 'there', 'home', 'office', 'room', 'place', 'location', 'where']
    
    def __init__(self, vocabulary: Optional[Vocabulary] = None):
        self.vocabulary = vocabulary or Vocabulary()
        self.concept_cache: Dict[str, ConceptGraph] = {}
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Perform semantic analysis on text.
        Returns concepts, intent, sentiment, and semantic roles.
        """
        text_lower = text.lower()
        
        # Extract concepts
        concepts = self._extract_concepts(text_lower)
        
        # Build concept graph
        graph = self._build_concept_graph(concepts)
        
        # Determine intent
        intent = self._determine_intent(text_lower)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(text_lower)
        
        # Extract semantic roles
        roles = self._extract_semantic_roles(text_lower)
        
        # Get topics
        topics = self._extract_topics(text_lower)
        
        return {
            'text': text,
            'concepts': [{'name': c.name, 'type': c.type, 'confidence': c.confidence} for c in concepts],
            'concept_graph': graph.to_dict(),
            'intent': intent,
            'sentiment': sentiment,
            'semantic_roles': roles,
            'topics': topics
        }
    
    def _extract_concepts(self, text: str) -> List[Concept]:
        """Extract semantic concepts from text."""
        concepts = []
        words = text.split()
        
        for word in words:
            clean_word = ''.join(c for c in word if c.isalnum())
            if not clean_word or len(clean_word) < 2:
                continue
            
            # Check for known concept types
            if clean_word in self.PERSON_INDICATORS:
                concepts.append(Concept(name=clean_word, type='person', mentions=[clean_word]))
            elif clean_word in self.TIME_INDICATORS:
                concepts.append(Concept(name=clean_word, type='time', mentions=[clean_word]))
            elif clean_word in self.LOCATION_INDICATORS:
                concepts.append(Concept(name=clean_word, type='location', mentions=[clean_word]))
            elif clean_word in self.ACTION_VERBS:
                concepts.append(Concept(name=clean_word, type='action', mentions=[clean_word]))
            elif clean_word in self.MENTAL_VERBS:
                concepts.append(Concept(name=clean_word, type='mental_process', mentions=[clean_word]))
            else:
                # Check vocabulary for known words
                vocab_word = self.vocabulary.get(clean_word)
                if vocab_word:
                    concepts.append(Concept(
                        name=clean_word,
                        type=vocab_word.primary_pos.value,
                        mentions=[clean_word],
                        confidence=0.8
                    ))
        
        return concepts
    
    def _build_concept_graph(self, concepts: List[Concept]) -> ConceptGraph:
        """Build a graph of concept relationships."""
        graph = ConceptGraph()
        
        for concept in concepts:
            graph.add_concept(concept)
        
        # Find relationships based on proximity and vocabulary knowledge
        for i, c1 in enumerate(concepts):
            for c2 in concepts[i+1:]:
                # Check if vocabulary knows about relationship
                w1 = self.vocabulary.get(c1.name)
                if w1:
                    if c2.name in w1.synonyms():
                        graph.add_relation(c1.name, c2.name, 'synonym')
                    elif c2.name in w1.antonyms():
                        graph.add_relation(c1.name, c2.name, 'antonym')
                    elif c2.name in w1.get_related(WordRelation.RELATED):
                        graph.add_relation(c1.name, c2.name, 'related')
        
        return graph
    
    def _determine_intent(self, text: str) -> Dict[str, Any]:
        """Determine the semantic intent of the text."""
        intent = {
            'primary': 'statement',
            'confidence': 0.5,
            'sub_intents': []
        }
        
        # Question intent
        if '?' in text or any(text.startswith(q) for q in ['what', 'who', 'where', 'when', 'why', 'how', 'can', 'could', 'would', 'should', 'is', 'are', 'do', 'does']):
            intent['primary'] = 'question'
            intent['confidence'] = 0.9
            
            if 'how' in text:
                intent['sub_intents'].append('how_to')
            if 'what' in text:
                intent['sub_intents'].append('definition')
            if 'why' in text:
                intent['sub_intents'].append('explanation')
        
        # Command intent
        elif any(text.startswith(c) for c in ['please', 'do', 'make', 'create', 'show', 'tell', 'help', 'find', 'get', 'run', 'start', 'stop']):
            intent['primary'] = 'command'
            intent['confidence'] = 0.85
        
        # Request intent
        elif any(p in text for p in ['can you', 'could you', 'would you', 'please']):
            intent['primary'] = 'request'
            intent['confidence'] = 0.8
        
        # Information sharing
        elif any(p in text for p in ['i think', 'i believe', 'i know', 'did you know', 'in fact']):
            intent['primary'] = 'information'
            intent['confidence'] = 0.7
        
        # Learning intent
        if any(w in text for w in ['learn', 'study', 'understand', 'teach', 'explain']):
            intent['sub_intents'].append('learning')
        
        # Memory intent
        if any(w in text for w in ['remember', 'recall', 'forget', 'memorize']):
            intent['sub_intents'].append('memory')
        
        return intent
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment/emotion in text."""
        positive_words = ['good', 'great', 'excellent', 'wonderful', 'amazing', 'love', 'like', 'happy', 'glad', 'pleased', 'thank', 'thanks', 'appreciate', 'helpful', 'nice', 'best', 'perfect', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'sad', 'angry', 'frustrated', 'annoyed', 'disappointed', 'worst', 'wrong', 'error', 'fail', 'problem']
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count:
            polarity = 'positive'
            score = min(1.0, pos_count * 0.2)
        elif neg_count > pos_count:
            polarity = 'negative'
            score = max(-1.0, -neg_count * 0.2)
        else:
            polarity = 'neutral'
            score = 0.0
        
        return {
            'polarity': polarity,
            'score': score,
            'positive_count': pos_count,
            'negative_count': neg_count
        }
    
    def _extract_semantic_roles(self, text: str) -> Dict[str, List[str]]:
        """Extract semantic roles (agent, patient, instrument, etc.)."""
        roles = {
            'agent': [],      # Who/what performs the action
            'patient': [],    # Who/what is affected
            'instrument': [], # With what
            'location': [],   # Where
            'time': [],       # When
            'manner': [],     # How
            'purpose': [],    # Why/for what
        }
        
        words = text.split()
        
        # Simple role extraction
        for i, word in enumerate(words):
            clean = ''.join(c for c in word if c.isalnum()).lower()
            
            if clean in self.PERSON_INDICATORS:
                roles['agent'].append(clean)
            elif clean in self.TIME_INDICATORS:
                roles['time'].append(clean)
            elif clean in self.LOCATION_INDICATORS:
                roles['location'].append(clean)
            
            # Check for purpose markers
            if clean in ['to', 'for'] and i + 1 < len(words):
                next_word = ''.join(c for c in words[i + 1] if c.isalnum())
                roles['purpose'].append(next_word)
            
            # Check for manner markers
            if clean.endswith('ly'):
                roles['manner'].append(clean)
        
        return {k: v for k, v in roles.items() if v}
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text."""
        topics = []
        
        # Use vocabulary to find important nouns
        words = text.split()
        for word in words:
            clean = ''.join(c for c in word if c.isalnum()).lower()
            vocab_word = self.vocabulary.get(clean)
            
            if vocab_word:
                from .vocabulary import PartOfSpeech
                if vocab_word.primary_pos == PartOfSpeech.NOUN:
                    if vocab_word.importance > 0.5:
                        topics.append(clean)
        
        return list(set(topics))[:5]
    
    def understand(self, text: str) -> str:
        """Get a natural language understanding summary."""
        analysis = self.analyze(text)
        
        lines = [f"Understanding: \"{text}\"", ""]
        
        # Intent
        intent = analysis['intent']
        lines.append(f"Intent: {intent['primary']} (confidence: {intent['confidence']:.0%})")
        if intent['sub_intents']:
            lines.append(f"  Sub-intents: {', '.join(intent['sub_intents'])}")
        
        # Sentiment
        sentiment = analysis['sentiment']
        lines.append(f"Sentiment: {sentiment['polarity']} (score: {sentiment['score']:.2f})")
        
        # Concepts
        if analysis['concepts']:
            lines.append(f"Key concepts: {', '.join(c['name'] for c in analysis['concepts'][:5])}")
        
        # Topics
        if analysis['topics']:
            lines.append(f"Topics: {', '.join(analysis['topics'])}")
        
        # Semantic roles
        if analysis['semantic_roles']:
            lines.append("Semantic roles:")
            for role, values in analysis['semantic_roles'].items():
                lines.append(f"  {role}: {', '.join(values)}")
        
        return "\n".join(lines)
