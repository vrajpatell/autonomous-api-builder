from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    queued = "queued"
    planning = "planning"
    generating = "generating"
    reviewing = "reviewing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"
