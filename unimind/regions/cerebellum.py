# unimind/regions/cerebellum.py
# Cerebellum - Pattern learning, motor control, timing, procedural memory

import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from collections import deque
import json


@dataclass
class MotorProgram:
    """A learned motor/action program."""
    program_id: str
    name: str
    action_sequence: List[Dict[str, Any]]
    timing: List[float]             # Timing for each action (ms)
    total_duration: float
    success_rate: float = 0.5
    execution_count: int = 0
    last_executed: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "program_id": self.program_id,
            "name": self.name,
            "actions": len(self.action_sequence),
            "duration_ms": self.total_duration,
            "success_rate": self.success_rate,
            "execution_count": self.execution_count
        }


@dataclass
class LearnedPattern:
    """A learned input-output pattern."""
    pattern_id: str
    input_pattern: Any
    output_pattern: Any
    strength: float = 0.5
    error_history: List[float] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def update_strength(self, error: float, learning_rate: float = 0.1):
        """Update pattern strength based on error."""
        self.error_history.append(error)
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
            
        # Reduce strength on high error, increase on low error
        if error < 0.3:
            self.strength = min(1.0, self.strength + learning_rate * (1 - error))
        else:
            self.strength = max(0.1, self.strength - learning_rate * error)


@dataclass
class TimingModel:
    """A learned timing model for a task."""
    task_id: str
    expected_duration_ms: float
    variance_ms: float
    samples: List[float] = field(default_factory=list)
    
    def update(self, actual_duration: float):
        """Update timing model with new sample."""
        self.samples.append(actual_duration)
        if len(self.samples) > 50:
            self.samples = self.samples[-50:]
            
        # Update expected duration (moving average)
        self.expected_duration_ms = sum(self.samples) / len(self.samples)
        
        # Update variance
        if len(self.samples) > 1:
            mean = self.expected_duration_ms
            self.variance_ms = sum((x - mean) ** 2 for x in self.samples) / len(self.samples)


