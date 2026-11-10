from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, Tuple, Dict
import time

class TaskPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    DEFAULT = 2
    LOW = 3

class TaskState(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

@dataclass(order=True)
class PrioritizedTask:
    priority_val: int
    created_at: float
    task_id: str = field(compare=False)
    func: Callable = field(compare=False)
    args: Tuple[Any, ...] = field(default_factory=tuple, compare=False)
    kwargs: Dict[str, Any] = field(default_factory=dict, compare=False)
    timeout_seconds: Optional[float] = field(default=None, compare=False)
    retries_left: int = field(default=0, compare=False)

@dataclass
class TaskResult:
    task_id: str
    state: TaskState
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
