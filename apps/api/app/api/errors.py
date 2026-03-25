from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.exceptions import DomainError


def _error_payload(code: str, message: str, details: dict | None = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(_, exc: DomainError):
        status_code = 400
        if exc.code == "authorization_error":
            status_code = 403
        elif exc.code == "not_found":
            status_code = 404
        elif exc.code == "conflict":
            status_code = 409

        return JSONResponse(status_code=status_code, content=_error_payload(exc.code, exc.message, exc.details))

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_, exc: HTTPException):
        detail = exc.detail if isinstance(exc.detail, str) else "HTTP error"
        return JSONResponse(status_code=exc.status_code, content=_error_payload("http_error", detail))

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(_, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=_error_payload("request_validation_error", "Request validation failed", {"errors": jsonable_encoder(exc.errors())}),
        )
