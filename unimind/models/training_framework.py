# unimind/models/training_framework.py
# Cognitive Model Training Framework

import json
import time
import random
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import threading
from collections import defaultdict


class TrainingMode(Enum):
    """Training modes."""
    SUPERVISED = "supervised"
    REINFORCEMENT = "reinforcement"
    IMITATION = "imitation"
    CONTRASTIVE = "contrastive"
    CURRICULUM = "curriculum"
    SELF_PLAY = "self_play"
    HUMAN_FEEDBACK = "human_feedback"


class DatasetType(Enum):
    """Dataset types."""
    CONVERSATION = "conversation"
    QA = "qa"
    REASONING = "reasoning"
    CODE = "code"
    CREATIVE = "creative"
    FACTUAL = "factual"
    EMOTIONAL = "emotional"
    TASK_COMPLETION = "task_completion"


@dataclass
class TrainingSample:
    """A single training sample."""
    input_text: str
    target_output: str
    sample_type: DatasetType
    metadata: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    difficulty: float = 0.5  # 0.0 = easy, 1.0 = hard
    feedback_score: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "input": self.input_text,
            "output": self.target_output,
            "type": self.sample_type.value,
            "weight": self.weight,
            "difficulty": self.difficulty,
            "feedback": self.feedback_score
        }


@dataclass
class TrainingBatch:
    """A batch of training samples."""
    samples: List[TrainingSample]
    batch_id: str
    epoch: int = 0
    
    @property
    def size(self) -> int:
        return len(self.samples)
        
    def get_average_difficulty(self) -> float:
        if not self.samples:
            return 0.0
        return sum(s.difficulty for s in self.samples) / len(self.samples)


@dataclass
class TrainingMetrics:
    """Training metrics and statistics."""
    loss: float = 0.0
    accuracy: float = 0.0
    samples_processed: int = 0
    epochs_completed: int = 0
    training_time_seconds: float = 0.0
    validation_score: float = 0.0
    best_score: float = 0.0
    improvement_rate: float = 0.0
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    
    def update(self, new_loss: float, new_accuracy: float, samples: int):
        """Update metrics with new values."""
        self.loss = new_loss
        self.accuracy = new_accuracy
        self.samples_processed += samples
        
    def to_dict(self) -> Dict:
        return {
            "loss": self.loss,
            "accuracy": self.accuracy,
            "samples_processed": self.samples_processed,
            "epochs_completed": self.epochs_completed,
            "training_time": self.training_time_seconds,
            "validation_score": self.validation_score,
            "best_score": self.best_score
        }


