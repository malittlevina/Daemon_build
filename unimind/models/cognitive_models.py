# unimind/models/cognitive_models.py
# Specialized Cognitive Models for Different Brain Functions

from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import re
import json
import math


class CognitiveCapability(Enum):
    """Cognitive capabilities for specialized models."""
    # Language capabilities
    LANGUAGE_UNDERSTANDING = "language_understanding"
    LANGUAGE_GENERATION = "language_generation"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    PRAGMATIC_REASONING = "pragmatic_reasoning"
    
    # Reasoning capabilities
    LOGICAL_REASONING = "logical_reasoning"
    CAUSAL_REASONING = "causal_reasoning"
    ANALOGICAL_REASONING = "analogical_reasoning"
    PROBABILISTIC_REASONING = "probabilistic_reasoning"
    
    # Creative capabilities
    CREATIVE_GENERATION = "creative_generation"
    CONCEPTUAL_BLENDING = "conceptual_blending"
    NARRATIVE_CONSTRUCTION = "narrative_construction"
    IDEATION = "ideation"
    
    # Memory capabilities
    EPISODIC_MEMORY = "episodic_memory"
    SEMANTIC_MEMORY = "semantic_memory"
    WORKING_MEMORY = "working_memory"
    PROCEDURAL_MEMORY = "procedural_memory"
    
    # Emotional capabilities
    EMOTION_RECOGNITION = "emotion_recognition"
    EMPATHY = "empathy"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    EMOTIONAL_GENERATION = "emotional_generation"
    
    # Executive capabilities
    PLANNING = "planning"
    DECISION_MAKING = "decision_making"
    GOAL_MANAGEMENT = "goal_management"
    ATTENTION_CONTROL = "attention_control"


@dataclass
class ModelOutput:
    """Standard output from cognitive models."""
    content: Any
    confidence: float = 0.0
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "processing_time_ms": self.processing_time_ms
        }


class BaseCognitiveModel(ABC):
    """Base class for all cognitive models."""
    
    def __init__(self, name: str, capabilities: List[CognitiveCapability]):
        self.name = name
        self.capabilities = capabilities
        self.call_count = 0
        self.total_processing_time = 0.0
        self.llm_backend = None
        
    def set_llm_backend(self, llm):
        """Set the LLM backend for enhanced processing."""
        self.llm_backend = llm
        
    @abstractmethod
    def process(self, input_data: Any, **kwargs) -> ModelOutput:
        """Process input and return output."""
        pass
        
    def has_capability(self, capability: CognitiveCapability) -> bool:
        """Check if model has a capability."""
        return capability in self.capabilities
        
    def get_stats(self) -> Dict:
        return {
            "name": self.name,
            "capabilities": [c.value for c in self.capabilities],
            "call_count": self.call_count,
            "avg_processing_time": self.total_processing_time / max(1, self.call_count)
        }


# =============================================================================
# Natural Language Understanding Model
# =============================================================================

@dataclass
class IntentResult:
    """Result of intent classification."""
    intent: str
    confidence: float
    slots: Dict[str, str] = field(default_factory=dict)
    alternatives: List[Tuple[str, float]] = field(default_factory=list)


@dataclass
class EntityResult:
    """Result of entity extraction."""
    text: str
    entity_type: str
    start: int
    end: int
    confidence: float


