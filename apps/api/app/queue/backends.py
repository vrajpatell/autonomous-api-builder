from uuid import uuid4

from app.queue.base import JobQueueBackend
from app.workers.tasks import process_generation_task


class CeleryQueueBackend(JobQueueBackend):
    def enqueue_task_generation(self, task_id: int, correlation_id: str | None = None) -> str:
        async_result = process_generation_task.delay(task_id, correlation_id)
        return async_result.id


class NoopQueueBackend(JobQueueBackend):
    """Queue backend for tests/local fallbacks where workers are not active."""

    def enqueue_task_generation(self, task_id: int, correlation_id: str | None = None) -> str:
        return f"noop-{task_id}-{correlation_id or uuid4()}"