class TrainingDataset:
    """
    Manages training data for cognitive models.
    
    Supports:
    - Multiple data types
    - Difficulty-based curriculum
    - Data augmentation
    - Active learning selection
    """
    
    def __init__(self, name: str):
        self.name = name
        self.samples: List[TrainingSample] = []
        self.samples_by_type: Dict[DatasetType, List[TrainingSample]] = defaultdict(list)
        self.validation_samples: List[TrainingSample] = []
        
    def add_sample(
        self,
        input_text: str,
        target_output: str,
        sample_type: DatasetType = DatasetType.CONVERSATION,
        difficulty: float = 0.5,
        weight: float = 1.0,
        is_validation: bool = False
    ) -> TrainingSample:
        """Add a training sample."""
        sample = TrainingSample(
            input_text=input_text,
            target_output=target_output,
            sample_type=sample_type,
            weight=weight,
            difficulty=difficulty
        )
        
        if is_validation:
            self.validation_samples.append(sample)
        else:
            self.samples.append(sample)
            self.samples_by_type[sample_type].append(sample)
            
        return sample
        
    def add_conversation_pair(
        self,
        user_message: str,
        assistant_response: str,
        difficulty: float = 0.5
    ):
        """Add a conversation pair."""
        self.add_sample(
            input_text=user_message,
            target_output=assistant_response,
            sample_type=DatasetType.CONVERSATION,
            difficulty=difficulty
        )
        
    def add_qa_pair(
        self,
        question: str,
        answer: str,
        difficulty: float = 0.5
    ):
        """Add a QA pair."""
        self.add_sample(
            input_text=question,
            target_output=answer,
            sample_type=DatasetType.QA,
            difficulty=difficulty
        )
        
    def add_reasoning_example(
        self,
        problem: str,
        reasoning_steps: str,
        difficulty: float = 0.7
    ):
        """Add a reasoning example with chain-of-thought."""
        self.add_sample(
            input_text=problem,
            target_output=reasoning_steps,
            sample_type=DatasetType.REASONING,
            difficulty=difficulty
        )
        
    def get_batch(
        self,
        batch_size: int,
        sample_type: Optional[DatasetType] = None,
        difficulty_range: Tuple[float, float] = (0.0, 1.0)
    ) -> TrainingBatch:
        """Get a batch of training samples."""
        # Filter samples
        source = self.samples_by_type[sample_type] if sample_type else self.samples
        filtered = [
            s for s in source
            if difficulty_range[0] <= s.difficulty <= difficulty_range[1]
        ]
        
        if not filtered:
            filtered = source
            
        # Sample with weights
        weights = [s.weight for s in filtered]
        total_weight = sum(weights)
        probs = [w / total_weight for w in weights]
        
        batch_samples = []
        indices = list(range(len(filtered)))
        
        for _ in range(min(batch_size, len(filtered))):
            idx = random.choices(indices, weights=probs, k=1)[0]
            batch_samples.append(filtered[idx])
            
        return TrainingBatch(
            samples=batch_samples,
            batch_id=f"batch_{int(time.time())}_{random.randint(1000, 9999)}"
        )
        
    def get_curriculum_batch(
        self,
        batch_size: int,
        current_skill_level: float
    ) -> TrainingBatch:
        """Get a curriculum-based batch matching skill level."""
        # Target difficulty slightly above current skill
        target_difficulty = min(1.0, current_skill_level + 0.1)
        margin = 0.2
        
        return self.get_batch(
            batch_size=batch_size,
            difficulty_range=(target_difficulty - margin, target_difficulty + margin)
        )
        
    def augment_sample(self, sample: TrainingSample) -> List[TrainingSample]:
        """Augment a sample to create variations."""
        augmented = []
        
        # Paraphrase-style augmentation (simple version)
        variations = [
            (sample.input_text.replace(".", "?"), sample.target_output),
            (f"Please {sample.input_text.lower()}", sample.target_output),
            (f"Can you {sample.input_text.lower()}", sample.target_output),
        ]
        
        for inp, out in variations:
            if inp != sample.input_text:
                augmented.append(TrainingSample(
                    input_text=inp,
                    target_output=out,
                    sample_type=sample.sample_type,
                    difficulty=sample.difficulty,
                    weight=sample.weight * 0.8  # Lower weight for augmented
                ))
                
        return augmented
        
    def save(self, path: str):
        """Save dataset to file."""
        data = {
            "name": self.name,
            "samples": [s.to_dict() for s in self.samples],
            "validation": [s.to_dict() for s in self.validation_samples]
        }
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
            
    def load(self, path: str):
        """Load dataset from file."""
        with open(path) as f:
            data = json.load(f)
            
        self.name = data.get("name", self.name)
        
        for s in data.get("samples", []):
            self.add_sample(
                input_text=s["input"],
                target_output=s["output"],
                sample_type=DatasetType(s.get("type", "conversation")),
                difficulty=s.get("difficulty", 0.5),
                weight=s.get("weight", 1.0)
            )
            
    @property
    def size(self) -> int:
        return len(self.samples)
        
    def get_stats(self) -> Dict:
        """Get dataset statistics."""
        return {
            "name": self.name,
            "total_samples": len(self.samples),
            "validation_samples": len(self.validation_samples),
            "samples_by_type": {k.value: len(v) for k, v in self.samples_by_type.items()},
            "avg_difficulty": sum(s.difficulty for s in self.samples) / len(self.samples) if self.samples else 0
        }


