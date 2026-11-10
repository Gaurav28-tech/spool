import heapq
import threading
import uuid
import time
from typing import Any, Callable, Optional, Tuple, Dict
from taskcraft.models import TaskPriority, TaskState, PrioritizedTask, TaskResult

class PriorityTaskQueue:
    def __init__(self):
        self.heap = []
        self.results: Dict[str, TaskResult] = {}
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)

    def enqueue(self, func: Callable, args: Tuple = (), kwargs: Dict = None,
                priority: TaskPriority = TaskPriority.DEFAULT,
                timeout_seconds: Optional[float] = None,
                retries: int = 0) -> str:
        if kwargs is None:
            kwargs = {}
        task_id = f"task_{uuid.uuid4().hex[:8]}"

        item = PrioritizedTask(
            priority_val=priority.value,
            created_at=time.time(),
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            timeout_seconds=timeout_seconds,
            retries_left=retries
        )

        with self.lock:
            self.results[task_id] = TaskResult(task_id=task_id, state=TaskState.PENDING)
            heapq.heappush(self.heap, item)
            self.not_empty.notify()

        return task_id

    def dequeue(self, block: bool = True, timeout: Optional[float] = None) -> Optional[PrioritizedTask]:
        with self.not_empty:
            while not self.heap:
                if not block:
                    return None
                if not self.not_empty.wait(timeout=timeout):
                    return None
            return heapq.heappop(self.heap)

    def get_result(self, task_id: str) -> Optional[TaskResult]:
        with self.lock:
            return self.results.get(task_id)

    def set_result(self, res: TaskResult):
        with self.lock:
            self.results[res.task_id] = res

    def __len__(self) -> int:
        with self.lock:
            return len(self.heap)