class Cerebellum:
    """
    Cerebellum module - Motor learning and coordination.
    
    Responsible for:
    - Motor program learning and execution
    - Timing and coordination
    - Error-based learning
    - Pattern-to-pattern associations
    - Procedural memory
    - Sensory prediction
    """
    
    def __init__(self, neural_bus=None):
        self.neural_bus = neural_bus
        
        # Motor programs (procedural memory)
        self.motor_programs: Dict[str, MotorProgram] = {}
        
        # Learned patterns (associative)
        self.patterns: Dict[str, LearnedPattern] = {}
        
        # Timing models
        self.timing_models: Dict[str, TimingModel] = {}
        
        # Error signals for learning
        self.error_buffer: deque = deque(maxlen=100)
        
        # Prediction models
        self.predictions: Dict[str, Any] = {}
        
        # Learning parameters
        self.learning_rate = 0.1
        self.error_threshold = 0.3
        
        # Capabilities
        self.capabilities = [
            "motor_learning", "pattern_learning", "timing",
            "coordination", "procedural_memory", "prediction"
        ]
        
        # Register with neural bus
        if self.neural_bus:
            self._register_with_bus()
            
        print("[Cerebellum] Motor learning initialized.")
        
    def _register_with_bus(self):
        """Register with neural bus."""
        self.neural_bus.register_region(
            region_id="cerebellum",
            name="Cerebellum",
            module_type="subcortical",
            capabilities=self.capabilities,
            handler=self._handle_signal
        )
        
    def _handle_signal(self, signal) -> Optional[Any]:
        """Handle incoming neural signals."""
        from unimind.neural_bus import NeuralSignal, SignalType
        
        payload = signal.payload
        
        if signal.signal_type == SignalType.QUERY:
            capability = payload.get("capability")
            if capability == "motor_learning":
                return self._handle_motor_query(payload.get("data", {}))
            elif capability == "pattern_learning":
                return self._handle_pattern_query(payload.get("data", {}))
                
        elif signal.signal_type == SignalType.MODULATORY:
            if "error" in payload:
                self.process_error(payload["error"], payload.get("source", "unknown"))
                
        return None
        
    def _handle_motor_query(self, data: Dict) -> Any:
        """Handle motor learning queries."""
        from unimind.neural_bus import NeuralSignal, SignalType
        
        if "execute" in data:
            result = self.execute_program(data["execute"])
            return NeuralSignal(
                signal_id=f"cereb_exec",
                signal_type=SignalType.RESPONSE,
                source="cerebellum",
                target=None,
                payload={"execution": result}
            )
        elif "learn" in data:
            program = self.learn_motor_program(
                name=data["learn"].get("name", "unnamed"),
                actions=data["learn"].get("actions", [])
            )
            return NeuralSignal(
                signal_id=f"cereb_learn",
                signal_type=SignalType.RESPONSE,
                source="cerebellum",
                target=None,
                payload={"program": program.to_dict()}
            )
        return None
        
    def _handle_pattern_query(self, data: Dict) -> Any:
        """Handle pattern learning queries."""
        if "associate" in data:
            self.learn_pattern(
                input_pattern=data["associate"].get("input"),
                output_pattern=data["associate"].get("output")
            )
        elif "predict" in data:
            output = self.predict(data["predict"])
            return output
        return None
        
    def learn_motor_program(
        self,
        name: str,
        actions: List[Dict[str, Any]],
        timing: List[float] = None
    ) -> MotorProgram:
        """
        Learn a new motor program (action sequence).
        
        Args:
            name: Program name
            actions: List of action definitions
            timing: Optional timing for each action
            
        Returns:
            Created MotorProgram
        """
        program_id = f"motor_{int(time.time() * 1000)}"
        
        # Default timing if not provided
        if timing is None:
            timing = [100.0] * len(actions)  # 100ms per action default
            
        program = MotorProgram(
            program_id=program_id,
            name=name,
            action_sequence=actions,
            timing=timing,
            total_duration=sum(timing)
        )
        
        self.motor_programs[program_id] = program
        
        # Create timing model
        self.timing_models[program_id] = TimingModel(
            task_id=program_id,
            expected_duration_ms=sum(timing),
            variance_ms=0.0
        )
        
        print(f"[Cerebellum] Learned motor program: {name} ({len(actions)} actions)")
        return program
        
    def execute_program(self, program_id: str) -> Optional[Dict]:
        """
        Execute a motor program.
        
        Args:
            program_id: ID of program to execute
            
        Returns:
            Execution result
        """
        program = self.motor_programs.get(program_id)
        if not program:
            return None
            
        start_time = time.time()
        results = []
        
        for i, (action, timing_ms) in enumerate(zip(program.action_sequence, program.timing)):
            # In a real system, this would dispatch to actual motor systems
            result = {
                "step": i,
                "action": action,
                "expected_timing": timing_ms,
                "status": "executed"
            }
            results.append(result)
            
        # Update execution stats
        program.execution_count += 1
        program.last_executed = datetime.now().isoformat()
        
        # Update timing model
        actual_duration = (time.time() - start_time) * 1000
        if program_id in self.timing_models:
            self.timing_models[program_id].update(actual_duration)
            
        return {
            "program_id": program_id,
            "name": program.name,
            "steps_executed": len(results),
            "duration_ms": actual_duration
        }
        
    def refine_program(self, program_id: str, error_signal: float, step_index: int = None):
        """
        Refine a motor program based on error signal.
        
        Args:
            program_id: Program to refine
            error_signal: Error magnitude
            step_index: Which step had the error (if known)
        """
        program = self.motor_programs.get(program_id)
        if not program:
            return
            
        # Adjust timing based on error
        if step_index is not None and step_index < len(program.timing):
            # Adjust specific step timing
            adjustment = error_signal * 10  # ms adjustment
            program.timing[step_index] += adjustment
        else:
            # General refinement
            program.success_rate = (program.success_rate * 0.9 + 
                                    (1 - error_signal) * 0.1)
            
        self.error_buffer.append({
            "program_id": program_id,
            "error": error_signal,
            "timestamp": datetime.now().isoformat()
        })
        
    def learn_pattern(
        self,
        input_pattern: Any,
        output_pattern: Any,
        initial_strength: float = 0.5
    ) -> LearnedPattern:
        """
        Learn an input-output pattern association.
        
        Args:
            input_pattern: Input pattern
            output_pattern: Expected output
            initial_strength: Starting strength
            
        Returns:
            Created LearnedPattern
        """
        pattern_id = f"pat_{hash(str(input_pattern)) % 10000}_{int(time.time())}"
        
        pattern = LearnedPattern(
            pattern_id=pattern_id,
            input_pattern=input_pattern,
            output_pattern=output_pattern,
            strength=initial_strength
        )
        
        self.patterns[pattern_id] = pattern
        
        print(f"[Cerebellum] Learned pattern: {pattern_id}")
        return pattern
        
    def predict(self, input_pattern: Any) -> Optional[Tuple[Any, float]]:
        """
        Predict output for an input pattern.
        
        Args:
            input_pattern: Input to predict from
            
        Returns:
            Tuple of (predicted_output, confidence) or None
        """
        best_match = None
        best_similarity = 0.0
        
        input_str = str(input_pattern).lower()
        
        for pattern in self.patterns.values():
            # Simple string similarity
            pattern_str = str(pattern.input_pattern).lower()
            
            # Calculate similarity
            common = len(set(input_str.split()) & set(pattern_str.split()))
            total = len(set(input_str.split()) | set(pattern_str.split()))
            
            if total > 0:
                similarity = common / total * pattern.strength
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = pattern
                    
        if best_match and best_similarity > 0.3:
            return (best_match.output_pattern, best_similarity)
            
        return None
        
    def process_error(self, error_signal: float, source: str):
        """
        Process an error signal for learning.
        
        Args:
            error_signal: Error magnitude (0-1)
            source: Source of the error
        """
        self.error_buffer.append({
            "error": error_signal,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update patterns associated with source
        for pattern in self.patterns.values():
            if source in str(pattern.input_pattern):
                pattern.update_strength(error_signal, self.learning_rate)
                
        # Broadcast error for system-wide learning
        if self.neural_bus and error_signal > self.error_threshold:
            self.neural_bus.emit(
                source="cerebellum",
                signal_type="modulatory",
                payload={"error_signal": error_signal, "origin": source},
                priority="normal"
            )
            
    def get_timing_prediction(self, task_id: str) -> Optional[Tuple[float, float]]:
        """
        Get predicted timing for a task.
        
        Returns:
            Tuple of (expected_ms, variance_ms) or None
        """
        model = self.timing_models.get(task_id)
        if model:
            return (model.expected_duration_ms, model.variance_ms)
        return None
        
    def record_timing(self, task_id: str, actual_duration_ms: float):
        """Record actual timing for a task."""
        if task_id not in self.timing_models:
            self.timing_models[task_id] = TimingModel(
                task_id=task_id,
                expected_duration_ms=actual_duration_ms,
                variance_ms=0.0
            )
        else:
            self.timing_models[task_id].update(actual_duration_ms)
            
    def get_average_error(self) -> float:
        """Get average recent error."""
        if not self.error_buffer:
            return 0.0
        errors = [e["error"] for e in self.error_buffer]
        return sum(errors) / len(errors)
        
    def consolidate_programs(self) -> int:
        """
        Consolidate motor programs - strengthen successful ones, weaken poor ones.
        
        Returns:
            Number of programs modified
        """
        modified = 0
        
        for program in self.motor_programs.values():
            if program.execution_count > 5:
                if program.success_rate > 0.8:
                    # Strengthen successful program
                    program.success_rate = min(1.0, program.success_rate * 1.05)
                    modified += 1
                elif program.success_rate < 0.3:
                    # Weaken unsuccessful program
                    program.success_rate *= 0.9
                    modified += 1
                    
        return modified
        
    def get_status(self) -> Dict[str, Any]:
        """Get cerebellum status."""
        return {
            "motor_programs": len(self.motor_programs),
            "patterns": len(self.patterns),
            "timing_models": len(self.timing_models),
            "error_buffer_size": len(self.error_buffer),
            "average_error": self.get_average_error(),
            "learning_rate": self.learning_rate
        }
