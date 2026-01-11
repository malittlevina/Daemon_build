# unimind/ai_models.py
# AI Model Integration - Hooks for connecting AI models to brain regions

from typing import Dict, List, Optional, Any, Callable, Protocol
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import json


class AIModelInterface(ABC):
    """Abstract interface for AI models integrated with brain regions."""
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Process input and return output."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get model capabilities."""
        pass


class LLMInterface(AIModelInterface):
    """Interface for Large Language Models."""
    
    def __init__(self, model_name: str = "default"):
        self.model_name = model_name
        self.context_window = 4096
        self.temperature = 0.7
        
    def process(self, input_data: Any) -> Any:
        """Process with LLM (placeholder for actual implementation)."""
        # This would connect to actual LLM (OpenAI, Anthropic, local Ollama, etc.)
        return f"[LLM:{self.model_name}] Processed: {str(input_data)[:100]}"
        
    def get_capabilities(self) -> List[str]:
        return ["reasoning", "generation", "analysis", "conversation"]
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text from prompt."""
        return f"[Generated response for: {prompt[:50]}...]"
    
    def reason(self, problem: str, context: str = "") -> Dict[str, Any]:
        """Perform reasoning on a problem."""
        return {
            "problem": problem,
            "reasoning_steps": ["Analyze", "Consider", "Conclude"],
            "conclusion": "Reasoned conclusion placeholder"
        }


class EmbeddingInterface(AIModelInterface):
    """Interface for embedding models."""
    
    def __init__(self, model_name: str = "default", dimensions: int = 384):
        self.model_name = model_name
        self.dimensions = dimensions
        
    def process(self, input_data: Any) -> Any:
        """Generate embedding (placeholder)."""
        # Simple hash-based pseudo-embedding
        text = str(input_data)
        embedding = [0.0] * self.dimensions
        for i, char in enumerate(text[:self.dimensions]):
            embedding[i % self.dimensions] += (ord(char) % 100) / 100.0
        return embedding
        
    def get_capabilities(self) -> List[str]:
        return ["embedding", "similarity", "retrieval"]
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        return self.process(text)
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between texts."""
        emb1 = self.embed(text1)
        emb2 = self.embed(text2)
        
        # Cosine similarity
        dot = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = sum(a * a for a in emb1) ** 0.5
        norm2 = sum(b * b for b in emb2) ** 0.5
        
        if norm1 > 0 and norm2 > 0:
            return dot / (norm1 * norm2)
        return 0.0


class SentimentInterface(AIModelInterface):
    """Interface for sentiment analysis models."""
    
    def __init__(self, model_name: str = "default"):
        self.model_name = model_name
        
    def process(self, input_data: Any) -> Any:
        """Analyze sentiment (placeholder)."""
        return self.analyze(str(input_data))
        
    def get_capabilities(self) -> List[str]:
        return ["sentiment", "emotion_detection", "valence"]
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        text_lower = text.lower()
        
        # Simple keyword-based sentiment
        positive_words = ["good", "great", "happy", "love", "excellent", "wonderful", "best"]
        negative_words = ["bad", "terrible", "hate", "awful", "worst", "sad", "angry"]
        
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        
        if pos_count + neg_count == 0:
            sentiment = "neutral"
            score = 0.0
        elif pos_count > neg_count:
            sentiment = "positive"
            score = pos_count / (pos_count + neg_count)
        else:
            sentiment = "negative"
            score = -neg_count / (pos_count + neg_count)
            
        return {
            "sentiment": sentiment,
            "score": score,
            "positive_indicators": pos_count,
            "negative_indicators": neg_count
        }


class VisionInterface(AIModelInterface):
    """Interface for vision/image models."""
    
    def __init__(self, model_name: str = "default"):
        self.model_name = model_name
        
    def process(self, input_data: Any) -> Any:
        """Process image (placeholder)."""
        return {"description": "Image processing placeholder"}
        
    def get_capabilities(self) -> List[str]:
        return ["image_understanding", "object_detection", "scene_analysis"]
    
    def describe(self, image_data: Any) -> str:
        """Describe an image."""
        return "Image description placeholder"
    
    def detect_objects(self, image_data: Any) -> List[Dict]:
        """Detect objects in image."""
        return [{"object": "placeholder", "confidence": 0.5}]


class SpeechInterface(AIModelInterface):
    """Interface for speech models (TTS/STT)."""
    
    def __init__(self, model_name: str = "default"):
        self.model_name = model_name
        
    def process(self, input_data: Any) -> Any:
        """Process speech (placeholder)."""
        return {"transcription": str(input_data)}
        
    def get_capabilities(self) -> List[str]:
        return ["speech_to_text", "text_to_speech"]
    
    def transcribe(self, audio_data: Any) -> str:
        """Transcribe audio to text."""
        return "Transcription placeholder"
    
    def synthesize(self, text: str) -> Any:
        """Synthesize speech from text."""
        return f"[Audio for: {text[:50]}]"


@dataclass
class AIModelRegistry:
    """Registry for AI models connected to brain regions."""
    
    models: Dict[str, AIModelInterface] = field(default_factory=dict)
    region_assignments: Dict[str, List[str]] = field(default_factory=dict)  # region -> model_ids
    
    def register(self, model_id: str, model: AIModelInterface, regions: List[str] = None):
        """Register a model and optionally assign to regions."""
        self.models[model_id] = model
        
        if regions:
            for region in regions:
                if region not in self.region_assignments:
                    self.region_assignments[region] = []
                self.region_assignments[region].append(model_id)
                
        print(f"[AIModelRegistry] Registered: {model_id} ({type(model).__name__})")
        
    def get_model(self, model_id: str) -> Optional[AIModelInterface]:
        """Get a model by ID."""
        return self.models.get(model_id)
    
    def get_models_for_region(self, region: str) -> List[AIModelInterface]:
        """Get all models assigned to a region."""
        model_ids = self.region_assignments.get(region, [])
        return [self.models[mid] for mid in model_ids if mid in self.models]
    
    def list_models(self) -> List[Dict]:
        """List all registered models."""
        return [
            {
                "model_id": mid,
                "type": type(model).__name__,
                "capabilities": model.get_capabilities()
            }
            for mid, model in self.models.items()
        ]


