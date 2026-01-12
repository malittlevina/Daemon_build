# unimind/models/native/brain_connector.py
# Connect Native LLM to Unimind Brain Regions

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from unimind.models.native.native_llm import NativeLLM, get_native_llm, NativeLLMConfig


@dataclass
class BrainCapability:
    """Capability provided by native LLM to brain regions."""
    name: str
    description: str
    handler: Any
    region: str


class NativeBrainConnector:
    """
    Connects Native LLM capabilities to Unimind brain regions.
    
    This allows the brain to use local AI capabilities without
    external dependencies.
    
    Connections:
    - Prefrontal Cortex: Reasoning and planning via local LLM
    - Hippocampus: Memory embeddings via local embeddings
    - Amygdala: Sentiment via local analysis
    - Wernicke's Area: Language understanding via local NLU
    - Broca's Area: Language generation via local LLM
    """
    
    def __init__(self, native_llm: NativeLLM = None):
        self.llm = native_llm or get_native_llm()
        self.connected_regions: Dict[str, Any] = {}
        self.capabilities: List[BrainCapability] = []
        self._setup_capabilities()
        
    def _setup_capabilities(self):
        """Set up native capabilities for brain regions."""
        
        # Reasoning capability for Prefrontal Cortex
        self.capabilities.append(BrainCapability(
            name="reasoning",
            description="Local chain-of-thought reasoning",
            handler=self._reason,
            region="prefrontal_cortex"
        ))
        
        # Planning capability
        self.capabilities.append(BrainCapability(
            name="planning",
            description="Multi-step plan generation",
            handler=self._plan,
            region="prefrontal_cortex"
        ))
        
        # Memory embedding for Hippocampus
        self.capabilities.append(BrainCapability(
            name="memory_embedding",
            description="Semantic memory embeddings",
            handler=self._embed_memory,
            region="hippocampus"
        ))
        
        # Memory recall
        self.capabilities.append(BrainCapability(
            name="memory_recall",
            description="Similarity-based memory recall",
            handler=self._recall_memory,
            region="hippocampus"
        ))
        
        # Sentiment analysis for Amygdala
        self.capabilities.append(BrainCapability(
            name="sentiment",
            description="Emotional content analysis",
            handler=self._analyze_sentiment,
            region="amygdala"
        ))
        
        # Language understanding for Wernicke's
        self.capabilities.append(BrainCapability(
            name="language_understanding",
            description="Natural language understanding",
            handler=self._understand_language,
            region="wernicke"
        ))
        
        # Language generation for Broca's
        self.capabilities.append(BrainCapability(
            name="language_generation",
            description="Natural language generation",
            handler=self._generate_language,
            region="broca"
        ))
        
    def connect_region(self, region: Any, region_name: str):
        """Connect a brain region to native capabilities."""
        self.connected_regions[region_name] = region
        
        # Inject native handlers into region
        if hasattr(region, 'set_reasoning_model'):
            region.set_reasoning_model(self._create_reasoning_interface())
            
        if hasattr(region, 'set_embedding_model'):
            region.set_embedding_model(self._create_embedding_interface())
            
        if hasattr(region, 'set_sentiment_model'):
            region.set_sentiment_model(self._create_sentiment_interface())
            
        print(f"[NativeBrainConnector] Connected to {region_name}")
        
    def _create_reasoning_interface(self):
        """Create an interface that matches expected model API."""
        class ReasoningInterface:
            def __init__(self, llm):
                self.llm = llm
                
            def process(self, input_data):
                result = self.llm.generate(str(input_data))
                return result.text
                
            def generate(self, prompt, max_tokens=256):
                result = self.llm.generate(prompt, max_tokens=max_tokens)
                return result.text
                
            def reason(self, problem, context=""):
                prompt = f"Problem: {problem}\nContext: {context}\nLet me think step by step:"
                result = self.llm.generate(prompt, max_tokens=512)
                return {
                    "problem": problem,
                    "reasoning": result.text,
                    "confidence": 0.7
                }
                
            def get_capabilities(self):
                return ["reasoning", "generation", "analysis"]
                
        return ReasoningInterface(self.llm)
        
    def _create_embedding_interface(self):
        """Create an embedding interface."""
        class EmbeddingInterface:
            def __init__(self, llm):
                self.llm = llm
                self.dimensions = llm.config.embedding_dimension
                
            def process(self, input_data):
                return self.embed(str(input_data))
                
            def embed(self, text):
                return self.llm.embed(text)
                
            def similarity(self, text1, text2):
                return self.llm.similarity(text1, text2)
                
            def get_capabilities(self):
                return ["embedding", "similarity", "retrieval"]
                
        return EmbeddingInterface(self.llm)
        
    def _create_sentiment_interface(self):
        """Create a sentiment analysis interface."""
        class SentimentInterface:
            def __init__(self, llm):
                self.llm = llm
                
            def process(self, input_data):
                return self.analyze(str(input_data))
                
            def analyze(self, text):
                # Use local embedding-based sentiment
                positive_words = ["good", "great", "happy", "love", "excellent", "wonderful"]
                negative_words = ["bad", "terrible", "hate", "awful", "sad", "angry"]
                
                text_lower = text.lower()
                pos = sum(1 for w in positive_words if w in text_lower)
                neg = sum(1 for w in negative_words if w in text_lower)
                
                if pos > neg:
                    sentiment = "positive"
                    score = pos / (pos + neg) if (pos + neg) > 0 else 0.5
                elif neg > pos:
                    sentiment = "negative"
                    score = -neg / (pos + neg) if (pos + neg) > 0 else -0.5
                else:
                    sentiment = "neutral"
                    score = 0.0
                    
                return {
                    "sentiment": sentiment,
                    "score": score,
                    "valence": score,
                    "arousal": abs(score),
                    "emotions": {},
                    "dominant": sentiment
                }
                
            def get_capabilities(self):
                return ["sentiment", "emotion_detection"]
                
        return SentimentInterface(self.llm)
        
    # Capability handlers
    
    def _reason(self, problem: str, context: str = "") -> Dict:
        """Perform reasoning."""
        prompt = f"""Analyze this problem carefully and reason through it step by step.

Problem: {problem}
{f'Context: {context}' if context else ''}

Let me think through this systematically:
1."""
        
        result = self.llm.generate(prompt, max_tokens=512)
        
        return {
            "problem": problem,
            "reasoning": result.text,
            "tokens_used": result.tokens_generated,
            "confidence": 0.7
        }
        
    def _plan(self, goal: str, constraints: List[str] = None) -> Dict:
        """Generate a plan."""
        constraints_text = ""
        if constraints:
            constraints_text = "Constraints:\n" + "\n".join(f"- {c}" for c in constraints)
            
        prompt = f"""Create a detailed step-by-step plan to achieve this goal.

Goal: {goal}
{constraints_text}

Step-by-step plan:
1."""
        
        result = self.llm.generate(prompt, max_tokens=512)
        
        # Parse steps from result
        steps = []
        for line in result.text.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                steps.append(line)
                
        return {
            "goal": goal,
            "plan": result.text,
            "steps": steps,
            "tokens_used": result.tokens_generated
        }
        
    def _embed_memory(self, content: str) -> List[float]:
        """Generate embedding for memory storage."""
        return self.llm.embed(content)
        
    def _recall_memory(
        self,
        query: str,
        memories: List[str],
        top_k: int = 5
    ) -> List[tuple]:
        """Recall similar memories."""
        return self.llm.find_similar(query, memories, top_k)
        
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text."""
        interface = self._create_sentiment_interface()
        return interface.analyze(text)
        
    def _understand_language(self, text: str) -> Dict:
        """Understand language input."""
        # Use embeddings for semantic understanding
        embedding = self.llm.embed(text)
        
        # Simple intent detection
        intents = {
            "question": ["what", "how", "why", "when", "where", "who", "?"],
            "command": ["do", "make", "create", "show", "tell", "help"],
            "greeting": ["hello", "hi", "hey", "good morning"],
            "statement": []
        }
        
        detected_intent = "statement"
        text_lower = text.lower()
        
        for intent, keywords in intents.items():
            if any(kw in text_lower for kw in keywords):
                detected_intent = intent
                break
                
        return {
            "text": text,
            "intent": detected_intent,
            "embedding": embedding,
            "word_count": len(text.split())
        }
        
    def _generate_language(
        self,
        prompt: str,
        style: str = "neutral",
        max_tokens: int = 256
    ) -> str:
        """Generate language output."""
        style_prompts = {
            "formal": "Please respond in a formal, professional manner:\n",
            "casual": "Respond casually and conversationally:\n",
            "empathetic": "Respond with empathy and understanding:\n",
            "technical": "Provide a technical, detailed response:\n",
            "neutral": ""
        }
        
        full_prompt = style_prompts.get(style, "") + prompt
        result = self.llm.generate(full_prompt, max_tokens=max_tokens)
        return result.text
        
    def process(self, capability: str, **kwargs) -> Any:
        """
        Process a request using a specific capability.
        
        Args:
            capability: Name of the capability to use
            **kwargs: Arguments for the capability handler
            
        Returns:
            Result from the capability handler
        """
        handlers = {
            "reasoning": self._reason,
            "planning": self._plan,
            "memory_embedding": self._embed_memory,
            "memory_recall": self._recall_memory,
            "sentiment": self._analyze_sentiment,
            "language_understanding": self._understand_language,
            "language_generation": self._generate_language,
        }
        
        handler = handlers.get(capability)
        if handler:
            return handler(**kwargs)
            
        raise ValueError(f"Unknown capability: {capability}")
        
    def get_status(self) -> Dict:
        """Get connector status."""
        return {
            "llm_status": self.llm.get_status(),
            "connected_regions": list(self.connected_regions.keys()),
            "capabilities": [
                {"name": c.name, "region": c.region}
                for c in self.capabilities
            ]
        }


def connect_native_llm_to_brain(brain_components: Dict = None) -> NativeBrainConnector:
    """
    Connect native LLM to brain components.
    
    Args:
        brain_components: Dictionary with brain region instances
        
    Returns:
        Configured NativeBrainConnector
    """
    connector = NativeBrainConnector()
    
    if brain_components:
        for region_name, region in brain_components.items():
            if region is not None:
                connector.connect_region(region, region_name)
                
    return connector


def create_self_contained_brain() -> Dict:
    """
    Create a completely self-contained brain with native LLM.
    
    Returns:
        Dictionary with all brain components using native AI
    """
    from unimind.ai_models import create_connected_brain
    
    # Create brain
    brain = create_connected_brain()
    
    # Create native connector
    native_connector = NativeBrainConnector()
    
    # Connect to all regions
    for region_name in ["prefrontal_cortex", "hippocampus", "amygdala", "cerebellum"]:
        region = brain.get(region_name)
        if region:
            native_connector.connect_region(region, region_name)
            
    brain["native_connector"] = native_connector
    brain["native_llm"] = native_connector.llm
    
    return brain
