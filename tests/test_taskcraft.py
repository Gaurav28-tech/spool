import os
import sys
import unittest
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from taskcraft.models import TaskPriority, TaskState
from taskcraft.queue import PriorityTaskQueue
from taskcraft.worker import WorkerPool

class TestTaskCraft(unittest.TestCase):
    def test_priority_scheduling(self):
        queue = PriorityTaskQueue()
        # Enqueue low first, then critical
        t1 = queue.enqueue(lambda: "low", priority=TaskPriority.LOW)
        t2 = queue.enqueue(lambda: "crit", priority=TaskPriority.CRITICAL)

        first_dequeued = queue.dequeue(block=False)
        self.assertEqual(first_dequeued.task_id, t2)

        second_dequeued = queue.dequeue(block=False)
        self.assertEqual(second_dequeued.task_id, t1)

    def test_worker_execution_success(self):
        queue = PriorityTaskQueue()
        pool = WorkerPool(queue, num_workers=1)
        pool.start()

        def add(a, b):
            return a + b

        t_id = queue.enqueue(add, args=(10, 25))
        result = pool.wait_for(t_id, timeout=2.0)

        self.assertIsNotNone(result)
        self.assertEqual(result.state, TaskState.SUCCESS)
        self.assertEqual(result.result, 35)

        pool.stop()

    def test_worker_retry_on_failure(self):
        queue = PriorityTaskQueue()
        pool = WorkerPool(queue, num_workers=1)
        pool.start()

        attempts = {"count": 0}

        def flaky_task():
            attempts["count"] += 1
            if attempts["count"] < 2:
                raise ValueError("Temporary failure")
            return "recovered"

        t_id = queue.enqueue(flaky_task, retries=1)
        result = pool.wait_for(t_id, timeout=2.0)

        self.assertEqual(result.state, TaskState.SUCCESS)
        self.assertEqual(result.result, "recovered")
        self.assertEqual(attempts["count"], 2)

        pool.stop()

if __name__ == "__main__":
    unittest.main()