class BrainRegionModelConnector:
    """
    Connects AI models to brain regions for enhanced processing.
    
    This allows brain regions to use external AI capabilities:
    - Prefrontal Cortex: LLM for reasoning and planning
    - Hippocampus: Embeddings for semantic memory
    - Amygdala: Sentiment analysis for emotion detection
    - Cerebellum: Prediction models
    - Language Areas: LLM for generation/understanding
    """
    
    def __init__(self, cortex=None):
        self.cortex = cortex
        self.registry = AIModelRegistry()
        
        # Default model instances
        self._setup_default_models()
        
    def _setup_default_models(self):
        """Set up default model interfaces."""
        # These are placeholder implementations
        # In production, these would connect to actual AI services
        
        self.registry.register(
            "llm_reasoning",
            LLMInterface("reasoning"),
            regions=["prefrontal_cortex", "cortex"]
        )
        
        self.registry.register(
            "embeddings",
            EmbeddingInterface("semantic"),
            regions=["hippocampus"]
        )
        
        self.registry.register(
            "sentiment",
            SentimentInterface("emotion"),
            regions=["amygdala"]
        )
        
        self.registry.register(
            "llm_generation",
            LLMInterface("generation"),
            regions=["broca_area", "cortex"]
        )
        
    def connect_to_region(self, region: Any, region_name: str):
        """
        Connect appropriate AI models to a brain region.
        
        Args:
            region: The brain region module
            region_name: Name/type of the region
        """
        models = self.registry.get_models_for_region(region_name)
        
        for model in models:
            if isinstance(model, LLMInterface):
                if hasattr(region, 'set_reasoning_model'):
                    region.set_reasoning_model(model)
            elif isinstance(model, EmbeddingInterface):
                if hasattr(region, 'set_embedding_model'):
                    region.set_embedding_model(model)
            elif isinstance(model, SentimentInterface):
                if hasattr(region, 'set_sentiment_model'):
                    region.set_sentiment_model(model)
                    
        print(f"[BrainRegionModelConnector] Connected {len(models)} models to {region_name}")
        
    def register_custom_model(
        self,
        model_id: str,
        model: AIModelInterface,
        regions: List[str]
    ):
        """Register a custom model and connect to regions."""
        self.registry.register(model_id, model, regions)
        
    def process_with_models(
        self,
        region_name: str,
        input_data: Any,
        capability: str = None
    ) -> List[Any]:
        """
        Process input using models assigned to a region.
        
        Args:
            region_name: Region to use models from
            input_data: Data to process
            capability: Optional specific capability needed
            
        Returns:
            List of model outputs
        """
        models = self.registry.get_models_for_region(region_name)
        results = []
        
        for model in models:
            if capability is None or capability in model.get_capabilities():
                try:
                    result = model.process(input_data)
                    results.append({
                        "model": type(model).__name__,
                        "result": result
                    })
                except Exception as e:
                    results.append({
                        "model": type(model).__name__,
                        "error": str(e)
                    })
                    
        return results
        
    def get_status(self) -> Dict[str, Any]:
        """Get connector status."""
        return {
            "total_models": len(self.registry.models),
            "region_assignments": {k: len(v) for k, v in self.registry.region_assignments.items()},
            "models": self.registry.list_models()
        }


# Factory function for creating a complete brain with AI models
def create_connected_brain(neural_bus=None) -> Dict[str, Any]:
    """
    Create a complete brain system with AI model connections.
    
    Returns:
        Dictionary with all brain components
    """
    from unimind.cortex import UnimindCortex, get_cortex
    from unimind.neural_bus import get_neural_bus
    from unimind.regions import PrefrontalCortex, Hippocampus, Amygdala, Cerebellum
    
    # Get or create neural bus
    if neural_bus is None:
        neural_bus = get_neural_bus()
        
    # Create cortex
    cortex = get_cortex()
    
    # Create brain regions
    prefrontal = PrefrontalCortex(neural_bus=neural_bus, cortex=cortex)
    hippocampus = Hippocampus(neural_bus=neural_bus)
    amygdala = Amygdala(neural_bus=neural_bus)
    cerebellum = Cerebellum(neural_bus=neural_bus)
    
    # Register regions with cortex
    cortex.register_brain_region("prefrontal_cortex", prefrontal)
    cortex.register_brain_region("hippocampus", hippocampus)
    cortex.register_brain_region("amygdala", amygdala)
    cortex.register_brain_region("cerebellum", cerebellum)
    
    # Create AI model connector
    connector = BrainRegionModelConnector(cortex)
    
    # Connect models to regions
    connector.connect_to_region(prefrontal, "prefrontal_cortex")
    connector.connect_to_region(hippocampus, "hippocampus")
    connector.connect_to_region(amygdala, "amygdala")
    
    # Start neural bus processing
    neural_bus.start_processing()
    
    return {
        "neural_bus": neural_bus,
        "cortex": cortex,
        "prefrontal_cortex": prefrontal,
        "hippocampus": hippocampus,
        "amygdala": amygdala,
        "cerebellum": cerebellum,
        "ai_connector": connector
    }
