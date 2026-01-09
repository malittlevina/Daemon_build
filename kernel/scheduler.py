# kernel/scheduler.py
"""
Scheduler - Task scheduling and priority-based execution.

The scheduler provides:
- Priority-based task queuing
- Delayed and recurring tasks
- Cron-like scheduling
- Task dependencies
- Resource-aware scheduling
"""

import threading
import heapq
import time
from typing import Dict, Any, Optional, List, Callable, Set
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid


class TaskState(Enum):
    """Task lifecycle states."""
    PENDING = auto()
    SCHEDULED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    IDLE = 4


@dataclass(order=True)
class ScheduledTask:
    """A task in the scheduler."""
    next_run: float
    priority: int = field(compare=True)
    id: str = field(compare=False, default_factory=lambda: str(uuid.uuid4()))
    name: str = field(compare=False, default="unnamed")
    callback: Callable = field(compare=False, default=None)
    args: tuple = field(compare=False, default_factory=tuple)
    kwargs: Dict[str, Any] = field(compare=False, default_factory=dict)
    state: TaskState = field(compare=False, default=TaskState.PENDING)
    recurring: bool = field(compare=False, default=False)
    interval: Optional[float] = field(compare=False, default=None)
    max_runs: Optional[int] = field(compare=False, default=None)
    run_count: int = field(compare=False, default=0)
    created_at: datetime = field(compare=False, default_factory=datetime.now)
    last_run: Optional[datetime] = field(compare=False, default=None)
    last_error: Optional[str] = field(compare=False, default=None)
    dependencies: Set[str] = field(compare=False, default_factory=set)
    timeout: Optional[float] = field(compare=False, default=None)
    metadata: Dict[str, Any] = field(compare=False, default_factory=dict)


