import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.router import api_router
from app.core.config import settings
from app.observability import configure_logging, configure_tracing, metrics_response, new_id, set_request_context
from app.observability.metrics import api_request_count, api_request_latency_seconds

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)
register_exception_handlers(app)
configure_tracing(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_observability_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or new_id()
    correlation_id = request.headers.get("x-correlation-id") or request_id
    set_request_context(request_id=request_id, correlation_id=correlation_id)

    started = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["x-request-id"] = request_id
        response.headers["x-correlation-id"] = correlation_id
        return response
    except Exception:
        logger.exception(
            "Unhandled API exception",
            extra={"path": request.url.path, "method": request.method},
        )
        raise
    finally:
        duration = time.perf_counter() - started
        path = request.url.path
        api_request_count.labels(method=request.method, path=path, status_code=str(status_code)).inc()
        api_request_latency_seconds.labels(method=request.method, path=path).observe(duration)
        logger.info(
            "HTTP request handled",
            extra={
                "event": "http.request",
                "method": request.method,
                "path": path,
                "status_code": status_code,
                "duration_ms": round(duration * 1000, 2),
                "client_ip": request.client.host if request.client else None,
            },
        )


@app.get("/metrics", include_in_schema=False)
def metrics():
    return metrics_response()


@app.get("/api/metrics", include_in_schema=False)
def api_metrics():
    return metrics_response()


app.include_router(api_router)
