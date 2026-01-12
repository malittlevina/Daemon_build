# unimind/models/brain_integration.py
# Integration of Enhanced AI Models with Brain Regions

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BrainModelMapping:
    """Maps brain regions to their AI model capabilities."""
    
    region_name: str
    primary_models: List[str]
    capabilities: List[str]
    processing_mode: str = "sequential"  # "sequential", "parallel", "ensemble"
    
    
class EnhancedBrainConnector:
    """
    Enhanced connector between AI models and brain regions.
    
    Provides advanced integration including:
    - Multi-model support per region
    - Chain-of-thought reasoning integration
    - Training/fine-tuning hooks
    - Cognitive model specialization
    """
    
    # Default mappings for brain regions
    REGION_MAPPINGS = {
        "prefrontal_cortex": BrainModelMapping(
            region_name="prefrontal_cortex",
            primary_models=["llm_reasoning", "chain_of_thought", "planning"],
            capabilities=["reasoning", "planning", "decision_making", "executive_control"],
            processing_mode="sequential"
        ),
        "hippocampus": BrainModelMapping(
            region_name="hippocampus",
            primary_models=["embedding", "memory_model", "spatial"],
            capabilities=["memory_formation", "recall", "navigation", "consolidation"],
            processing_mode="parallel"
        ),
        "amygdala": BrainModelMapping(
            region_name="amygdala",
            primary_models=["emotional_intelligence", "sentiment"],
            capabilities=["emotion_recognition", "fear_processing", "reward", "empathy"],
            processing_mode="ensemble"
        ),
        "cerebellum": BrainModelMapping(
            region_name="cerebellum",
            primary_models=["pattern_model", "motor_learning"],
            capabilities=["pattern_recognition", "timing", "procedural_memory"],
            processing_mode="sequential"
        ),
        "wernicke_area": BrainModelMapping(
            region_name="wernicke_area",
            primary_models=["nlu", "semantic_model"],
            capabilities=["language_understanding", "semantic_processing"],
            processing_mode="sequential"
        ),
        "broca_area": BrainModelMapping(
            region_name="broca_area",
            primary_models=["llm_generation", "speech_production"],
            capabilities=["language_generation", "speech_planning"],
            processing_mode="sequential"
        ),
        "visual_cortex": BrainModelMapping(
            region_name="visual_cortex",
            primary_models=["vision_model", "spatial_processing"],
            capabilities=["image_understanding", "object_recognition", "scene_analysis"],
            processing_mode="parallel"
        )
    }
    
    def __init__(self):
        self.connected_regions: Dict[str, Any] = {}
        self.model_instances: Dict[str, Any] = {}
        self.cognitive_registry = None
        self.llm_manager = None
        self.cot_engine = None
        self.orchestrator = None
        self.trainers: Dict[str, Any] = {}
        
    def initialize_models(self):
        """Initialize all enhanced AI models."""
        # Import here to avoid circular imports
        from unimind.models.llm_providers import create_llm_manager
        from unimind.models.chain_of_thought import create_reasoner
        from unimind.models.cognitive_models import create_cognitive_models
        from unimind.models.orchestration import ModelOrchestrator, ModelType
        
        # Create LLM manager with available providers
        self.llm_manager = create_llm_manager(use_ollama=True, use_mock=True)
        print("[EnhancedBrainConnector] LLM Manager initialized")
        
        # Create chain-of-thought engine
        llm_provider = self.llm_manager.get_provider("ollama") or self.llm_manager.get_provider("mock")
        self.cot_engine = create_reasoner(llm_provider)
        print("[EnhancedBrainConnector] Chain-of-Thought engine initialized")
        
        # Create cognitive model registry
        self.cognitive_registry = create_cognitive_models()
        print("[EnhancedBrainConnector] Cognitive models initialized")
        
        # Create orchestrator
        self.orchestrator = ModelOrchestrator(max_workers=4)
        
        # Register models with orchestrator
        for name, model in self.cognitive_registry.models.items():
            model_type = self._get_model_type(name)
            self.orchestrator.register_model(name, model_type, model)
            self.model_instances[name] = model
            
        print(f"[EnhancedBrainConnector] Registered {len(self.model_instances)} models")
        
    def _get_model_type(self, name: str):
        """Map model name to ModelType."""
        from unimind.models.orchestration import ModelType
        
        type_map = {
            "nlu": ModelType.NLU,
            "reasoning": ModelType.REASONING,
            "creative": ModelType.CREATIVE,
            "emotional": ModelType.EMOTIONAL,
        }
        return type_map.get(name, ModelType.LLM)
        
    def connect_region(self, region: Any, region_name: str):
        """
        Connect enhanced AI models to a brain region.
        
        Args:
            region: Brain region instance
            region_name: Name of the region
        """
        mapping = self.REGION_MAPPINGS.get(region_name)
        if not mapping:
            print(f"[EnhancedBrainConnector] No mapping for region: {region_name}")
            return
            
        self.connected_regions[region_name] = region
        
        # Connect appropriate models based on mapping
        for model_id in mapping.primary_models:
            self._connect_model_to_region(region, region_name, model_id)
            
        print(f"[EnhancedBrainConnector] Connected {len(mapping.primary_models)} models to {region_name}")
        
    def _connect_model_to_region(self, region: Any, region_name: str, model_id: str):
        """Connect a specific model to a region."""
        # Handle LLM connections
        if model_id in ["llm_reasoning", "llm_generation"]:
            if hasattr(region, 'set_reasoning_model') and self.llm_manager:
                provider = self.llm_manager.get_provider("mock")
                if provider:
                    region.set_reasoning_model(provider)
                    
        # Handle embedding connections
        elif model_id == "embedding":
            if hasattr(region, 'set_embedding_model') and self.cognitive_registry:
                # Create embedding-like interface from NLU
                nlu = self.cognitive_registry.get("nlu")
                if nlu and hasattr(region, 'set_embedding_model'):
                    region.set_embedding_model(nlu)
                    
        # Handle sentiment connections
        elif model_id in ["sentiment", "emotional_intelligence"]:
            if hasattr(region, 'set_sentiment_model') and self.cognitive_registry:
                emotional = self.cognitive_registry.get("emotional")
                if emotional:
                    region.set_sentiment_model(emotional)
                    
        # Handle chain-of-thought connections
        elif model_id == "chain_of_thought":
            if hasattr(region, 'set_reasoning_engine') and self.cot_engine:
                region.set_reasoning_engine(self.cot_engine)
                
        # Handle NLU connections
        elif model_id == "nlu":
            if hasattr(region, 'set_nlu_model') and self.cognitive_registry:
                nlu = self.cognitive_registry.get("nlu")
                if nlu:
                    region.set_nlu_model(nlu)
                    
    def process_with_region(
        self,
        region_name: str,
        input_data: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process input using models connected to a region.
        
        Args:
            region_name: Name of the brain region
            input_data: Input data to process
            **kwargs: Additional processing parameters
            
        Returns:
            Processing results from all connected models
        """
        mapping = self.REGION_MAPPINGS.get(region_name)
        if not mapping:
            return {"error": f"Unknown region: {region_name}"}
            
        results = {}
        
        # Process based on mode
        if mapping.processing_mode == "sequential":
            results = self._process_sequential(mapping, input_data, **kwargs)
        elif mapping.processing_mode == "parallel":
            results = self._process_parallel(mapping, input_data, **kwargs)
        elif mapping.processing_mode == "ensemble":
            results = self._process_ensemble(mapping, input_data, **kwargs)
            
        return results
        
    def _process_sequential(self, mapping: BrainModelMapping, input_data: Any, **kwargs) -> Dict:
        """Process sequentially through models."""
        current_data = input_data
        results = {"steps": [], "final": None}
        
        for model_id in mapping.primary_models:
            model = self.model_instances.get(model_id)
            if model:
                try:
                    output = model.process(current_data, **kwargs)
                    results["steps"].append({
                        "model": model_id,
                        "output": output
                    })
                    # Use output as input for next model
                    if hasattr(output, 'content'):
                        current_data = output.content
                    else:
                        current_data = output
                except Exception as e:
                    results["steps"].append({
                        "model": model_id,
                        "error": str(e)
                    })
                    
        results["final"] = current_data
        return results
        
    def _process_parallel(self, mapping: BrainModelMapping, input_data: Any, **kwargs) -> Dict:
        """Process in parallel through all models."""
        results = {"outputs": {}, "combined": None}
        
        for model_id in mapping.primary_models:
            model = self.model_instances.get(model_id)
            if model:
                try:
                    output = model.process(input_data, **kwargs)
                    results["outputs"][model_id] = output
                except Exception as e:
                    results["outputs"][model_id] = {"error": str(e)}
                    
        # Combine results (simple aggregation)
        if results["outputs"]:
            first = list(results["outputs"].values())[0]
            results["combined"] = first
            
        return results
        
    def _process_ensemble(self, mapping: BrainModelMapping, input_data: Any, **kwargs) -> Dict:
        """Process as an ensemble with voting/aggregation."""
        from unimind.models.orchestration import ModelEnsemble
        
        ensemble = ModelEnsemble(f"{mapping.region_name}_ensemble", aggregation="max_confidence")
        
        for model_id in mapping.primary_models:
            model = self.model_instances.get(model_id)
            if model:
                ensemble.add_model(model_id, model)
                
        return ensemble.predict(input_data, **kwargs)
        
    def reason_with_cot(
        self,
        query: str,
        region_name: str = "prefrontal_cortex",
        strategy: str = "step_by_step"
    ) -> Dict:
        """
        Perform chain-of-thought reasoning.
        
        Args:
            query: The question or problem to reason about
            region_name: Brain region context
            strategy: Reasoning strategy to use
            
        Returns:
            Reasoning trace with steps and conclusion
        """
        if not self.cot_engine:
            return {"error": "Chain-of-thought engine not initialized"}
            
        from unimind.models.chain_of_thought import ReasoningStrategy
        
        strategy_map = {
            "step_by_step": ReasoningStrategy.STEP_BY_STEP,
            "tree_of_thought": ReasoningStrategy.TREE_OF_THOUGHT,
            "self_consistency": ReasoningStrategy.SELF_CONSISTENCY,
            "least_to_most": ReasoningStrategy.LEAST_TO_MOST,
            "verify_and_edit": ReasoningStrategy.VERIFY_AND_EDIT,
        }
        
        strat = strategy_map.get(strategy, ReasoningStrategy.STEP_BY_STEP)
        trace = self.cot_engine.reason(query, strategy=strat)
        
        return {
            "trace_id": trace.trace_id,
            "query": query,
            "strategy": strategy,
            "steps": [s.to_dict() for s in trace.steps],
            "final_answer": trace.final_answer,
            "confidence": trace.total_confidence,
            "formatted": trace.get_formatted_chain()
        }
        
    def train_region_model(
        self,
        region_name: str,
        training_data: List[Dict],
        epochs: int = 3
    ) -> Dict:
        """
        Train models associated with a brain region.
        
        Args:
            region_name: Brain region to train
            training_data: List of training samples
            epochs: Number of training epochs
            
        Returns:
            Training results
        """
        from unimind.models.training_framework import (
            TrainingDataset, CognitiveTrainer, TrainingConfig, TrainingMode, DatasetType
        )
        
        mapping = self.REGION_MAPPINGS.get(region_name)
        if not mapping:
            return {"error": f"Unknown region: {region_name}"}
            
        results = {}
        
        for model_id in mapping.primary_models:
            model = self.model_instances.get(model_id)
            if model and hasattr(model, 'process'):
                # Create dataset
                dataset = TrainingDataset(f"{region_name}_{model_id}")
                
                for sample in training_data:
                    dataset.add_sample(
                        input_text=sample.get("input", ""),
                        target_output=sample.get("output", ""),
                        sample_type=DatasetType.CONVERSATION
                    )
                    
                # Create trainer
                config = TrainingConfig(
                    mode=TrainingMode.CURRICULUM,
                    epochs=epochs,
                    curriculum_enabled=True
                )
                
                trainer = CognitiveTrainer(model, config)
                trainer.set_dataset(dataset)
                
                # Train
                try:
                    metrics = trainer.train()
                    results[model_id] = {
                        "success": True,
                        "metrics": metrics.to_dict()
                    }
                except Exception as e:
                    results[model_id] = {
                        "success": False,
                        "error": str(e)
                    }
                    
                self.trainers[f"{region_name}_{model_id}"] = trainer
                
        return results
        
    def fine_tune_for_domain(
        self,
        domain: str,
        training_data: List[Dict],
        epochs: int = 3
    ) -> Dict:
        """
        Fine-tune models for a specific domain.
        
        Args:
            domain: Domain to fine-tune for
            training_data: Training data for the domain
            epochs: Number of epochs
            
        Returns:
            Fine-tuning results
        """
        from unimind.models.fine_tuning import (
            DomainAdapter, FineTuneDataset, FineTuneConfig, FineTuneMethod
        )
        
        results = {}
        
        # Get primary model
        if not self.llm_manager:
            return {"error": "LLM manager not initialized"}
            
        provider = self.llm_manager.get_provider("mock")
        adapter = DomainAdapter(provider)
        
        # Create dataset
        dataset = adapter.create_domain_dataset(domain)
        for sample in training_data:
            dataset.add_sample(
                sample.get("instruction", ""),
                sample.get("input", ""),
                sample.get("output", "")
            )
            
        # Fine-tune
        try:
            result = adapter.adapt_to_domain(domain, dataset)
            results = {
                "success": result.success,
                "final_loss": result.final_loss,
                "training_time": result.training_time_seconds,
                "model_path": result.model_path
            }
        except Exception as e:
            results = {"success": False, "error": str(e)}
            
        return results
        
    def get_status(self) -> Dict:
        """Get connector status."""
        return {
            "initialized": self.llm_manager is not None,
            "connected_regions": list(self.connected_regions.keys()),
            "model_instances": list(self.model_instances.keys()),
            "has_cot_engine": self.cot_engine is not None,
            "has_orchestrator": self.orchestrator is not None,
            "active_trainers": list(self.trainers.keys()),
            "llm_status": self.llm_manager.get_status() if self.llm_manager else None,
            "cognitive_models": self.cognitive_registry.list_models() if self.cognitive_registry else None
        }


# =============================================================================
# Factory Functions
# =============================================================================

_global_connector: Optional[EnhancedBrainConnector] = None


def get_brain_connector() -> EnhancedBrainConnector:
    """Get or create the global brain connector."""
    global _global_connector
    if _global_connector is None:
        _global_connector = EnhancedBrainConnector()
        _global_connector.initialize_models()
    return _global_connector


def connect_brain_with_enhanced_models(cortex=None, neural_bus=None) -> Dict[str, Any]:
    """
    Connect enhanced AI models to a complete brain system.
    
    Args:
        cortex: UnimindCortex instance (optional)
        neural_bus: NeuralBus instance (optional)
        
    Returns:
        Dictionary with brain components and connector
    """
    from unimind.ai_models import create_connected_brain
    
    # Create brain if needed
    brain = create_connected_brain(neural_bus)
    
    # Get enhanced connector
    connector = get_brain_connector()
    
    # Connect to brain regions
    for region_name, region in [
        ("prefrontal_cortex", brain.get("prefrontal_cortex")),
        ("hippocampus", brain.get("hippocampus")),
        ("amygdala", brain.get("amygdala")),
        ("cerebellum", brain.get("cerebellum")),
    ]:
        if region:
            connector.connect_region(region, region_name)
            
    return {
        **brain,
        "enhanced_connector": connector
    }
