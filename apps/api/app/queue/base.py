from typing import Protocol


class JobQueueBackend(Protocol):
    def enqueue_task_generation(self, task_id: int, correlation_id: str | None = None) -> str:
        """Enqueue a long-running task generation job and return queue job id."""
