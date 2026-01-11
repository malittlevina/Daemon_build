# unimind/models/fine_tuning.py
# Model Fine-Tuning and Adaptation System

from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
import time
from pathlib import Path


class FineTuneMethod(Enum):
    """Fine-tuning methods."""
    FULL = "full"                    # Full parameter fine-tuning
    LORA = "lora"                    # Low-Rank Adaptation
    QLORA = "qlora"                  # Quantized LoRA
    PREFIX_TUNING = "prefix_tuning"  # Soft prompts
    ADAPTER = "adapter"              # Adapter layers
    PROMPT_TUNING = "prompt_tuning"  # Learnable prompt tokens
    DISTILLATION = "distillation"    # Knowledge distillation


class AdaptationType(Enum):
    """Types of model adaptation."""
    TASK_SPECIFIC = "task_specific"      # Adapt for specific task
    DOMAIN_SPECIFIC = "domain_specific"  # Adapt for domain
    STYLE_TRANSFER = "style_transfer"    # Adapt output style
    PERSONA = "persona"                  # Adapt personality
    SAFETY = "safety"                    # Safety fine-tuning
    INSTRUCTION = "instruction"          # Instruction following


@dataclass
class FineTuneConfig:
    """Configuration for fine-tuning."""
    method: FineTuneMethod = FineTuneMethod.LORA
    adaptation_type: AdaptationType = AdaptationType.TASK_SPECIFIC
    
    # Training parameters
    epochs: int = 3
    batch_size: int = 8
    learning_rate: float = 2e-5
    warmup_steps: int = 100
    weight_decay: float = 0.01
    gradient_accumulation_steps: int = 4
    
    # LoRA specific
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    
    # Data
    max_seq_length: int = 512
    train_split: float = 0.9
    
    # Checkpointing
    save_steps: int = 500
    eval_steps: int = 100
    output_dir: str = "fine_tuned_models"
    
    def to_dict(self) -> Dict:
        return {
            "method": self.method.value,
            "adaptation_type": self.adaptation_type.value,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "lora_rank": self.lora_rank
        }


@dataclass
class FineTuneDataset:
    """Dataset for fine-tuning."""
    name: str
    samples: List[Dict[str, str]] = field(default_factory=list)
    
    def add_sample(self, instruction: str, input_text: str, output: str):
        """Add a training sample."""
        self.samples.append({
            "instruction": instruction,
            "input": input_text,
            "output": output
        })
        
    def add_conversation(self, messages: List[Dict[str, str]]):
        """Add a conversation sample."""
        self.samples.append({"messages": messages})
        
    def to_jsonl(self, path: str):
        """Save dataset as JSONL."""
        with open(path, "w") as f:
            for sample in self.samples:
                f.write(json.dumps(sample) + "\n")
                
    def from_jsonl(self, path: str):
        """Load dataset from JSONL."""
        with open(path) as f:
            for line in f:
                self.samples.append(json.loads(line))
                
    @property
    def size(self) -> int:
        return len(self.samples)
        
    def get_stats(self) -> Dict:
        return {
            "name": self.name,
            "samples": len(self.samples)
        }


@dataclass
class FineTuneCheckpoint:
    """A training checkpoint."""
    checkpoint_id: str
    step: int
    epoch: int
    loss: float
    eval_loss: Optional[float]
    path: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "checkpoint_id": self.checkpoint_id,
            "step": self.step,
            "epoch": self.epoch,
            "loss": self.loss,
            "eval_loss": self.eval_loss,
            "path": self.path
        }


@dataclass 
class FineTuneResult:
    """Result of fine-tuning."""
    success: bool
    final_loss: float
    best_checkpoint: Optional[FineTuneCheckpoint]
    training_time_seconds: float
    samples_processed: int
    model_path: str
    metrics: Dict[str, float] = field(default_factory=dict)


