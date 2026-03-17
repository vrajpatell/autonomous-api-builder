from contextvars import ContextVar
from uuid import uuid4

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def new_id() -> str:
    return str(uuid4())


def set_request_context(*, request_id: str | None = None, correlation_id: str | None = None) -> None:
    if request_id is not None:
        request_id_var.set(request_id)
    if correlation_id is not None:
        correlation_id_var.set(correlation_id)


def get_request_id() -> str:
    value = request_id_var.get()
    if value:
        return value
    value = new_id()
    request_id_var.set(value)
    return value


def get_correlation_id() -> str:
    value = correlation_id_var.get()
    if value:
        return value
    value = new_id()
    correlation_id_var.set(value)
    return value
