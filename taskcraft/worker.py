import threading
import time
from typing import List, Optional
from taskcraft.models import TaskState, TaskResult, PrioritizedTask
from taskcraft.queue import PriorityTaskQueue

class WorkerPool:
    def __init__(self, queue: PriorityTaskQueue, num_workers: int = 2):
        self.queue = queue
        self.num_workers = num_workers
        self.workers: List[threading.Thread] = []
        self.is_running = False

    def _worker_loop(self):
        while self.is_running:
            task = self.queue.dequeue(block=True, timeout=0.2)
            if task is None:
                continue

            self.queue.set_result(TaskResult(task_id=task.task_id, state=TaskState.RUNNING))
            start_time = time.perf_counter()

            try:
                out = task.func(*task.args, **task.kwargs)
                elapsed = (time.perf_counter() - start_time) * 1000.0
                self.queue.set_result(TaskResult(
                    task_id=task.task_id,
                    state=TaskState.SUCCESS,
                    result=out,
                    execution_time_ms=elapsed
                ))
            except Exception as e:
                elapsed = (time.perf_counter() - start_time) * 1000.0
                if task.retries_left > 0:
                    task.retries_left -= 1
                    with self.queue.lock:
                        import heapq
                        heapq.heappush(self.queue.heap, task)
                else:
                    self.queue.set_result(TaskResult(
                        task_id=task.task_id,
                        state=TaskState.FAILED,
                        error=str(e),
                        execution_time_ms=elapsed
                    ))

    def start(self):
        self.is_running = True
        for i in range(self.num_workers):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            self.workers.append(t)
            t.start()

    def stop(self):
        self.is_running = False
        for t in self.workers:
            t.join(timeout=1.0)
        self.workers.clear()

    def wait_for(self, task_id: str, timeout: float = 5.0) -> Optional[TaskResult]:
        deadline = time.time() + timeout
        while time.time() < deadline:
            res = self.queue.get_result(task_id)
            if res and res.state in (TaskState.SUCCESS, TaskState.FAILED, TaskState.CANCELLED):
                return res
            time.sleep(0.02)
        return self.queue.get_result(task_id)
