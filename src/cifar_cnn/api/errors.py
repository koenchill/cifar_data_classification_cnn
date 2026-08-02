"""Secure error responses — no stack traces or internal paths to clients."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from cifar_cnn.api.audit import audit, new_request_id


def _request_id(request: Request) -> str:
    rid = getattr(request.state, "request_id", None)
    if isinstance(rid, str) and rid:
        return rid
    return new_request_id()


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exc_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        rid = _request_id(request)
        detail = exc.detail if isinstance(exc.detail, str) else "request_failed"
        principal = getattr(request.state, "principal", None)
        subject = getattr(principal, "subject", None) if principal else None
        audit(
            "http_error",
            "denied" if exc.status_code in {401, 403, 429} else "error",
            subject=subject,
            status_code=exc.status_code,
            detail=detail,
            request_id=rid,
        )
        headers = dict(exc.headers) if exc.headers else None
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": detail, "request_id": rid},
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        rid = _request_id(request)
        audit(
            "validation_error",
            "error",
            status_code=422,
            detail="validation_error",
            request_id=rid,
        )
        return JSONResponse(
            status_code=422,
            content={"detail": "validation_error", "request_id": rid},
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        rid = _request_id(request)
        audit(
            "unhandled_error",
            "error",
            status_code=500,
            detail=type(exc).__name__,
            request_id=rid,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "internal_error", "request_id": rid},
        )
