from collections.abc import Iterable

from app.models.task_status import TaskStatus


class InvalidTaskStatusTransitionError(ValueError):
    """Raised when a task status transition is not allowed."""


class TaskWorkflowPolicy:
    _ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
        TaskStatus.pending: {TaskStatus.queued, TaskStatus.cancelled, TaskStatus.failed},
        TaskStatus.queued: {TaskStatus.planning, TaskStatus.cancelled, TaskStatus.failed},
        TaskStatus.planning: {TaskStatus.generating, TaskStatus.cancelled, TaskStatus.failed},
        TaskStatus.generating: {TaskStatus.reviewing, TaskStatus.cancelled, TaskStatus.failed},
        TaskStatus.reviewing: {TaskStatus.completed, TaskStatus.failed, TaskStatus.cancelled},
        TaskStatus.completed: set(),
        TaskStatus.failed: set(),
        TaskStatus.cancelled: set(),
    }

    @classmethod
    def allowed_next_statuses(cls, status: TaskStatus) -> Iterable[TaskStatus]:
        return cls._ALLOWED_TRANSITIONS[status]

    @classmethod
    def validate_transition(cls, current: TaskStatus, next_status: TaskStatus) -> None:
        if current == next_status:
            return
        if next_status not in cls._ALLOWED_TRANSITIONS[current]:
            raise InvalidTaskStatusTransitionError(
                f"Invalid task status transition: {current.value} -> {next_status.value}"
            )
