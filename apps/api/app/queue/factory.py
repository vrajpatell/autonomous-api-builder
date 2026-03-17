from app.core.config import settings
from app.queue.backends import CeleryQueueBackend, NoopQueueBackend
from app.queue.base import JobQueueBackend


def get_queue_backend() -> JobQueueBackend:
    if settings.queue_backend == "noop":
        return NoopQueueBackend()
    return CeleryQueueBackend()