class RewardModel:
    """
    Model for scoring outputs in reinforcement learning.
    
    Used for:
    - RLHF (Reinforcement Learning from Human Feedback)
    - Self-evaluation
    - Preference learning
    """
    
    def __init__(self):
        self.feedback_history: List[Dict] = []
        self.preference_pairs: List[Tuple[str, str, int]] = []  # (better, worse, margin)
        self.learned_preferences: Dict[str, float] = {}
        
    def score_output(self, input_text: str, output: str) -> float:
        """Score an output for a given input."""
        score = 0.5  # Base score
        
        # Length-based heuristics
        if len(output) < 10:
            score -= 0.1
        elif len(output) > 500:
            score += 0.1
            
        # Keyword matching
        input_words = set(input_text.lower().split())
        output_words = set(output.lower().split())
        relevance = len(input_words & output_words) / len(input_words) if input_words else 0
        score += relevance * 0.2
        
        # Check for reasoning indicators
        reasoning_markers = ["because", "therefore", "first", "then", "finally", "step"]
        if any(m in output.lower() for m in reasoning_markers):
            score += 0.1
            
        # Check learned preferences
        for key, pref_score in self.learned_preferences.items():
            if key in output.lower():
                score += pref_score * 0.05
                
        return max(0.0, min(1.0, score))
        
    def add_human_feedback(
        self,
        input_text: str,
        output: str,
        rating: float,  # 0-1 scale
        feedback_text: str = ""
    ):
        """Add human feedback for an output."""
        self.feedback_history.append({
            "input": input_text,
            "output": output,
            "rating": rating,
            "feedback": feedback_text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Learn from feedback
        words = output.lower().split()
        if rating > 0.7:
            for word in words:
                self.learned_preferences[word] = self.learned_preferences.get(word, 0) + 0.01
        elif rating < 0.3:
            for word in words:
                self.learned_preferences[word] = self.learned_preferences.get(word, 0) - 0.01
                
    def add_preference_pair(
        self,
        input_text: str,
        better_output: str,
        worse_output: str,
        margin: int = 1
    ):
        """Add a preference comparison pair."""
        self.preference_pairs.append((better_output, worse_output, margin))
        
    def get_preference_score(self, output1: str, output2: str, input_text: str = "") -> int:
        """Compare two outputs and return preference (-1, 0, 1)."""
        score1 = self.score_output(input_text, output1)
        score2 = self.score_output(input_text, output2)
        
        if abs(score1 - score2) < 0.1:
            return 0
        return 1 if score1 > score2 else -1
        
    def get_stats(self) -> Dict:
        return {
            "feedback_count": len(self.feedback_history),
            "preference_pairs": len(self.preference_pairs),
            "learned_preferences": len(self.learned_preferences)
        }


@dataclass
class TrainingConfig:
    """Configuration for training."""
    mode: TrainingMode = TrainingMode.SUPERVISED
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 0.001
    validation_split: float = 0.1
    early_stopping_patience: int = 3
    curriculum_enabled: bool = False
    curriculum_start_difficulty: float = 0.3
    augmentation_enabled: bool = False
    save_checkpoints: bool = True
    checkpoint_interval: int = 1000


class CognitiveTrainer:
    """
    Main trainer for cognitive models.
    
    Features:
    - Multiple training modes
    - Curriculum learning
    - Human feedback integration
    - Checkpoint management
    - Progress tracking
    """
    
    def __init__(self, model_interface: Any, config: TrainingConfig = None):
        self.model = model_interface
        self.config = config or TrainingConfig()
        self.dataset: Optional[TrainingDataset] = None
        self.reward_model = RewardModel()
        self.metrics = TrainingMetrics()
        self.training_history: List[Dict] = []
        self.is_training = False
        self.should_stop = False
        self.current_difficulty = self.config.curriculum_start_difficulty
        
    def set_dataset(self, dataset: TrainingDataset):
        """Set the training dataset."""
        self.dataset = dataset
        print(f"[CognitiveTrainer] Dataset set: {dataset.name} ({dataset.size} samples)")
        
    def train_step(self, batch: TrainingBatch) -> Dict[str, float]:
        """Execute a single training step."""
        total_loss = 0.0
        correct = 0
        
        for sample in batch.samples:
            # Generate model output
            if hasattr(self.model, 'generate'):
                output = self.model.generate(sample.input_text)
            else:
                output = str(self.model.process(sample.input_text))
                
            # Calculate pseudo-loss (similarity to target)
            similarity = self._calculate_similarity(output, sample.target_output)
            loss = 1.0 - similarity
            total_loss += loss
            
            if similarity > 0.7:
                correct += 1
                
            # Update reward model
            if self.config.mode == TrainingMode.REINFORCEMENT:
                reward = self.reward_model.score_output(sample.input_text, output)
                sample.feedback_score = reward
                
        avg_loss = total_loss / batch.size if batch.size > 0 else 0
        accuracy = correct / batch.size if batch.size > 0 else 0
        
        return {
            "loss": avg_loss,
            "accuracy": accuracy,
            "batch_size": batch.size
        }
        
    def _calculate_similarity(self, output: str, target: str) -> float:
        """Calculate similarity between output and target."""
        output_words = set(output.lower().split())
        target_words = set(target.lower().split())
        
        if not target_words:
            return 0.0
            
        intersection = output_words & target_words
        union = output_words | target_words
        
        return len(intersection) / len(union) if union else 0.0
        
    def train(
        self,
        epochs: Optional[int] = None,
        callbacks: List[Callable] = None
    ) -> TrainingMetrics:
        """
        Run training loop.
        
        Args:
            epochs: Number of epochs (overrides config)
            callbacks: List of callback functions called each epoch
            
        Returns:
            Final training metrics
        """
        if self.dataset is None:
            raise ValueError("No dataset set. Call set_dataset() first.")
            
        epochs = epochs or self.config.epochs
        callbacks = callbacks or []
        
        self.is_training = True
        self.should_stop = False
        start_time = time.time()
        
        print(f"[CognitiveTrainer] Starting training: {epochs} epochs, {self.dataset.size} samples")
        
        best_score = 0.0
        patience_counter = 0
        
        for epoch in range(epochs):
            if self.should_stop:
                break
                
            epoch_loss = 0.0
            epoch_accuracy = 0.0
            batches_processed = 0
            
            # Get batches based on training mode
            samples_remaining = list(self.dataset.samples)
            random.shuffle(samples_remaining)
            
            while samples_remaining:
                # Get batch
                batch_samples = samples_remaining[:self.config.batch_size]
                samples_remaining = samples_remaining[self.config.batch_size:]
                
                if self.config.curriculum_enabled:
                    batch = self.dataset.get_curriculum_batch(
                        self.config.batch_size,
                        self.current_difficulty
                    )
                else:
                    batch = TrainingBatch(
                        samples=batch_samples,
                        batch_id=f"epoch{epoch}_{batches_processed}",
                        epoch=epoch
                    )
                    
                # Training step
                step_result = self.train_step(batch)
                epoch_loss += step_result["loss"]
                epoch_accuracy += step_result["accuracy"]
                batches_processed += 1
                
            # Epoch metrics
            avg_loss = epoch_loss / batches_processed if batches_processed > 0 else 0
            avg_accuracy = epoch_accuracy / batches_processed if batches_processed > 0 else 0
            
            self.metrics.update(avg_loss, avg_accuracy, self.config.batch_size * batches_processed)
            self.metrics.epochs_completed = epoch + 1
            
            # Validation
            val_score = self._validate()
            self.metrics.validation_score = val_score
            
            # Track best
            if val_score > best_score:
                best_score = val_score
                self.metrics.best_score = best_score
                patience_counter = 0
            else:
                patience_counter += 1
                
            # Update curriculum difficulty
            if self.config.curriculum_enabled and avg_accuracy > 0.8:
                self.current_difficulty = min(1.0, self.current_difficulty + 0.05)
                
            # Record history
            epoch_record = {
                "epoch": epoch + 1,
                "loss": avg_loss,
                "accuracy": avg_accuracy,
                "validation": val_score,
                "difficulty": self.current_difficulty
            }
            self.training_history.append(epoch_record)
            
            print(f"  Epoch {epoch + 1}/{epochs}: loss={avg_loss:.4f}, acc={avg_accuracy:.4f}, val={val_score:.4f}")
            
            # Callbacks
            for cb in callbacks:
                cb(epoch_record)
                
            # Early stopping
            if patience_counter >= self.config.early_stopping_patience:
                print(f"[CognitiveTrainer] Early stopping at epoch {epoch + 1}")
                break
                
        self.metrics.training_time_seconds = time.time() - start_time
        self.is_training = False
        
        print(f"[CognitiveTrainer] Training complete: {self.metrics.epochs_completed} epochs, best={best_score:.4f}")
        
        return self.metrics
        
    def _validate(self) -> float:
        """Run validation and return score."""
        if not self.dataset.validation_samples:
            return 0.0
            
        correct = 0
        for sample in self.dataset.validation_samples:
            if hasattr(self.model, 'generate'):
                output = self.model.generate(sample.input_text)
            else:
                output = str(self.model.process(sample.input_text))
                
            similarity = self._calculate_similarity(output, sample.target_output)
            if similarity > 0.7:
                correct += 1
                
        return correct / len(self.dataset.validation_samples)
        
    def train_from_feedback(
        self,
        input_text: str,
        output: str,
        rating: float,
        feedback_text: str = ""
    ):
        """Train from human feedback on a single example."""
        self.reward_model.add_human_feedback(input_text, output, rating, feedback_text)
        
        # Add as training sample if rating is high
        if rating > 0.7 and self.dataset:
            self.dataset.add_sample(
                input_text=input_text,
                target_output=output,
                sample_type=DatasetType.CONVERSATION,
                weight=rating
            )
            
    def stop_training(self):
        """Signal to stop training."""
        self.should_stop = True
        
    def get_status(self) -> Dict:
        """Get training status."""
        return {
            "is_training": self.is_training,
            "metrics": self.metrics.to_dict(),
            "current_difficulty": self.current_difficulty,
            "dataset_size": self.dataset.size if self.dataset else 0,
            "history_length": len(self.training_history),
            "reward_model_stats": self.reward_model.get_stats()
        }


class DatasetBuilder:
    """Helper for building training datasets."""
    
    @staticmethod
    def create_conversation_dataset(name: str = "conversation") -> TrainingDataset:
        """Create a dataset for conversation training."""
        ds = TrainingDataset(name)
        
        # Add some built-in conversation pairs
        conversations = [
            ("Hello", "Hello! How can I help you today?", 0.2),
            ("What's your name?", "I'm an AI assistant. How can I assist you?", 0.3),
            ("Can you help me?", "Of course! What do you need help with?", 0.3),
            ("Tell me a joke", "Why did the AI go to therapy? It had too many issues to process!", 0.4),
            ("How does machine learning work?", "Machine learning involves training models on data to recognize patterns and make predictions. The model learns from examples rather than being explicitly programmed.", 0.6),
            ("Explain recursion", "Recursion is when a function calls itself. To understand recursion, you must first understand recursion. It's useful for problems that can be broken into smaller, similar sub-problems.", 0.7),
        ]
        
        for user_msg, response, difficulty in conversations:
            ds.add_conversation_pair(user_msg, response, difficulty)
            
        return ds
        
    @staticmethod
    def create_reasoning_dataset(name: str = "reasoning") -> TrainingDataset:
        """Create a dataset for reasoning training."""
        ds = TrainingDataset(name)
        
        reasoning_examples = [
            (
                "If all cats are animals, and Fluffy is a cat, what is Fluffy?",
                "Let me reason through this:\n1. Premise: All cats are animals\n2. Premise: Fluffy is a cat\n3. By logical inference, since Fluffy belongs to the category 'cats', and all cats are animals\n4. Therefore: Fluffy is an animal",
                0.4
            ),
            (
                "What comes next: 2, 4, 8, 16, ?",
                "Analyzing the pattern:\n1. Looking at differences: 4-2=2, 8-4=4, 16-8=8\n2. The differences are doubling: 2, 4, 8\n3. Each number is 2x the previous\n4. 16 × 2 = 32\nAnswer: 32",
                0.5
            ),
            (
                "Should I bring an umbrella if there's a 60% chance of rain?",
                "Decision analysis:\n1. Probability of rain: 60% (more likely than not)\n2. Cost of bringing umbrella: Minor inconvenience\n3. Cost of getting wet: Discomfort, wet clothes, potential illness\n4. Expected value calculation favors bringing umbrella\nRecommendation: Yes, bring an umbrella. The probability is significant enough that the protection outweighs the inconvenience.",
                0.6
            ),
        ]
        
        for problem, reasoning, difficulty in reasoning_examples:
            ds.add_reasoning_example(problem, reasoning, difficulty)
            
        return ds
        
    @staticmethod
    def create_emotional_dataset(name: str = "emotional") -> TrainingDataset:
        """Create a dataset for emotional intelligence training."""
        ds = TrainingDataset(name)
        
        emotional_examples = [
            (
                "I'm feeling really sad today",
                "I'm sorry to hear you're feeling sad. It's okay to have these feelings. Would you like to talk about what's troubling you? I'm here to listen and support you.",
                0.4,
                DatasetType.EMOTIONAL
            ),
            (
                "I just got promoted!",
                "Congratulations! That's wonderful news! You must have worked really hard to earn this. How are you feeling about your new role? I'd love to hear more about it!",
                0.3,
                DatasetType.EMOTIONAL
            ),
            (
                "I'm stressed about my exam",
                "Exam stress is very common, and it's understandable to feel this way. Remember: preparation builds confidence. Would you like me to help you with study strategies or just talk through your concerns?",
                0.5,
                DatasetType.EMOTIONAL
            ),
        ]
        
        for input_text, response, difficulty, sample_type in emotional_examples:
            ds.add_sample(input_text, response, sample_type, difficulty)
            
        return ds


# Convenience function
def create_trainer_with_datasets(model_interface: Any) -> CognitiveTrainer:
    """Create a trainer with pre-built datasets."""
    config = TrainingConfig(
        mode=TrainingMode.CURRICULUM,
        epochs=5,
        batch_size=16,
        curriculum_enabled=True
    )
    
    trainer = CognitiveTrainer(model_interface, config)
    
    # Build combined dataset
    ds = TrainingDataset("cognitive_training")
    
    # Add conversation data
    conv_ds = DatasetBuilder.create_conversation_dataset()
    for sample in conv_ds.samples:
        ds.samples.append(sample)
        ds.samples_by_type[sample.sample_type].append(sample)
        
    # Add reasoning data
    reason_ds = DatasetBuilder.create_reasoning_dataset()
    for sample in reason_ds.samples:
        ds.samples.append(sample)
        ds.samples_by_type[sample.sample_type].append(sample)
        
    # Add emotional data
    emo_ds = DatasetBuilder.create_emotional_dataset()
    for sample in emo_ds.samples:
        ds.samples.append(sample)
        ds.samples_by_type[sample.sample_type].append(sample)
        
    trainer.set_dataset(ds)
    
    return trainer
