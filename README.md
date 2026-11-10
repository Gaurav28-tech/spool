# TaskCraft ⚙️

[![CI](https://github.com/Gaurav28-tech/task-craft/actions/workflows/ci.yml/badge.svg)](https://github.com/Gaurav28-tech/task-craft)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-brightgreen.svg)]()

**TaskCraft** is a lightweight, embeddable background job queue and worker execution framework for Python. Designed as a clean, low-overhead alternative to Celery and RQ, it provides priority-ranked scheduling, worker concurrency control, task timeouts, retry backoff, and linear/DAG pipeline chaining.

---

## 🚀 Key Features

- **Priority-Ranked Scheduling**: Strict priority ordering (`CRITICAL` > `HIGH` > `DEFAULT` > `LOW`) ensuring vital workloads preempt background jobs.
- **Worker Concurrency Pools**: Configurable thread worker pools with graceful shutdown and signal handling.
- **Pipeline & DAG Chaining**: Express dependencies easily; downstream jobs trigger automatically upon successful upstream completion.
- **Failure Resilience**: Built-in timeout enforcement, failure recovery, and configurable retry counts.
- **Zero External Dependencies**: Pure Python standard library implementation with zero Redis/RabbitMQ infrastructure overhead for embedded services.

---

## 🏗️ Architecture

```
Tasks Submitted
       |
       v
+--------------------------------------------------------+
| Priority Queue (CRITICAL -> HIGH -> DEFAULT -> LOW)   |
+--------------------------------------------------------+
       |
       +--------------+--------------+
       |              |              |
       v              v              v
  [Worker 1]     [Worker 2]     [Worker 3]
       |              |              |
       +--------------+--------------+
                      |
                      v
             [Pipeline Coordinator]
         (Triggers downstream dependent tasks)
```

---

## 📦 Quickstart

### Installation

```bash
git clone https://github.com/Gaurav28-tech/task-craft.git
cd task-craft
```

### Basic Usage

```python
from taskcraft.queue import PriorityTaskQueue
from taskcraft.worker import WorkerPool
from taskcraft.models import TaskPriority
import time

queue = PriorityTaskQueue()

def generate_invoice(order_id: str):
    time.sleep(0.1)
    return f"invoice_{order_id}.pdf"

# Enqueue tasks with priority
task_id = queue.enqueue(
    func=generate_invoice,
    args=("ord_8819",),
    priority=TaskPriority.HIGH
)

# Start workers to process jobs
pool = WorkerPool(queue, num_workers=2)
pool.start()

# Wait for completion and fetch result
result = pool.wait_for(task_id, timeout=2.0)
print(f"Task Status: {result.state.value}, Output: {result.result}")

pool.stop()
```

### Running Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📄 License

Distributed under the [MIT License](LICENSE).
