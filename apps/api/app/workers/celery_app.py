from celery import Celery

from app.core.config import settings
from app.observability import configure_logging, configure_worker_tracing

configure_logging()
configure_worker_tracing()

celery_app = Celery(
    "autonomous_api_builder",
    broker=settings.effective_celery_broker_url,
    backend=settings.effective_celery_result_backend,
)

celery_app.conf.update(
    task_default_queue="generation",
    task_track_started=True,
)

celery_app.autodiscover_tasks(["app.workers"])