class Scheduler:
    """
    Task scheduler for the kernel.
    
    Features:
    - Priority queue scheduling
    - One-time and recurring tasks
    - Delayed execution
    - Task dependencies
    - Concurrent task limits
    """
    
    def __init__(self, kernel, max_concurrent: int = 10):
        """Initialize the scheduler."""
        self.kernel = kernel
        self.max_concurrent = max_concurrent
        
        self._tasks: Dict[str, ScheduledTask] = {}
        self._heap: List[ScheduledTask] = []
        self._completed: Dict[str, ScheduledTask] = {}
        self._running: Dict[str, threading.Thread] = {}
        self._lock = threading.RLock()
        self._running_flag = False
        self._tick_thread: Optional[threading.Thread] = None
        
        # Stats
        self._stats = {
            "tasks_scheduled": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_cancelled": 0
        }
        
        print("[Scheduler] Initialized")
    
    # =========================================================================
    # Task scheduling
    # =========================================================================
    
    def schedule(
        self,
        callback: Callable,
        name: str = "task",
        delay: float = 0,
        priority: TaskPriority = TaskPriority.NORMAL,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        recurring: bool = False,
        interval: Optional[float] = None,
        max_runs: Optional[int] = None,
        dependencies: Set[str] = None,
        timeout: Optional[float] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Schedule a task for execution.
        
        Args:
            callback: Function to execute
            name: Task name
            delay: Delay before first execution (seconds)
            priority: Task priority
            args: Positional arguments for callback
            kwargs: Keyword arguments for callback
            recurring: If True, reschedule after completion
            interval: Interval for recurring tasks (seconds)
            max_runs: Maximum number of runs for recurring tasks
            dependencies: Set of task IDs that must complete first
            timeout: Task execution timeout
            metadata: Additional metadata
        
        Returns:
            Task ID
        """
        task = ScheduledTask(
            next_run=time.time() + delay,
            priority=priority.value,
            name=name,
            callback=callback,
            args=args,
            kwargs=kwargs or {},
            recurring=recurring,
            interval=interval or delay,
            max_runs=max_runs,
            dependencies=dependencies or set(),
            timeout=timeout,
            metadata=metadata or {}
        )
        
        with self._lock:
            self._tasks[task.id] = task
            task.state = TaskState.SCHEDULED
            heapq.heappush(self._heap, task)
            self._stats["tasks_scheduled"] += 1
        
        self.kernel.message_bus.emit("task.scheduled", {
            "id": task.id,
            "name": name
        })
        
        return task.id
    
    def schedule_at(
        self,
        callback: Callable,
        run_at: datetime,
        name: str = "task",
        **kwargs
    ) -> str:
        """Schedule a task to run at a specific time."""
        delay = max(0, (run_at - datetime.now()).total_seconds())
        return self.schedule(callback, name=name, delay=delay, **kwargs)
    
    def schedule_recurring(
        self,
        callback: Callable,
        interval: float,
        name: str = "recurring_task",
        immediate: bool = False,
        **kwargs
    ) -> str:
        """Schedule a recurring task."""
        delay = 0 if immediate else interval
        return self.schedule(
            callback,
            name=name,
            delay=delay,
            recurring=True,
            interval=interval,
            **kwargs
        )
    
    def defer(self, callback: Callable, **kwargs) -> str:
        """Defer a task to run on next tick."""
        return self.schedule(callback, delay=0, **kwargs)
    
    # =========================================================================
    # Task management
    # =========================================================================
    
    def cancel(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        with self._lock:
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            if task.state in (TaskState.COMPLETED, TaskState.CANCELLED):
                return False
            
            task.state = TaskState.CANCELLED
            self._stats["tasks_cancelled"] += 1
        
        self.kernel.message_bus.emit("task.cancelled", {"id": task_id})
        return True
    
    def reschedule(self, task_id: str, delay: float) -> bool:
        """Reschedule a task with a new delay."""
        with self._lock:
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            if task.state not in (TaskState.PENDING, TaskState.SCHEDULED):
                return False
            
            task.next_run = time.time() + delay
            # Reheapify
            heapq.heapify(self._heap)
        
        return True
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get a task by ID."""
        return self._tasks.get(task_id)
    
    def get_tasks_by_name(self, name: str) -> List[ScheduledTask]:
        """Get all tasks with a given name."""
        return [t for t in self._tasks.values() if t.name == name]
    
    def pending_count(self) -> int:
        """Get count of pending tasks."""
        return len([t for t in self._tasks.values() 
                   if t.state in (TaskState.PENDING, TaskState.SCHEDULED)])
    
    # =========================================================================
    # Task execution
    # =========================================================================
    
    def tick(self):
        """Process ready tasks (called by kernel main loop)."""
        now = time.time()
        tasks_to_run = []
        
        with self._lock:
            # Find ready tasks
            while self._heap:
                task = self._heap[0]
                
                if task.state == TaskState.CANCELLED:
                    heapq.heappop(self._heap)
                    continue
                
                if task.next_run > now:
                    break
                
                # Check concurrent limit
                if len(self._running) >= self.max_concurrent:
                    break
                
                # Check dependencies
                if not self._dependencies_met(task):
                    # Push back with slight delay
                    task.next_run = now + 0.1
                    heapq.heapreplace(self._heap, task)
                    continue
                
                heapq.heappop(self._heap)
                tasks_to_run.append(task)
        
        # Execute ready tasks
        for task in tasks_to_run:
            self._execute_task(task)
    
    def _dependencies_met(self, task: ScheduledTask) -> bool:
        """Check if all task dependencies are completed."""
        for dep_id in task.dependencies:
            if dep_id in self._tasks:
                dep = self._tasks[dep_id]
                if dep.state != TaskState.COMPLETED:
                    return False
            elif dep_id not in self._completed:
                return False
        return True
    
    def _execute_task(self, task: ScheduledTask):
        """Execute a task in a thread."""
        def run_task():
            task.state = TaskState.RUNNING
            task.last_run = datetime.now()
            
            try:
                # Execute with timeout if specified
                if task.timeout:
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(task.callback, *task.args, **task.kwargs)
                        future.result(timeout=task.timeout)
                else:
                    task.callback(*task.args, **task.kwargs)
                
                task.run_count += 1
                task.state = TaskState.COMPLETED
                self._stats["tasks_completed"] += 1
                
                self.kernel.message_bus.emit("task.completed", {
                    "id": task.id,
                    "name": task.name
                })
                
            except Exception as e:
                task.state = TaskState.FAILED
                task.last_error = str(e)
                self._stats["tasks_failed"] += 1
                
                self.kernel.message_bus.emit("task.failed", {
                    "id": task.id,
                    "name": task.name,
                    "error": str(e)
                })
            
            finally:
                with self._lock:
                    self._running.pop(task.id, None)
                    
                    # Handle recurring tasks
                    if task.recurring and task.state == TaskState.COMPLETED:
                        if task.max_runs is None or task.run_count < task.max_runs:
                            task.next_run = time.time() + task.interval
                            task.state = TaskState.SCHEDULED
                            heapq.heappush(self._heap, task)
                        else:
                            self._completed[task.id] = task
                            del self._tasks[task.id]
                    else:
                        self._completed[task.id] = task
                        del self._tasks[task.id]
        
        thread = threading.Thread(
            target=run_task,
            name=f"Task-{task.id[:8]}-{task.name}",
            daemon=True
        )
        
        with self._lock:
            self._running[task.id] = thread
        
        thread.start()
    
    # =========================================================================
    # Scheduler lifecycle
    # =========================================================================
    
    def start(self):
        """Start the scheduler tick loop."""
        if self._running_flag:
            return
        
        self._running_flag = True
        print("[Scheduler] Started")
    
    def stop(self):
        """Stop the scheduler."""
        self._running_flag = False
        
        # Wait for running tasks
        for task_id, thread in list(self._running.items()):
            thread.join(timeout=1.0)
        
        print("[Scheduler] Stopped")
    
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running_flag
    
    # =========================================================================
    # Statistics
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        state_counts = {}
        for task in self._tasks.values():
            state_name = task.state.name
            state_counts[state_name] = state_counts.get(state_name, 0) + 1
        
        return {
            **self._stats,
            "pending_tasks": self.pending_count(),
            "running_tasks": len(self._running),
            "completed_history": len(self._completed),
            "by_state": state_counts
        }
    
    def clear_history(self):
        """Clear completed task history."""
        self._completed.clear()