class LoRAAdapter:
    """
    Low-Rank Adaptation (LoRA) implementation.
    
    Efficiently adapts large models by adding low-rank matrices
    to specific layers without modifying base weights.
    """
    
    def __init__(self, rank: int = 8, alpha: int = 16, dropout: float = 0.1):
        self.rank = rank
        self.alpha = alpha
        self.dropout = dropout
        self.scaling = alpha / rank
        
        # Simulated LoRA weights
        self.adapters: Dict[str, Dict[str, Any]] = {}
        
    def create_adapter(self, module_name: str, input_dim: int, output_dim: int):
        """Create LoRA adapter for a module."""
        import random
        
        # Simulated low-rank matrices
        lora_A = [[random.gauss(0, 0.02) for _ in range(self.rank)] for _ in range(input_dim)]
        lora_B = [[0.0 for _ in range(output_dim)] for _ in range(self.rank)]
        
        self.adapters[module_name] = {
            "lora_A": lora_A,
            "lora_B": lora_B,
            "input_dim": input_dim,
            "output_dim": output_dim,
            "enabled": True
        }
        
    def forward(self, module_name: str, x: List[float]) -> List[float]:
        """Apply LoRA transformation."""
        if module_name not in self.adapters:
            return x
            
        adapter = self.adapters[module_name]
        if not adapter["enabled"]:
            return x
            
        # Simplified LoRA forward: output = x + scaling * (x @ A) @ B
        lora_A = adapter["lora_A"]
        lora_B = adapter["lora_B"]
        
        # This is a simplified simulation
        return [v * (1.0 + self.scaling * 0.01) for v in x]
        
    def merge_weights(self, module_name: str):
        """Merge LoRA weights into base model (conceptual)."""
        if module_name in self.adapters:
            self.adapters[module_name]["merged"] = True
            
    def save(self, path: str):
        """Save LoRA adapters."""
        with open(path, "w") as f:
            json.dump({
                "rank": self.rank,
                "alpha": self.alpha,
                "dropout": self.dropout,
                "adapters": {
                    name: {
                        "input_dim": a["input_dim"],
                        "output_dim": a["output_dim"],
                        "enabled": a["enabled"]
                    }
                    for name, a in self.adapters.items()
                }
            }, f, indent=2)
            
    def load(self, path: str):
        """Load LoRA adapters."""
        with open(path) as f:
            data = json.load(f)
            self.rank = data["rank"]
            self.alpha = data["alpha"]
            self.dropout = data["dropout"]


class PromptTemplate:
    """Template for formatting fine-tuning data."""
    
    ALPACA = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input}

### Response:
{output}"""

    CHAT = """<|user|>
{instruction}

{input}
<|assistant|>
{output}"""

    SIMPLE = """{instruction}

{input}