class NLUModel(BaseCognitiveModel):
    """
    Natural Language Understanding Model.
    
    Capabilities:
    - Intent classification
    - Entity extraction
    - Semantic parsing
    - Coreference resolution
    - Discourse analysis
    """
    
    def __init__(self):
        super().__init__(
            "NLUModel",
            [
                CognitiveCapability.LANGUAGE_UNDERSTANDING,
                CognitiveCapability.SEMANTIC_ANALYSIS
            ]
        )
        
        # Intent patterns
        self.intent_patterns = {
            "greeting": ["hello", "hi", "hey", "good morning", "good afternoon"],
            "question": ["what", "how", "why", "when", "where", "who", "which", "?"],
            "request": ["please", "could you", "can you", "would you", "help me"],
            "command": ["do", "make", "create", "start", "stop", "run", "execute"],
            "affirmation": ["yes", "yeah", "sure", "okay", "ok", "correct", "right"],
            "negation": ["no", "nope", "not", "don't", "cancel", "stop"],
            "gratitude": ["thank", "thanks", "appreciate"],
            "farewell": ["bye", "goodbye", "see you", "later"],
            "emotion_expression": ["feel", "feeling", "happy", "sad", "angry", "excited"],
            "information": ["tell me", "explain", "describe", "what is", "define"],
        }
        
        # Entity patterns
        self.entity_patterns = {
            "DATE": r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|today|tomorrow|yesterday)\b",
            "TIME": r"\b(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[ap]m)?|noon|midnight)\b",
            "NUMBER": r"\b(\d+(?:\.\d+)?)\b",
            "EMAIL": r"\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b",
            "URL": r"\b(https?://\S+|www\.\S+)\b",
            "PERCENTAGE": r"\b(\d+(?:\.\d+)?%)\b",
        }
        
    def process(self, input_data: Any, **kwargs) -> ModelOutput:
        """Process text for NLU."""
        import time
        start = time.time()
        
        text = str(input_data)
        
        # Classify intent
        intent = self.classify_intent(text)
        
        # Extract entities
        entities = self.extract_entities(text)
        
        # Semantic analysis
        semantics = self.analyze_semantics(text)
        
        result = {
            "intent": intent.intent,
            "intent_confidence": intent.confidence,
            "slots": intent.slots,
            "entities": [{"text": e.text, "type": e.entity_type} for e in entities],
            "semantics": semantics
        }
        
        processing_time = (time.time() - start) * 1000
        self.call_count += 1
        self.total_processing_time += processing_time
        
        return ModelOutput(
            content=result,
            confidence=intent.confidence,
            reasoning=f"Detected intent '{intent.intent}' with {len(entities)} entities",
            processing_time_ms=processing_time
        )
        
    def classify_intent(self, text: str) -> IntentResult:
        """Classify the intent of the text."""
        text_lower = text.lower()
        scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = sum(1 for p in patterns if p in text_lower)
            if score > 0:
                scores[intent] = score / len(patterns)
                
        if not scores:
            return IntentResult(intent="unknown", confidence=0.3)
            
        best_intent = max(scores.keys(), key=lambda k: scores[k])
        confidence = min(0.95, scores[best_intent] * 2)
        
        alternatives = sorted(
            [(i, s) for i, s in scores.items() if i != best_intent],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return IntentResult(
            intent=best_intent,
            confidence=confidence,
            alternatives=alternatives
        )
        
    def extract_entities(self, text: str) -> List[EntityResult]:
        """Extract named entities from text."""
        entities = []
        
        for entity_type, pattern in self.entity_patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(EntityResult(
                    text=match.group(),
                    entity_type=entity_type,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.85
                ))
                
        return entities
        
    def analyze_semantics(self, text: str) -> Dict:
        """Analyze semantic structure."""
        words = text.split()
        
        return {
            "word_count": len(words),
            "avg_word_length": sum(len(w) for w in words) / max(1, len(words)),
            "complexity": "simple" if len(words) < 10 else "medium" if len(words) < 25 else "complex",
            "question_type": self._detect_question_type(text),
            "formality": self._detect_formality(text)
        }
        
    def _detect_question_type(self, text: str) -> str:
        text_lower = text.lower()
        if "what" in text_lower:
            return "definition"
        elif "how" in text_lower:
            return "process"
        elif "why" in text_lower:
            return "explanation"
        elif "when" in text_lower:
            return "temporal"
        elif "where" in text_lower:
            return "location"
        elif "who" in text_lower:
            return "person"
        return "none"
        
    def _detect_formality(self, text: str) -> str:
        formal_markers = ["please", "would you", "could you", "kindly", "sir", "madam"]
        informal_markers = ["hey", "yo", "gonna", "wanna", "stuff", "lol"]
        
        formal_count = sum(1 for m in formal_markers if m in text.lower())
        informal_count = sum(1 for m in informal_markers if m in text.lower())
        
        if formal_count > informal_count:
            return "formal"
        elif informal_count > formal_count:
            return "informal"
        return "neutral"


# =============================================================================
# Reasoning Model
# =============================================================================

class ReasoningType(Enum):
    """Types of reasoning."""
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"
    CAUSAL = "causal"
    PROBABILISTIC = "probabilistic"


@dataclass
class ReasoningResult:
    """Result of a reasoning operation."""
    conclusion: str
    reasoning_type: ReasoningType
    premises: List[str]
    confidence: float
    steps: List[str]


class ReasoningModel(BaseCognitiveModel):
    """
    Logical Reasoning Model.
    
    Capabilities:
    - Deductive reasoning
    - Inductive reasoning
    - Causal inference
    - Analogical reasoning
    - Probability estimation
    """
    
    def __init__(self):
        super().__init__(
            "ReasoningModel",
            [
                CognitiveCapability.LOGICAL_REASONING,
                CognitiveCapability.CAUSAL_REASONING,
                CognitiveCapability.ANALOGICAL_REASONING,
                CognitiveCapability.PROBABILISTIC_REASONING
            ]
        )
        
        # Knowledge base for reasoning
        self.knowledge_base: Dict[str, List[str]] = {
            "is_a": [],  # X is_a Y
            "has_property": [],  # X has_property Y
            "causes": [],  # X causes Y
        }
        
    def process(self, input_data: Any, **kwargs) -> ModelOutput:
        """Process reasoning request."""
        import time
        start = time.time()
        
        reasoning_type = kwargs.get("reasoning_type", ReasoningType.DEDUCTIVE)
        premises = kwargs.get("premises", [])
        
        if isinstance(input_data, str):
            # Parse premises from text
            premises = self._parse_premises(input_data)
            
        result = self.reason(premises, reasoning_type)
        
        processing_time = (time.time() - start) * 1000
        self.call_count += 1
        self.total_processing_time += processing_time
        
        return ModelOutput(
            content={
                "conclusion": result.conclusion,
                "type": result.reasoning_type.value,
                "steps": result.steps
            },
            confidence=result.confidence,
            reasoning=f"Applied {result.reasoning_type.value} reasoning",
            processing_time_ms=processing_time
        )
        
    def reason(self, premises: List[str], reasoning_type: ReasoningType) -> ReasoningResult:
        """Perform reasoning based on type."""
        if reasoning_type == ReasoningType.DEDUCTIVE:
            return self._deductive_reasoning(premises)
        elif reasoning_type == ReasoningType.INDUCTIVE:
            return self._inductive_reasoning(premises)
        elif reasoning_type == ReasoningType.CAUSAL:
            return self._causal_reasoning(premises)
        elif reasoning_type == ReasoningType.ANALOGICAL:
            return self._analogical_reasoning(premises)
        else:
            return self._deductive_reasoning(premises)
            
    def _deductive_reasoning(self, premises: List[str]) -> ReasoningResult:
        """Apply deductive reasoning (general to specific)."""
        steps = []
        conclusion = ""
        confidence = 0.5
        
        # Simple syllogism detection
        # All X are Y, Z is X, therefore Z is Y
        
        all_statements = [p for p in premises if p.lower().startswith("all ")]
        instance_statements = [p for p in premises if " is " in p.lower() or " are " in p.lower()]
        
        steps.append(f"Analyzing {len(premises)} premises")
        
        if all_statements and instance_statements:
            steps.append(f"Found universal statement: {all_statements[0]}")
            steps.append(f"Found instance statement: {instance_statements[0]}")
            
            # Extract terms
            # Very simplified logic
            conclusion = f"Based on the premises, a logical conclusion can be drawn"
            confidence = 0.7
            steps.append(f"Applying modus ponens")
            
        if not conclusion:
            conclusion = "Insufficient premises for deductive conclusion"
            
        return ReasoningResult(
            conclusion=conclusion,
            reasoning_type=ReasoningType.DEDUCTIVE,
            premises=premises,
            confidence=confidence,
            steps=steps
        )
        
    def _inductive_reasoning(self, premises: List[str]) -> ReasoningResult:
        """Apply inductive reasoning (specific to general)."""
        steps = []
        
        steps.append(f"Examining {len(premises)} specific observations")
        
        # Look for patterns
        common_words = self._find_common_patterns(premises)
        
        if common_words:
            steps.append(f"Found common pattern: {common_words[:3]}")
            conclusion = f"Based on the pattern, it appears that {common_words[0]} is a common factor"
            confidence = 0.6
        else:
            conclusion = "No clear pattern detected in observations"
            confidence = 0.4
            
        steps.append("Generalizing from observations")
        
        return ReasoningResult(
            conclusion=conclusion,
            reasoning_type=ReasoningType.INDUCTIVE,
            premises=premises,
            confidence=confidence,
            steps=steps
        )
        
    def _causal_reasoning(self, premises: List[str]) -> ReasoningResult:
        """Apply causal reasoning."""
        steps = []
        
        # Look for causal indicators
        causal_words = ["because", "causes", "leads to", "results in", "therefore"]
        
        causal_premises = [p for p in premises if any(w in p.lower() for w in causal_words)]
        
        steps.append(f"Found {len(causal_premises)} causal statements")
        
        if causal_premises:
            steps.append(f"Analyzing causal chain")
            conclusion = f"Causal relationship identified in premises"
            confidence = 0.65
        else:
            conclusion = "No clear causal relationship detected"
            confidence = 0.4
            
        return ReasoningResult(
            conclusion=conclusion,
            reasoning_type=ReasoningType.CAUSAL,
            premises=premises,
            confidence=confidence,
            steps=steps
        )
        
    def _analogical_reasoning(self, premises: List[str]) -> ReasoningResult:
        """Apply analogical reasoning."""
        steps = []
        
        steps.append("Looking for analogical structures")
        
        # Look for "like" or "similar" comparisons
        analogy_words = ["like", "similar", "same as", "just as", "comparable"]
        
        analogies = [p for p in premises if any(w in p.lower() for w in analogy_words)]
        
        if analogies:
            steps.append(f"Found analogy: {analogies[0]}")
            conclusion = "By analogy, the same pattern may apply"
            confidence = 0.55
        else:
            conclusion = "No clear analogy detected"
            confidence = 0.4
            
        return ReasoningResult(
            conclusion=conclusion,
            reasoning_type=ReasoningType.ANALOGICAL,
            premises=premises,
            confidence=confidence,
            steps=steps
        )
        
    def _parse_premises(self, text: str) -> List[str]:
        """Parse premises from text."""
        # Split on periods, newlines, or semicolons
        parts = re.split(r'[.\n;]', text)
        return [p.strip() for p in parts if p.strip()]
        
    def _find_common_patterns(self, premises: List[str]) -> List[str]:
        """Find common words/patterns in premises."""
        word_counts: Dict[str, int] = {}
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being"}
        
        for premise in premises:
            words = premise.lower().split()
            for word in words:
                if word not in stop_words and len(word) > 2:
                    word_counts[word] = word_counts.get(word, 0) + 1
                    
        sorted_words = sorted(word_counts.keys(), key=lambda k: word_counts[k], reverse=True)
        return sorted_words
        
    def add_knowledge(self, relation: str, subject: str, obj: str):
        """Add knowledge to the reasoning base."""
        if relation in self.knowledge_base:
            self.knowledge_base[relation].append(f"{subject} {relation} {obj}")


# =============================================================================
# Creative Model
# =============================================================================

@dataclass
class CreativeOutput:
    """Output from creative generation."""
    content: str
    style: str
    originality_score: float
    coherence_score: float


class CreativeModel(BaseCognitiveModel):
    """
    Creative Generation Model.
    
    Capabilities:
    - Story generation
    - Conceptual blending
    - Metaphor creation
    - Ideation/brainstorming
    """
    
    def __init__(self):
        super().__init__(
            "CreativeModel",
            [
                CognitiveCapability.CREATIVE_GENERATION,
                CognitiveCapability.CONCEPTUAL_BLENDING,
                CognitiveCapability.NARRATIVE_CONSTRUCTION,
                CognitiveCapability.IDEATION
            ]
        )
        
        # Creative templates
        self.story_templates = [
            "Once upon a time, there was a {protagonist} who wanted to {goal}. But {obstacle} stood in the way. Through {effort}, they finally {resolution}.",
            "In a world where {setting}, a {protagonist} discovered that {discovery}. This changed everything because {consequence}.",
            "The {protagonist} had always believed {belief}. But one day, {event} happened, and they realized {realization}.",
        ]
        
        self.metaphor_patterns = [
            "{concept1} is a {concept2} that {action}",
            "Like a {concept2}, {concept1} {quality}",
            "{concept1} flows like {concept2} through {context}",
        ]
        
        # Word associations for ideation
        self.word_associations = {
            "technology": ["innovation", "digital", "future", "automation", "connectivity"],
            "nature": ["organic", "growth", "ecosystem", "harmony", "cycles"],
            "emotion": ["feeling", "expression", "connection", "depth", "journey"],
            "creativity": ["imagination", "exploration", "breakthrough", "synthesis", "vision"],
        }
        
    def process(self, input_data: Any, **kwargs) -> ModelOutput:
        """Process creative generation request."""
        import time
        start = time.time()
        
        task = kwargs.get("task", "ideate")
        
        if task == "story":
            result = self.generate_story(str(input_data), **kwargs)
        elif task == "metaphor":
            result = self.create_metaphor(str(input_data), **kwargs)
        elif task == "blend":
            concepts = kwargs.get("concepts", [])
            result = self.conceptual_blend(concepts)
        else:
            result = self.ideate(str(input_data), **kwargs)
            
        processing_time = (time.time() - start) * 1000
        self.call_count += 1
        self.total_processing_time += processing_time
        
        return ModelOutput(
            content=result.content,
            confidence=result.originality_score,
            reasoning=f"Generated {task} with style '{result.style}'",
            metadata={
                "originality": result.originality_score,
                "coherence": result.coherence_score
            },
            processing_time_ms=processing_time
        )
        
    def generate_story(self, prompt: str, **kwargs) -> CreativeOutput:
        """Generate a story based on prompt."""
        import random
        
        style = kwargs.get("style", "narrative")
        
        # Extract key elements from prompt
        words = prompt.lower().split()
        
        # Fill template
        template = random.choice(self.story_templates)
        
        # Simple slot filling
        filled = template.format(
            protagonist=self._get_protagonist(words),
            goal=self._get_goal(words),
            obstacle=self._get_obstacle(words),
            effort=self._get_effort(words),
            resolution=self._get_resolution(words),
            setting=self._get_setting(words),
            discovery=self._get_discovery(words),
            consequence=self._get_consequence(words),
            belief=self._get_belief(words),
            event=self._get_event(words),
            realization=self._get_realization(words)
        )
        
        return CreativeOutput(
            content=filled,
            style=style,
            originality_score=0.6,
            coherence_score=0.7
        )
        
    def create_metaphor(self, concept: str, **kwargs) -> CreativeOutput:
        """Create a metaphor for a concept."""
        import random
        
        # Find associations
        associations = []
        for key, values in self.word_associations.items():
            if concept.lower() in key or any(concept.lower() in v for v in values):
                associations.extend(values)
                
        if not associations:
            associations = ["a journey", "a river", "a garden", "a symphony"]
            
        target = random.choice(associations)
        template = random.choice(self.metaphor_patterns)
        
        metaphor = template.format(
            concept1=concept,
            concept2=target,
            action="unfolds with possibility",
            quality="grows and transforms",
            context="the landscape of experience"
        )
        
        return CreativeOutput(
            content=metaphor,
            style="metaphorical",
            originality_score=0.65,
            coherence_score=0.75
        )
        
    def conceptual_blend(self, concepts: List[str]) -> CreativeOutput:
        """Blend multiple concepts into a new idea."""
        if len(concepts) < 2:
            return CreativeOutput(
                content="Need at least 2 concepts to blend",
                style="error",
                originality_score=0,
                coherence_score=0
            )
            
        # Simple blending
        blend_name = "".join(c[:3].title() for c in concepts[:3])
        
        properties = []
        for concept in concepts:
            if concept.lower() in self.word_associations:
                properties.extend(self.word_associations[concept.lower()][:2])
                
        if not properties:
            properties = ["innovative", "adaptive", "harmonious"]
            
        description = f"{blend_name}: A novel concept combining {' and '.join(concepts)}. " \
                      f"It embodies {', '.join(properties[:3])}."
                      
        return CreativeOutput(
            content=description,
            style="conceptual_blend",
            originality_score=0.75,
            coherence_score=0.6
        )
        
    def ideate(self, topic: str, **kwargs) -> CreativeOutput:
        """Generate ideas for a topic."""
        num_ideas = kwargs.get("num_ideas", 5)
        
        ideas = []
        
        # Get associations
        associations = []
        for key, values in self.word_associations.items():
            associations.extend(values)
            
        import random
        random.shuffle(associations)
        
        for i in range(num_ideas):
            association = associations[i % len(associations)] if associations else "innovation"
            idea = f"Idea {i + 1}: Explore {topic} through the lens of {association}"
            ideas.append(idea)
            
        return CreativeOutput(
            content="\n".join(ideas),
            style="brainstorm",
            originality_score=0.6,
            coherence_score=0.8
        )
        
    # Helper methods for story generation
    def _get_protagonist(self, words): return "curious explorer"
    def _get_goal(self, words): return "find the truth"
    def _get_obstacle(self, words): return "great challenges"
    def _get_effort(self, words): return "determination and wisdom"
    def _get_resolution(self, words): return "achieved their dream"
    def _get_setting(self, words): return "anything was possible"
    def _get_discovery(self, words): return "hidden potential within"
    def _get_consequence(self, words): return "nothing would be the same"
    def _get_belief(self, words): return "the world was fixed"
    def _get_event(self, words): return "an unexpected encounter"
    def _get_realization(self, words): return "change was always possible"


# =============================================================================
# Emotional Intelligence Model
# =============================================================================

@dataclass
class EmotionalState:
    """Representation of emotional state."""
    primary_emotion: str
    intensity: float  # 0-1
    valence: float   # -1 to 1 (negative to positive)
    arousal: float   # 0-1 (calm to excited)
    secondary_emotions: List[Tuple[str, float]] = field(default_factory=list)


class EmotionalIntelligenceModel(BaseCognitiveModel):
    """
    Emotional Intelligence Model.
    
    Capabilities:
    - Emotion recognition from text
    - Empathetic response generation
    - Sentiment analysis
    - Emotional tone adaptation
    """
    
    def __init__(self):
        super().__init__(
            "EmotionalIntelligenceModel",
            [
                CognitiveCapability.EMOTION_RECOGNITION,
                CognitiveCapability.EMPATHY,
                CognitiveCapability.SENTIMENT_ANALYSIS,
                CognitiveCapability.EMOTIONAL_GENERATION
            ]
        )
        
        # Emotion lexicon
        self.emotion_lexicon = {
            "joy": {
                "words": ["happy", "joy", "delighted", "excited", "wonderful", "amazing", "great", "love"],
                "valence": 0.8,
                "arousal": 0.6
            },
            "sadness": {
                "words": ["sad", "unhappy", "depressed", "down", "miserable", "heartbroken", "grief"],
                "valence": -0.7,
                "arousal": 0.3
            },
            "anger": {
                "words": ["angry", "furious", "annoyed", "irritated", "mad", "outraged", "frustrated"],
                "valence": -0.6,
                "arousal": 0.8
            },
            "fear": {
                "words": ["afraid", "scared", "terrified", "anxious", "worried", "nervous", "panic"],
                "valence": -0.5,
                "arousal": 0.7
            },
            "surprise": {
                "words": ["surprised", "shocked", "amazed", "astonished", "unexpected", "wow"],
                "valence": 0.1,
                "arousal": 0.8
            },
            "trust": {
                "words": ["trust", "believe", "confident", "secure", "reliable", "faithful"],
                "valence": 0.6,
                "arousal": 0.3
            },
        }
        
        # Empathetic responses
        self.empathy_templates = {
            "joy": [
                "That's wonderful to hear! Your happiness is contagious.",
                "I'm so glad things are going well for you!",
            ],
            "sadness": [
                "I'm sorry you're feeling this way. It's okay to feel sad.",
                "That sounds really difficult. I'm here for you.",
            ],
            "anger": [
                "I understand your frustration. That situation sounds really challenging.",
                "It's completely valid to feel upset about this.",
            ],
            "fear": [
                "It's natural to feel scared. You're not alone in this.",
                "I hear your concerns. Let's think through this together.",
            ],
        }
        
    def process(self, input_data: Any, **kwargs) -> ModelOutput:
        """Process emotional analysis request."""
        import time
        start = time.time()
        
        text = str(input_data)
        
        # Recognize emotion
        emotional_state = self.recognize_emotion(text)
        
        # Generate empathetic response if requested
        response = None
        if kwargs.get("generate_response", False):
            response = self.generate_empathetic_response(emotional_state)
            
        result = {
            "primary_emotion": emotional_state.primary_emotion,
            "intensity": emotional_state.intensity,
            "valence": emotional_state.valence,
            "arousal": emotional_state.arousal,
            "secondary_emotions": emotional_state.secondary_emotions,
            "empathetic_response": response
        }
        
        processing_time = (time.time() - start) * 1000
        self.call_count += 1
        self.total_processing_time += processing_time
        
        return ModelOutput(
            content=result,
            confidence=emotional_state.intensity,
            reasoning=f"Detected {emotional_state.primary_emotion} with intensity {emotional_state.intensity:.2f}",
            processing_time_ms=processing_time
        )
        
    def recognize_emotion(self, text: str) -> EmotionalState:
        """Recognize emotions from text."""
        text_lower = text.lower()
        
        emotion_scores = {}
        
        for emotion, data in self.emotion_lexicon.items():
            score = sum(1 for word in data["words"] if word in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
                
        if not emotion_scores:
            return EmotionalState(
                primary_emotion="neutral",
                intensity=0.3,
                valence=0.0,
                arousal=0.3
            )
            
        # Get primary emotion
        primary = max(emotion_scores.keys(), key=lambda k: emotion_scores[k])
        primary_data = self.emotion_lexicon[primary]
        
        # Calculate intensity based on word count
        max_score = max(emotion_scores.values())
        intensity = min(1.0, max_score / 3)
        
        # Get secondary emotions
        secondary = [
            (e, emotion_scores[e] / max_score)
            for e in emotion_scores.keys()
            if e != primary
        ][:2]
        
        return EmotionalState(
            primary_emotion=primary,
            intensity=intensity,
            valence=primary_data["valence"],
            arousal=primary_data["arousal"],
            secondary_emotions=secondary
        )
        
    def generate_empathetic_response(self, state: EmotionalState) -> str:
        """Generate an empathetic response based on emotional state."""
        import random
        
        templates = self.empathy_templates.get(
            state.primary_emotion,
            ["I hear you. How can I help?"]
        )
        
        return random.choice(templates)
        
    def adapt_tone(self, message: str, target_emotion: str) -> str:
        """Adapt message tone to target emotion."""
        if target_emotion == "joy":
            return f"😊 {message} This is great news!"
        elif target_emotion == "sadness":
            return f"I understand. {message} Take your time."
        elif target_emotion == "anger":
            return f"I hear your frustration. {message} Let's work through this."
        elif target_emotion == "fear":
            return f"It's okay to feel uncertain. {message} We'll figure this out together."
        return message


# =============================================================================
# Model Registry
# =============================================================================

class CognitiveModelRegistry:
    """Registry for cognitive models."""
    
    def __init__(self):
        self.models: Dict[str, BaseCognitiveModel] = {}
        self._setup_default_models()
        
    def _setup_default_models(self):
        """Set up default cognitive models."""
        self.register("nlu", NLUModel())
        self.register("reasoning", ReasoningModel())
        self.register("creative", CreativeModel())
        self.register("emotional", EmotionalIntelligenceModel())
        
    def register(self, name: str, model: BaseCognitiveModel):
        """Register a model."""
        self.models[name] = model
        print(f"[CognitiveModelRegistry] Registered: {name} ({model.name})")
        
    def get(self, name: str) -> Optional[BaseCognitiveModel]:
        """Get a model by name."""
        return self.models.get(name)
        
    def get_by_capability(self, capability: CognitiveCapability) -> List[BaseCognitiveModel]:
        """Get models that have a specific capability."""
        return [m for m in self.models.values() if m.has_capability(capability)]
        
    def list_models(self) -> List[Dict]:
        """List all registered models."""
        return [
            {
                "name": name,
                "model_name": m.name,
                "capabilities": [c.value for c in m.capabilities],
                "stats": m.get_stats()
            }
            for name, m in self.models.items()
        ]
        
    def process(self, model_name: str, input_data: Any, **kwargs) -> Optional[ModelOutput]:
        """Process input with a specific model."""
        model = self.get(model_name)
        if model:
            return model.process(input_data, **kwargs)
        return None


# Convenience function
def create_cognitive_models() -> CognitiveModelRegistry:
    """Create a registry with all cognitive models."""
    return CognitiveModelRegistry()
