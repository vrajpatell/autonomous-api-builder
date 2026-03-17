from enum import StrEnum


class TaskStatus(StrEnum):
    pending = "pending"
    queued = "queued"
    planning = "planning"
    generating = "generating"
    reviewing = "reviewing"
    completed = "completed"
    failed = "failed"