{output}"""

    @staticmethod
    def format_sample(
        template: str,
        instruction: str,
        input_text: str,
        output: str
    ) -> str:
        """Format a sample using the template."""
        return template.format(
            instruction=instruction,
            input=input_text if input_text else "",
            output=output
        )


class FineTuner:
    """
    Main fine-tuning system for cognitive models.
    
    Features:
    - Multiple fine-tuning methods (LoRA, adapters, etc.)
    - Dataset management
    - Training loop with checkpoints
    - Evaluation and metrics
    """
    
    def __init__(self, model: Any, config: FineTuneConfig = None):
        self.model = model
        self.config = config or FineTuneConfig()
        self.dataset: Optional[FineTuneDataset] = None
        self.checkpoints: List[FineTuneCheckpoint] = []
        self.training_history: List[Dict] = []
        self.is_training = False
        self.lora_adapter: Optional[LoRAAdapter] = None
        
        # Initialize LoRA if needed
        if self.config.method == FineTuneMethod.LORA:
            self.lora_adapter = LoRAAdapter(
                rank=self.config.lora_rank,
                alpha=self.config.lora_alpha,
                dropout=self.config.lora_dropout
            )
            
    def set_dataset(self, dataset: FineTuneDataset):
        """Set the fine-tuning dataset."""
        self.dataset = dataset
        print(f"[FineTuner] Dataset set: {dataset.name} ({dataset.size} samples)")
        
    def prepare_data(self) -> Tuple[List[Dict], List[Dict]]:
        """Prepare training and validation data."""
        if not self.dataset:
            raise ValueError("No dataset set")
            
        samples = self.dataset.samples.copy()
        import random
        random.shuffle(samples)
        
        split_idx = int(len(samples) * self.config.train_split)
        train_data = samples[:split_idx]
        val_data = samples[split_idx:]
        
        return train_data, val_data
        
    def fine_tune(
        self,
        callbacks: List[Callable] = None
    ) -> FineTuneResult:
        """
        Run fine-tuning process.
        
        Returns:
            FineTuneResult with training metrics
        """
        if not self.dataset:
            raise ValueError("No dataset set")
            
        callbacks = callbacks or []
        start_time = time.time()
        
        print(f"[FineTuner] Starting fine-tuning with {self.config.method.value}")
        print(f"  - Epochs: {self.config.epochs}")
        print(f"  - Batch size: {self.config.batch_size}")
        print(f"  - Samples: {self.dataset.size}")
        
        self.is_training = True
        train_data, val_data = self.prepare_data()
        
        total_steps = (len(train_data) // self.config.batch_size) * self.config.epochs
        current_step = 0
        best_loss = float('inf')
        best_checkpoint = None
        
        for epoch in range(self.config.epochs):
            epoch_loss = 0.0
            batches = 0
            
            # Shuffle training data each epoch
            import random
            random.shuffle(train_data)
            
            # Process batches
            for i in range(0, len(train_data), self.config.batch_size):
                batch = train_data[i:i + self.config.batch_size]
                
                # Training step (simulated)
                batch_loss = self._training_step(batch)
                epoch_loss += batch_loss
                batches += 1
                current_step += 1
                
                # Save checkpoint
                if current_step % self.config.save_steps == 0:
                    checkpoint = self._save_checkpoint(current_step, epoch, batch_loss)
                    self.checkpoints.append(checkpoint)
                    
                    if batch_loss < best_loss:
                        best_loss = batch_loss
                        best_checkpoint = checkpoint
                        
            # Epoch metrics
            avg_loss = epoch_loss / max(1, batches)
            eval_loss = self._evaluate(val_data) if val_data else None
            
            epoch_record = {
                "epoch": epoch + 1,
                "train_loss": avg_loss,
                "eval_loss": eval_loss,
                "step": current_step
            }
            self.training_history.append(epoch_record)
            
            print(f"  Epoch {epoch + 1}/{self.config.epochs}: train_loss={avg_loss:.4f}" + 
                  (f", eval_loss={eval_loss:.4f}" if eval_loss else ""))
                  
            for callback in callbacks:
                callback(epoch_record)
                
        self.is_training = False
        training_time = time.time() - start_time
        
        # Save final model
        model_path = self._save_model()
        
        return FineTuneResult(
            success=True,
            final_loss=self.training_history[-1]["train_loss"] if self.training_history else 0,
            best_checkpoint=best_checkpoint,
            training_time_seconds=training_time,
            samples_processed=self.dataset.size * self.config.epochs,
            model_path=model_path,
            metrics={
                "total_steps": current_step,
                "best_loss": best_loss,
                "epochs_completed": self.config.epochs
            }
        )
        
    def _training_step(self, batch: List[Dict]) -> float:
        """Execute a training step."""
        # Simulated training step
        import random
        
        loss = 0.0
        for sample in batch:
            # Format input
            if "messages" in sample:
                text = str(sample["messages"])
            else:
                text = PromptTemplate.format_sample(
                    PromptTemplate.SIMPLE,
                    sample.get("instruction", ""),
                    sample.get("input", ""),
                    sample.get("output", "")
                )
                
            # Simulated forward pass
            if hasattr(self.model, "generate"):
                # Generate and compute pseudo-loss
                _ = self.model.generate(text[:100])
                
            # Simulated loss (decreasing over time)
            step_loss = random.uniform(0.5, 1.5) * (1.0 / (1 + len(self.training_history) * 0.1))
            loss += step_loss
            
        return loss / max(1, len(batch))
        
    def _evaluate(self, val_data: List[Dict]) -> float:
        """Evaluate on validation data."""
        if not val_data:
            return 0.0
            
        total_loss = 0.0
        for sample in val_data:
            # Simulated evaluation
            import random
            total_loss += random.uniform(0.3, 0.8)
            
        return total_loss / len(val_data)
        
    def _save_checkpoint(self, step: int, epoch: int, loss: float) -> FineTuneCheckpoint:
        """Save a training checkpoint."""
        checkpoint_id = f"checkpoint_step{step}"
        checkpoint_path = os.path.join(self.config.output_dir, checkpoint_id)
        
        # Create output directory if needed
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        # Save checkpoint metadata
        checkpoint = FineTuneCheckpoint(
            checkpoint_id=checkpoint_id,
            step=step,
            epoch=epoch,
            loss=loss,
            eval_loss=None,
            path=checkpoint_path
        )
        
        # Save checkpoint data
        checkpoint_data = {
            **checkpoint.to_dict(),
            "config": self.config.to_dict()
        }
        
        with open(f"{checkpoint_path}_meta.json", "w") as f:
            json.dump(checkpoint_data, f, indent=2)
            
        # Save LoRA adapter if using LoRA
        if self.lora_adapter:
            self.lora_adapter.save(f"{checkpoint_path}_lora.json")
            
        return checkpoint
        
    def _save_model(self) -> str:
        """Save the fine-tuned model."""
        model_path = os.path.join(self.config.output_dir, "final_model")
        os.makedirs(model_path, exist_ok=True)
        
        # Save training history
        with open(os.path.join(model_path, "training_history.json"), "w") as f:
            json.dump(self.training_history, f, indent=2)
            
        # Save config
        with open(os.path.join(model_path, "config.json"), "w") as f:
            json.dump(self.config.to_dict(), f, indent=2)
            
        # Save LoRA adapter
        if self.lora_adapter:
            self.lora_adapter.save(os.path.join(model_path, "lora_adapter.json"))
            
        return model_path
        
    def load_checkpoint(self, checkpoint_path: str):
        """Load a checkpoint."""
        meta_path = f"{checkpoint_path}_meta.json"
        
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                data = json.load(f)
                print(f"[FineTuner] Loaded checkpoint from step {data['step']}")
                
        if self.lora_adapter:
            lora_path = f"{checkpoint_path}_lora.json"
            if os.path.exists(lora_path):
                self.lora_adapter.load(lora_path)
                
    def get_status(self) -> Dict:
        """Get fine-tuning status."""
        return {
            "is_training": self.is_training,
            "config": self.config.to_dict(),
            "dataset_size": self.dataset.size if self.dataset else 0,
            "checkpoints": len(self.checkpoints),
            "history_length": len(self.training_history),
            "has_lora": self.lora_adapter is not None
        }


class DomainAdapter:
    """
    Adapts models to specific domains.
    
    Creates domain-specific fine-tuned versions of models
    for improved performance in specialized areas.
    """
    
    DOMAINS = {
        "medical": {
            "keywords": ["diagnosis", "treatment", "symptoms", "patient", "medical"],
            "style": "precise, clinical, evidence-based"
        },
        "legal": {
            "keywords": ["law", "regulation", "contract", "rights", "legal"],
            "style": "formal, precise, citing precedents"
        },
        "technical": {
            "keywords": ["code", "algorithm", "system", "implement", "technical"],
            "style": "detailed, step-by-step, practical"
        },
        "creative": {
            "keywords": ["story", "imagine", "create", "artistic", "creative"],
            "style": "expressive, imaginative, engaging"
        },
        "customer_service": {
            "keywords": ["help", "support", "issue", "resolve", "assist"],
            "style": "empathetic, solution-oriented, professional"
        }
    }
    
    def __init__(self, base_model: Any):
        self.base_model = base_model
        self.domain_models: Dict[str, FineTuner] = {}
        self.domain_datasets: Dict[str, FineTuneDataset] = {}
        
    def create_domain_dataset(self, domain: str) -> FineTuneDataset:
        """Create a dataset for a domain."""
        if domain not in self.DOMAINS:
            raise ValueError(f"Unknown domain: {domain}")
            
        dataset = FineTuneDataset(f"{domain}_domain")
        self.domain_datasets[domain] = dataset
        
        return dataset
        
    def adapt_to_domain(
        self,
        domain: str,
        dataset: FineTuneDataset = None,
        config: FineTuneConfig = None
    ) -> FineTuneResult:
        """Adapt model to a specific domain."""
        if domain not in self.DOMAINS:
            raise ValueError(f"Unknown domain: {domain}")
            
        dataset = dataset or self.domain_datasets.get(domain)
        if not dataset or dataset.size == 0:
            raise ValueError(f"No dataset available for domain: {domain}")
            
        config = config or FineTuneConfig(
            method=FineTuneMethod.LORA,
            adaptation_type=AdaptationType.DOMAIN_SPECIFIC,
            epochs=3,
            output_dir=f"domain_models/{domain}"
        )
        
        fine_tuner = FineTuner(self.base_model, config)
        fine_tuner.set_dataset(dataset)
        
        result = fine_tuner.fine_tune()
        
        if result.success:
            self.domain_models[domain] = fine_tuner
            
        return result
        
    def detect_domain(self, text: str) -> str:
        """Detect the domain of input text."""
        text_lower = text.lower()
        domain_scores = {}
        
        for domain, info in self.DOMAINS.items():
            score = sum(1 for kw in info["keywords"] if kw in text_lower)
            if score > 0:
                domain_scores[domain] = score
                
        if domain_scores:
            return max(domain_scores.keys(), key=lambda k: domain_scores[k])
        return "general"
        
    def get_model_for_domain(self, domain: str) -> Any:
        """Get the model adapted for a domain."""
        if domain in self.domain_models:
            return self.domain_models[domain].model
        return self.base_model
        
    def get_status(self) -> Dict:
        return {
            "base_model": str(type(self.base_model)),
            "adapted_domains": list(self.domain_models.keys()),
            "available_datasets": {k: v.size for k, v in self.domain_datasets.items()}
        }


# =============================================================================
# Convenience Functions
# =============================================================================

def create_fine_tuner(
    model: Any,
    method: str = "lora",
    epochs: int = 3
) -> FineTuner:
    """Create a fine-tuner with common configuration."""
    config = FineTuneConfig(
        method=FineTuneMethod(method),
        epochs=epochs
    )
    return FineTuner(model, config)


def create_instruction_dataset(name: str = "instructions") -> FineTuneDataset:
    """Create a dataset for instruction fine-tuning."""
    dataset = FineTuneDataset(name)
    
    # Add some example instructions
    examples = [
        ("Summarize the following text.", "The quick brown fox jumps over the lazy dog.", "A fox jumps over a dog."),
        ("Translate to French.", "Hello, how are you?", "Bonjour, comment allez-vous?"),
        ("Explain this concept.", "Machine learning", "Machine learning is a subset of AI where computers learn from data."),
        ("Generate a creative title.", "A story about space exploration", "Among the Stars: A Journey Beyond"),
    ]
    
    for instruction, input_text, output in examples:
        dataset.add_sample(instruction, input_text, output)
        
    return dataset


def create_conversation_dataset(name: str = "conversations") -> FineTuneDataset:
    """Create a dataset for conversation fine-tuning."""
    dataset = FineTuneDataset(name)
    
    conversations = [
        [
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ],
        [
            {"role": "user", "content": "What's the weather like?"},
            {"role": "assistant", "content": "I don't have access to real-time weather data, but I'd be happy to help with other questions!"}
        ],
    ]
    
    for conv in conversations:
        dataset.add_conversation(conv)
        
    return dataset
