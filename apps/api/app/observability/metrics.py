from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response

api_request_count = Counter(
    "autobuilder_api_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
api_request_latency_seconds = Histogram(
    "autobuilder_api_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)

worker_jobs_total = Counter(
    "autobuilder_worker_jobs_total",
    "Total worker jobs processed",
    ["result"],
)
worker_job_duration_seconds = Histogram(
    "autobuilder_worker_job_duration_seconds",
    "Worker job runtime in seconds",
)

tasks_total = Counter(
    "autobuilder_tasks_lifecycle_total",
    "Task lifecycle transitions",
    ["status"],
)
active_tasks = Gauge(
    "autobuilder_active_tasks",
    "Number of tasks currently in-flight",
)


def metrics_response() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
