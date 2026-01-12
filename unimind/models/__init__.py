# unimind/models/__init__.py
# Enhanced AI Models Package - Advanced capabilities for Unimind

"""
Unimind AI Models Package

This package provides advanced AI model capabilities including:
- LLM providers (Ollama, OpenAI, Mock)
- Cognitive model training framework
- Chain-of-thought reasoning
- Specialized cognitive models (NLU, Reasoning, Creative, Emotional)
- Model orchestration and routing
- Fine-tuning and adaptation
"""

# LLM Providers
from unimind.models.llm_providers import (
    LLMProvider,
    LLMConfig,
    LLMResponse,
    Message,
    BaseLLMProvider,
    OllamaProvider,
    OpenAIProvider,
    MockProvider,
    LLMProviderFactory,
    InferenceCache,
    LLMManager,
    create_llm_manager,
    ModelCapability,
)

# Training Framework
from unimind.models.training_framework import (
    TrainingMode,
    DatasetType,
    TrainingSample,
    TrainingBatch,
    TrainingMetrics,
    TrainingDataset,
    RewardModel,
    TrainingConfig,
    CognitiveTrainer,
    DatasetBuilder,
    create_trainer_with_datasets,
)

# Chain-of-Thought Reasoning
from unimind.models.chain_of_thought import (
    ThoughtType,
    ReasoningStrategy,
    ThoughtStep,
    ReasoningTrace,
    ReasoningPromptBuilder,
    ChainOfThoughtEngine,
    create_reasoner,
)

# Cognitive Models
from unimind.models.cognitive_models import (
    CognitiveCapability,
    ModelOutput,
    BaseCognitiveModel,
    NLUModel,
    IntentResult,
    EntityResult,
    ReasoningModel,
    ReasoningType,
    ReasoningResult,
    CreativeModel,
    CreativeOutput,
    EmotionalIntelligenceModel,
    EmotionalState,
    CognitiveModelRegistry,
    create_cognitive_models,
)

# Orchestration
from unimind.models.orchestration import (
    TaskPriority,
    TaskStatus,
    ModelType,
    ModelTask,
    ModelEndpoint,
    RoutingStrategy,
    RoutingRule,
    ModelRouter,
    TaskQueue,
    ModelPipeline,
    ModelOrchestrator,
    ModelEnsemble,
    create_orchestrator,
    create_nlu_reasoning_pipeline,
)

# Fine-Tuning
from unimind.models.fine_tuning import (
    FineTuneMethod,
    AdaptationType,
    FineTuneConfig,
    FineTuneDataset,
    FineTuneCheckpoint,
    FineTuneResult,
    LoRAAdapter,
    PromptTemplate,
    FineTuner,
    DomainAdapter,
    create_fine_tuner,
    create_instruction_dataset,
    create_conversation_dataset,
)

# Brain Integration
from unimind.models.brain_integration import (
    BrainModelMapping,
    EnhancedBrainConnector,
    get_brain_connector,
    connect_brain_with_enhanced_models,
)


__all__ = [
    # LLM Providers
    "LLMProvider",
    "LLMConfig",
    "LLMResponse",
    "Message",
    "BaseLLMProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "MockProvider",
    "LLMProviderFactory",
    "InferenceCache",
    "LLMManager",
    "create_llm_manager",
    "ModelCapability",
    
    # Training
    "TrainingMode",
    "DatasetType",
    "TrainingSample",
    "TrainingBatch",
    "TrainingMetrics",
    "TrainingDataset",
    "RewardModel",
    "TrainingConfig",
    "CognitiveTrainer",
    "DatasetBuilder",
    "create_trainer_with_datasets",
    
    # Chain-of-Thought
    "ThoughtType",
    "ReasoningStrategy",
    "ThoughtStep",
    "ReasoningTrace",
    "ReasoningPromptBuilder",
    "ChainOfThoughtEngine",
    "create_reasoner",
    
    # Cognitive Models
    "CognitiveCapability",
    "ModelOutput",
    "BaseCognitiveModel",
    "NLUModel",
    "IntentResult",
    "EntityResult",
    "ReasoningModel",
    "ReasoningType",
    "ReasoningResult",
    "CreativeModel",
    "CreativeOutput",
    "EmotionalIntelligenceModel",
    "EmotionalState",
    "CognitiveModelRegistry",
    "create_cognitive_models",
    
    # Orchestration
    "TaskPriority",
    "TaskStatus",
    "ModelType",
    "ModelTask",
    "ModelEndpoint",
    "RoutingStrategy",
    "RoutingRule",
    "ModelRouter",
    "TaskQueue",
    "ModelPipeline",
    "ModelOrchestrator",
    "ModelEnsemble",
    "create_orchestrator",
    "create_nlu_reasoning_pipeline",
    
    # Fine-Tuning
    "FineTuneMethod",
    "AdaptationType",
    "FineTuneConfig",
    "FineTuneDataset",
    "FineTuneCheckpoint",
    "FineTuneResult",
    "LoRAAdapter",
    "PromptTemplate",
    "FineTuner",
    "DomainAdapter",
    "create_fine_tuner",
    "create_instruction_dataset",
    "create_conversation_dataset",
    
    # Brain Integration
    "BrainModelMapping",
    "EnhancedBrainConnector",
    "get_brain_connector",
    "connect_brain_with_enhanced_models",
]
