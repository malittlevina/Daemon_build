# unimind/models/orchestration.py
# Model Orchestration and Routing System

from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time
import threading
import queue
from collections import defaultdict
import json


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ModelType(Enum):
    """Types of models that can be orchestrated."""
    LLM = "llm"
    NLU = "nlu"
    REASONING = "reasoning"
    CREATIVE = "creative"
    EMOTIONAL = "emotional"
    EMBEDDING = "embedding"
    VISION = "vision"
    SPEECH = "speech"


@dataclass
class ModelTask:
    """A task to be processed by a model."""
    task_id: str
    model_type: ModelType
    input_data: Any
    priority: TaskPriority = TaskPriority.NORMAL
    timeout_ms: int = 30000
    kwargs: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "model_type": self.model_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "processing_time_ms": self.processing_time_ms
        }


@dataclass
class ModelEndpoint:
    """Configuration for a model endpoint."""
    name: str
    model_type: ModelType
    model_instance: Any
    max_concurrent: int = 1
    current_load: int = 0
    total_calls: int = 0
    total_time_ms: float = 0.0
    error_count: int = 0
    is_available: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def average_latency(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.total_time_ms / self.total_calls
        
    @property
    def error_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.error_count / self.total_calls


class RoutingStrategy(Enum):
    """Strategies for routing requests to models."""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    LOWEST_LATENCY = "lowest_latency"
    CAPABILITY_MATCH = "capability_match"
    RANDOM = "random"


@dataclass
class RoutingRule:
    """Rule for routing requests."""
    name: str
    condition: Callable[[ModelTask], bool]
    target_model: str
    priority: int = 0


class ModelRouter:
    """
    Routes requests to appropriate models based on rules and strategies.
    
    Features:
    - Multiple routing strategies
    - Custom routing rules
    - Load balancing
    - Capability-based routing
    """
    
    def __init__(self, strategy: RoutingStrategy = RoutingStrategy.CAPABILITY_MATCH):
        self.strategy = strategy
        self.endpoints: Dict[str, ModelEndpoint] = {}
        self.rules: List[RoutingRule] = []
        self.round_robin_index: Dict[ModelType, int] = defaultdict(int)
        
    def register_endpoint(self, endpoint: ModelEndpoint):
        """Register a model endpoint."""
        self.endpoints[endpoint.name] = endpoint
        print(f"[ModelRouter] Registered endpoint: {endpoint.name} ({endpoint.model_type.value})")
        
    def add_rule(self, rule: RoutingRule):
        """Add a routing rule."""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        
    def route(self, task: ModelTask) -> Optional[ModelEndpoint]:
        """Route a task to an appropriate endpoint."""
        # First check custom rules
        for rule in self.rules:
            if rule.condition(task):
                endpoint = self.endpoints.get(rule.target_model)
                if endpoint and endpoint.is_available:
                    return endpoint
                    
        # Get endpoints of matching type
        matching = [
            e for e in self.endpoints.values()
            if e.model_type == task.model_type and e.is_available
        ]
        
        if not matching:
            return None
            
        # Apply strategy
        if self.strategy == RoutingStrategy.ROUND_ROBIN:
            return self._route_round_robin(matching, task.model_type)
        elif self.strategy == RoutingStrategy.LEAST_LOADED:
            return self._route_least_loaded(matching)
        elif self.strategy == RoutingStrategy.LOWEST_LATENCY:
            return self._route_lowest_latency(matching)
        else:
            return matching[0]
            
    def _route_round_robin(self, endpoints: List[ModelEndpoint], model_type: ModelType) -> ModelEndpoint:
        """Round-robin routing."""
        idx = self.round_robin_index[model_type] % len(endpoints)
        self.round_robin_index[model_type] = idx + 1
        return endpoints[idx]
        
    def _route_least_loaded(self, endpoints: List[ModelEndpoint]) -> ModelEndpoint:
        """Route to least loaded endpoint."""
        return min(endpoints, key=lambda e: e.current_load / max(1, e.max_concurrent))
        
    def _route_lowest_latency(self, endpoints: List[ModelEndpoint]) -> ModelEndpoint:
        """Route to endpoint with lowest average latency."""
        return min(endpoints, key=lambda e: e.average_latency)
        
    def get_status(self) -> Dict:
        """Get router status."""
        return {
            "strategy": self.strategy.value,
            "endpoints": len(self.endpoints),
            "rules": len(self.rules),
            "endpoints_detail": [
                {
                    "name": e.name,
                    "type": e.model_type.value,
                    "available": e.is_available,
                    "load": e.current_load,
                    "avg_latency": e.average_latency
                }
                for e in self.endpoints.values()
            ]
        }


class TaskQueue:
    """Priority queue for model tasks."""
    
    def __init__(self, max_size: int = 1000):
        self.queues: Dict[TaskPriority, queue.Queue] = {
            p: queue.Queue(maxsize=max_size // 5) for p in TaskPriority
        }
        self._lock = threading.Lock()
        self.total_enqueued = 0
        self.total_dequeued = 0
        
    def enqueue(self, task: ModelTask) -> bool:
        """Add a task to the queue."""
        q = self.queues[task.priority]
        try:
            q.put_nowait(task)
            task.status = TaskStatus.QUEUED
            with self._lock:
                self.total_enqueued += 1
            return True
        except queue.Full:
            return False
            
    def dequeue(self, timeout: float = 0.1) -> Optional[ModelTask]:
        """Get the highest priority task."""
        for priority in TaskPriority:
            q = self.queues[priority]
            try:
                task = q.get_nowait()
                with self._lock:
                    self.total_dequeued += 1
                return task
            except queue.Empty:
                continue
        return None
        
    def size(self) -> int:
        """Get total queue size."""
        return sum(q.qsize() for q in self.queues.values())
        
    def get_stats(self) -> Dict:
        return {
            "total_size": self.size(),
            "by_priority": {p.name: self.queues[p].qsize() for p in TaskPriority},
            "total_enqueued": self.total_enqueued,
            "total_dequeued": self.total_dequeued
        }


class ModelPipeline:
    """
    Pipeline for chaining multiple models together.
    
    Allows sequential processing through multiple models
    with transformation between stages.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.stages: List[Tuple[str, Callable]] = []
        self.transformers: List[Callable] = []
        
    def add_stage(
        self,
        model_name: str,
        model_callable: Callable,
        transformer: Callable = None
    ):
        """Add a stage to the pipeline."""
        self.stages.append((model_name, model_callable))
        self.transformers.append(transformer or (lambda x: x))
        
    def execute(self, input_data: Any) -> Dict[str, Any]:
        """Execute the pipeline."""
        results = []
        current_data = input_data
        
        for i, (model_name, model_fn) in enumerate(self.stages):
            start = time.time()
            
            try:
                result = model_fn(current_data)
                elapsed = (time.time() - start) * 1000
                
                results.append({
                    "stage": i + 1,
                    "model": model_name,
                    "success": True,
                    "time_ms": elapsed,
                    "result": result
                })
                
                # Transform for next stage
                if i < len(self.transformers):
                    current_data = self.transformers[i](result)
                    
            except Exception as e:
                results.append({
                    "stage": i + 1,
                    "model": model_name,
                    "success": False,
                    "error": str(e)
                })
                break
                
        return {
            "pipeline": self.name,
            "stages_completed": len([r for r in results if r.get("success")]),
            "total_stages": len(self.stages),
            "results": results,
            "final_output": results[-1].get("result") if results and results[-1].get("success") else None
        }


class ModelOrchestrator:
    """
    Main orchestrator for coordinating multiple models.
    
    Features:
    - Request routing
    - Load balancing
    - Pipeline execution
    - Async task processing
    - Error handling and retries
    """
    
    def __init__(self, max_workers: int = 4):
        self.router = ModelRouter()
        self.task_queue = TaskQueue()
        self.pipelines: Dict[str, ModelPipeline] = {}
        self.tasks: Dict[str, ModelTask] = {}
        self.max_workers = max_workers
        self.workers: List[threading.Thread] = []
        self.is_running = False
        self.callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self._task_counter = 0
        self._lock = threading.Lock()
        
    def register_model(
        self,
        name: str,
        model_type: ModelType,
        model_instance: Any,
        max_concurrent: int = 1
    ):
        """Register a model with the orchestrator."""
        endpoint = ModelEndpoint(
            name=name,
            model_type=model_type,
            model_instance=model_instance,
            max_concurrent=max_concurrent
        )
        self.router.register_endpoint(endpoint)
        
    def create_pipeline(self, name: str) -> ModelPipeline:
        """Create a new processing pipeline."""
        pipeline = ModelPipeline(name)
        self.pipelines[name] = pipeline
        return pipeline
        
    def submit_task(
        self,
        model_type: ModelType,
        input_data: Any,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout_ms: int = 30000,
        **kwargs
    ) -> str:
        """Submit a task for processing."""
        with self._lock:
            self._task_counter += 1
            task_id = f"task_{self._task_counter}_{int(time.time())}"
            
        task = ModelTask(
            task_id=task_id,
            model_type=model_type,
            input_data=input_data,
            priority=priority,
            timeout_ms=timeout_ms,
            kwargs=kwargs
        )
        
        self.tasks[task_id] = task
        self.task_queue.enqueue(task)
        
        return task_id
        
    def get_task(self, task_id: str) -> Optional[ModelTask]:
        """Get task by ID."""
        return self.tasks.get(task_id)
        
    def process_sync(
        self,
        model_type: ModelType,
        input_data: Any,
        **kwargs
    ) -> Any:
        """Process a request synchronously."""
        task = ModelTask(
            task_id=f"sync_{int(time.time())}",
            model_type=model_type,
            input_data=input_data,
            kwargs=kwargs
        )
        
        endpoint = self.router.route(task)
        if not endpoint:
            raise ValueError(f"No endpoint available for model type: {model_type.value}")
            
        return self._execute_task(task, endpoint)
        
    def execute_pipeline(self, pipeline_name: str, input_data: Any) -> Dict:
        """Execute a named pipeline."""
        pipeline = self.pipelines.get(pipeline_name)
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_name}")
            
        return pipeline.execute(input_data)
        
    def _execute_task(self, task: ModelTask, endpoint: ModelEndpoint) -> Any:
        """Execute a task on an endpoint."""
        start = time.time()
        task.status = TaskStatus.RUNNING
        endpoint.current_load += 1
        
        try:
            model = endpoint.model_instance
            
            # Call the model
            if hasattr(model, 'process'):
                result = model.process(task.input_data, **task.kwargs)
            elif callable(model):
                result = model(task.input_data, **task.kwargs)
            else:
                raise ValueError(f"Model {endpoint.name} is not callable")
                
            task.result = result
            task.status = TaskStatus.COMPLETED
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            endpoint.error_count += 1
            raise
            
        finally:
            elapsed = (time.time() - start) * 1000
            task.processing_time_ms = elapsed
            endpoint.current_load -= 1
            endpoint.total_calls += 1
            endpoint.total_time_ms += elapsed
            
        return task.result
        
    def _worker_loop(self):
        """Worker thread loop for processing tasks."""
        while self.is_running:
            task = self.task_queue.dequeue(timeout=0.1)
            if task is None:
                continue
                
            endpoint = self.router.route(task)
            if endpoint is None:
                task.status = TaskStatus.FAILED
                task.error = "No available endpoint"
                continue
                
            try:
                self._execute_task(task, endpoint)
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
                
            # Trigger callbacks
            for callback in self.callbacks.get("task_complete", []):
                try:
                    callback(task)
                except:
                    pass
                    
    def start(self):
        """Start the orchestrator workers."""
        if self.is_running:
            return
            
        self.is_running = True
        
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.workers.append(worker)
            
        print(f"[ModelOrchestrator] Started with {self.max_workers} workers")
        
    def stop(self):
        """Stop the orchestrator."""
        self.is_running = False
        
        for worker in self.workers:
            worker.join(timeout=1.0)
            
        self.workers.clear()
        print("[ModelOrchestrator] Stopped")
        
    def on_task_complete(self, callback: Callable):
        """Register a callback for task completion."""
        self.callbacks["task_complete"].append(callback)
        
    def get_status(self) -> Dict:
        """Get orchestrator status."""
        return {
            "is_running": self.is_running,
            "workers": len(self.workers),
            "router": self.router.get_status(),
            "queue": self.task_queue.get_stats(),
            "tasks_total": len(self.tasks),
            "tasks_by_status": self._count_tasks_by_status(),
            "pipelines": list(self.pipelines.keys())
        }
        
    def _count_tasks_by_status(self) -> Dict[str, int]:
        """Count tasks by status."""
        counts = defaultdict(int)
        for task in self.tasks.values():
            counts[task.status.value] += 1
        return dict(counts)


class ModelEnsemble:
    """
    Ensemble of models for improved accuracy.
    
    Combines outputs from multiple models using
    various aggregation strategies.
    """
    
    def __init__(self, name: str, aggregation: str = "vote"):
        self.name = name
        self.models: List[Tuple[str, Any, float]] = []  # (name, model, weight)
        self.aggregation = aggregation  # "vote", "average", "weighted", "max_confidence"
        
    def add_model(self, name: str, model: Any, weight: float = 1.0):
        """Add a model to the ensemble."""
        self.models.append((name, model, weight))
        
    def predict(self, input_data: Any, **kwargs) -> Dict:
        """Get ensemble prediction."""
        results = []
        
        for name, model, weight in self.models:
            try:
                if hasattr(model, 'process'):
                    result = model.process(input_data, **kwargs)
                elif callable(model):
                    result = model(input_data, **kwargs)
                else:
                    continue
                    
                results.append({
                    "model": name,
                    "weight": weight,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "model": name,
                    "weight": weight,
                    "error": str(e)
                })
                
        # Aggregate results
        aggregated = self._aggregate(results)
        
        return {
            "ensemble": self.name,
            "aggregation": self.aggregation,
            "model_count": len(self.models),
            "results": results,
            "aggregated": aggregated
        }
        
    def _aggregate(self, results: List[Dict]) -> Any:
        """Aggregate results based on strategy."""
        valid_results = [r for r in results if "result" in r]
        
        if not valid_results:
            return None
            
        if self.aggregation == "max_confidence":
            # Find result with highest confidence
            best = max(
                valid_results,
                key=lambda r: getattr(r["result"], "confidence", 0) if hasattr(r["result"], "confidence") else 0
            )
            return best["result"]
            
        elif self.aggregation == "weighted":
            # Weighted combination (for numeric results)
            total_weight = sum(r["weight"] for r in valid_results)
            # Return first result for now (proper implementation depends on result type)
            return valid_results[0]["result"]
            
        else:  # "vote" or default
            # Return most common result (simplified)
            return valid_results[0]["result"]


# =============================================================================
# Convenience Functions
# =============================================================================

def create_orchestrator(models: Dict[str, Tuple[ModelType, Any]] = None) -> ModelOrchestrator:
    """Create a configured orchestrator."""
    orchestrator = ModelOrchestrator()
    
    if models:
        for name, (model_type, model) in models.items():
            orchestrator.register_model(name, model_type, model)
            
    return orchestrator


def create_nlu_reasoning_pipeline(orchestrator: ModelOrchestrator) -> ModelPipeline:
    """Create a pipeline that combines NLU and reasoning."""
    pipeline = orchestrator.create_pipeline("nlu_reasoning")
    
    # Get models
    nlu_endpoint = orchestrator.router.endpoints.get("nlu")
    reasoning_endpoint = orchestrator.router.endpoints.get("reasoning")
    
    if nlu_endpoint:
        pipeline.add_stage(
            "nlu",
            lambda x: nlu_endpoint.model_instance.process(x),
            lambda result: result.content if hasattr(result, "content") else result
        )
        
    if reasoning_endpoint:
        pipeline.add_stage(
            "reasoning",
            lambda x: reasoning_endpoint.model_instance.process(str(x)),
            None
        )
        
    return pipeline
