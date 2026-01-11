# kernel/scheduler.py
"""
Kernel Scheduler - Priority-based task scheduling

Manages background tasks, scheduled jobs, and async operations
with priority queuing and resource awareness.
"""

from typing import Callable, Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import heapq
import time
import uuid


class TaskPriority(Enum):
    CRITICAL = 0   # Immediate execution
    HIGH = 1       # Next available slot
    NORMAL = 2     # Standard scheduling
    LOW = 3        # Background tasks
    IDLE = 4       # Run when system is idle


class TaskState(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    """Represents a task scheduled for execution."""
    task_id: str
    name: str
    callback: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    state: TaskState = TaskState.PENDING
    scheduled_time: Optional[datetime] = None
    interval_seconds: Optional[float] = None  # For recurring tasks
    max_retries: int = 0
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    source_module: Optional[str] = None
    
    def __lt__(self, other):
        """Enable heap comparison based on priority and scheduled time."""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        if self.scheduled_time and other.scheduled_time:
            return self.scheduled_time < other.scheduled_time
        return self.created_at < other.created_at


class KernelScheduler:
    """
    Central task scheduler for the kernel.
    
    Features:
    - Priority-based task queuing
    - Scheduled (delayed) execution
    - Recurring tasks with intervals
    - Task retry with backoff
    - Resource-aware scheduling
    - Task cancellation
    """
    
    def __init__(self, max_workers: int = 4):
        self._task_heap: List[ScheduledTask] = []
        self._tasks: Dict[str, ScheduledTask] = {}
        self._lock = threading.RLock()
        self._running = False
        self._scheduler_thread: Optional[threading.Thread] = None
        self._worker_threads: List[threading.Thread] = []
        self._max_workers = max_workers
        self._active_workers = 0
        self._task_condition = threading.Condition(self._lock)
        self._completed_callbacks: Dict[str, Callable] = {}
        
        print(f"[KernelScheduler] Initialized with {max_workers} max workers.")
    
    def start(self):
        """Start the scheduler."""
        self._running = True
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        print("[KernelScheduler] Started.")
    
    def stop(self, wait: bool = True):
        """Stop the scheduler."""
        self._running = False
        with self._task_condition:
            self._task_condition.notify_all()
        
        if wait and self._scheduler_thread:
            self._scheduler_thread.join(timeout=5.0)
        
        print("[KernelScheduler] Stopped.")
    
    def schedule(
        self,
        callback: Callable,
        name: str = "unnamed_task",
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        delay_seconds: float = 0,
        interval_seconds: float = None,
        max_retries: int = 0,
        source_module: str = None,
        on_complete: Callable = None
    ) -> str:
        """
        Schedule a task for execution.
        
        Args:
            callback: Function to execute
            name: Human-readable task name
            args: Positional arguments for callback
            kwargs: Keyword arguments for callback
            priority: Task priority level
            delay_seconds: Delay before first execution
            interval_seconds: For recurring tasks, interval between executions
            max_retries: Number of retry attempts on failure
            source_module: Name of module that created the task
            on_complete: Callback when task completes
            
        Returns:
            Task ID string
        """
        task_id = str(uuid.uuid4())
        scheduled_time = datetime.utcnow() + timedelta(seconds=delay_seconds) if delay_seconds > 0 else None
        
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            callback=callback,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            state=TaskState.SCHEDULED if scheduled_time else TaskState.PENDING,
            scheduled_time=scheduled_time,
            interval_seconds=interval_seconds,
            max_retries=max_retries,
            source_module=source_module
        )
        
        with self._lock:
            self._tasks[task_id] = task
            heapq.heappush(self._task_heap, task)
            if on_complete:
                self._completed_callbacks[task_id] = on_complete
        
        with self._task_condition:
            self._task_condition.notify()
        
        print(f"[KernelScheduler] Scheduled task '{name}' (ID: {task_id[:8]}...) priority={priority.name}")
        return task_id
    
    def cancel(self, task_id: str) -> bool:
        """Cancel a pending task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task.state in (TaskState.PENDING, TaskState.SCHEDULED):
                task.state = TaskState.CANCELLED
                print(f"[KernelScheduler] Cancelled task: {task.name}")
                return True
            return False
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get task info by ID."""
        with self._lock:
            return self._tasks.get(task_id)
    
    def get_pending_tasks(self) -> List[ScheduledTask]:
        """Get all pending/scheduled tasks."""
        with self._lock:
            return [t for t in self._tasks.values() 
                    if t.state in (TaskState.PENDING, TaskState.SCHEDULED)]
    
    def get_running_tasks(self) -> List[ScheduledTask]:
        """Get currently running tasks."""
        with self._lock:
            return [t for t in self._tasks.values() if t.state == TaskState.RUNNING]
    
    def _scheduler_loop(self):
        """Main scheduler loop."""
        while self._running:
            task = self._get_next_task()
            if task:
                self._execute_task(task)
            else:
                # Wait for new tasks
                with self._task_condition:
                    self._task_condition.wait(timeout=0.5)
    
    def _get_next_task(self) -> Optional[ScheduledTask]:
        """Get the next task ready for execution."""
        with self._lock:
            now = datetime.utcnow()
            
            # Clean the heap of cancelled tasks
            while self._task_heap:
                task = self._task_heap[0]
                if task.state == TaskState.CANCELLED:
                    heapq.heappop(self._task_heap)
                    continue
                
                # Check if task is ready
                if task.state == TaskState.SCHEDULED and task.scheduled_time:
                    if task.scheduled_time > now:
                        return None  # Not ready yet
                
                if task.state in (TaskState.PENDING, TaskState.SCHEDULED):
                    return heapq.heappop(self._task_heap)
                
                break
            
            return None
    
    def _execute_task(self, task: ScheduledTask):
        """Execute a task."""
        with self._lock:
            if self._active_workers >= self._max_workers:
                # Re-queue the task
                heapq.heappush(self._task_heap, task)
                return
            
            task.state = TaskState.RUNNING
            task.started_at = datetime.utcnow()
            self._active_workers += 1
        
        def run_task():
            try:
                result = task.callback(*task.args, **task.kwargs)
                
                with self._lock:
                    task.state = TaskState.COMPLETED
                    task.result = result
                    task.completed_at = datetime.utcnow()
                    self._active_workers -= 1
                
                # Handle recurring tasks
                if task.interval_seconds and task.state == TaskState.COMPLETED:
                    self._reschedule_recurring(task)
                
                # Call completion callback
                if task.task_id in self._completed_callbacks:
                    try:
                        self._completed_callbacks[task.task_id](task)
                    except Exception as e:
                        print(f"[KernelScheduler] Completion callback error: {e}")
                
            except Exception as e:
                with self._lock:
                    task.error = str(e)
                    task.retry_count += 1
                    self._active_workers -= 1
                    
                    if task.retry_count <= task.max_retries:
                        # Retry with exponential backoff
                        delay = 2 ** task.retry_count
                        task.state = TaskState.SCHEDULED
                        task.scheduled_time = datetime.utcnow() + timedelta(seconds=delay)
                        heapq.heappush(self._task_heap, task)
                        print(f"[KernelScheduler] Task '{task.name}' failed, retry {task.retry_count}/{task.max_retries} in {delay}s")
                    else:
                        task.state = TaskState.FAILED
                        task.completed_at = datetime.utcnow()
                        print(f"[KernelScheduler] Task '{task.name}' failed permanently: {e}")
        
        # Run in thread
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()
    
    def _reschedule_recurring(self, task: ScheduledTask):
        """Reschedule a recurring task."""
        new_task = ScheduledTask(
            task_id=str(uuid.uuid4()),
            name=task.name,
            callback=task.callback,
            args=task.args,
            kwargs=task.kwargs,
            priority=task.priority,
            state=TaskState.SCHEDULED,
            scheduled_time=datetime.utcnow() + timedelta(seconds=task.interval_seconds),
            interval_seconds=task.interval_seconds,
            max_retries=task.max_retries,
            source_module=task.source_module
        )
        
        with self._lock:
            self._tasks[new_task.task_id] = new_task
            heapq.heappush(self._task_heap, new_task)
            
            # Copy completion callback
            if task.task_id in self._completed_callbacks:
                self._completed_callbacks[new_task.task_id] = self._completed_callbacks[task.task_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        with self._lock:
            states = {}
            for task in self._tasks.values():
                state_name = task.state.value
                states[state_name] = states.get(state_name, 0) + 1
            
            return {
                "total_tasks": len(self._tasks),
                "pending_count": len(self._task_heap),
                "active_workers": self._active_workers,
                "max_workers": self._max_workers,
                "task_states": states,
                "running": self._running
            }
