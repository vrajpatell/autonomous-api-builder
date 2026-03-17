import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings

logger = logging.getLogger(__name__)



def _build_provider() -> TracerProvider:
    resource = Resource.create(
        {
            "service.name": settings.otel_service_name,
            "deployment.environment": settings.app_env,
        }
    )
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    return provider


def configure_tracing(app) -> None:
    if not settings.otel_enabled:
        return

    trace.set_tracer_provider(_build_provider())
    FastAPIInstrumentor.instrument_app(app)
    logger.info(
        "OpenTelemetry enabled",
        extra={
            "otel_endpoint": settings.otel_exporter_otlp_endpoint,
            "otel_service_name": settings.otel_service_name,
        },
    )


def configure_worker_tracing() -> None:
    if not settings.otel_enabled:
        return

    trace.set_tracer_provider(_build_provider())
