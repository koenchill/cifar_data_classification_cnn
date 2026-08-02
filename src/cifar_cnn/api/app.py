"""Secure FastAPI application factory."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile, status
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from cifar_cnn.api.audit import audit, get_audit_sink, new_request_id
from cifar_cnn.api.auth import Principal, bind_request_principal, optional_principal
from cifar_cnn.api.config import Settings, get_settings, reset_settings_cache
from cifar_cnn.api.errors import install_exception_handlers
from cifar_cnn.api.images import read_and_validate_image
from cifar_cnn.api.rate_limit import enforce_predict_rate_limit, get_rate_limiter
from cifar_cnn.api.rbac import require_scopes
from cifar_cnn.api.runtime import ModelRuntime
from cifar_cnn.api.schemas import HealthResponse, MetadataResponse, PredictResponse, ReadyResponse
from cifar_cnn.api.service import metadata_payload, predict_image

logger = logging.getLogger("cifar_cnn.api")

_REQUIRE_METADATA = require_scopes("metadata:read")


def create_app(
    *,
    settings: Settings | None = None,
    runtime: ModelRuntime | None = None,
    load_model_on_startup: bool = True,
    max_concurrent_predicts: int = 8,
) -> FastAPI:
    injected = settings if settings is not None else get_settings()
    if settings is not None:
        reset_settings_cache()

    model_runtime = runtime or ModelRuntime()
    predict_sem = asyncio.Semaphore(max_concurrent_predicts)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.settings = injected
        app.state.runtime = model_runtime
        app.state.predict_sem = predict_sem
        if load_model_on_startup:
            try:
                model_runtime.load_bundle(injected.model_bundle_path)
                logger.info("model_loaded bundle=%s", injected.model_bundle_path)
            except Exception:  # noqa: BLE001 — readiness reported via /ready
                logger.exception("model_load_failed")
        yield

    app = FastAPI(
        title="CIFAR-CNN Inference API",
        version="0.1.0",
        docs_url=None if injected.is_production else "/docs",
        redoc_url=None,
        openapi_url=None if injected.is_production else "/openapi.json",
        lifespan=lifespan,
    )
    # Available before lifespan for dependency resolution in tests.
    app.state.settings = injected
    app.state.runtime = model_runtime
    app.state.predict_sem = predict_sem
    install_exception_handlers(app)

    @app.middleware("http")
    async def request_context(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request.state.request_id = new_request_id()
        request.state.started = time.perf_counter()
        response = await call_next(request)
        latency_ms = int((time.perf_counter() - request.state.started) * 1000)
        response.headers["X-Request-Id"] = request.state.request_id
        response.headers["X-Latency-Ms"] = str(latency_ms)
        return response

    def _settings(request: Request) -> Settings:
        return request.app.state.settings  # type: ignore[no-any-return]

    def _runtime(request: Request) -> ModelRuntime:
        return request.app.state.runtime  # type: ignore[no-any-return]

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse()

    @app.get("/ready", response_model=ReadyResponse)
    async def ready(
        request: Request,
        settings_dep: Settings = Depends(_settings),
        runtime_dep: ModelRuntime = Depends(_runtime),
        principal: Principal | None = Depends(optional_principal),
    ) -> ReadyResponse:
        bind_request_principal(request, principal)
        if settings_dep.require_auth_for_ready:
            if principal is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="missing_bearer_token",
                )
            if not principal.has_scope("health:read"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="insufficient_scope",
                )
        loaded = runtime_dep.get()
        if loaded is None:
            reason = runtime_dep.last_error or "model_not_loaded"
            return ReadyResponse(ready=False, reason=reason)
        return ReadyResponse(ready=True, model_id=loaded.model_id)

    @app.get("/v1/metadata", response_model=MetadataResponse)
    async def metadata(
        request: Request,
        principal: Principal = Depends(_REQUIRE_METADATA),
        runtime_dep: ModelRuntime = Depends(_runtime),
    ) -> MetadataResponse:
        bind_request_principal(request, principal)
        loaded = runtime_dep.get()
        if loaded is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="model_not_ready",
            )
        audit(
            "metadata",
            "success",
            subject=principal.subject,
            status_code=200,
            model_id=loaded.model_id,
            request_id=request.state.request_id,
        )
        return MetadataResponse(**metadata_payload(loaded))

    @app.post("/v1/predict", response_model=PredictResponse)
    async def predict(
        request: Request,
        file: UploadFile = File(...),
        top_k: int = Query(default=3, ge=1, le=10),
        settings_dep: Settings = Depends(_settings),
        runtime_dep: ModelRuntime = Depends(_runtime),
        principal: Principal | None = Depends(optional_principal),
    ) -> PredictResponse:
        bind_request_principal(request, principal)
        if principal is None:
            if not settings_dep.allow_anon_predict:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="missing_bearer_token",
                )
            principal = Principal(
                subject="anonymous",
                scopes=frozenset({"predict:invoke"}),
            )
        if not principal.has_scope("predict:invoke"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="insufficient_scope",
            )

        await enforce_predict_rate_limit(request, principal, settings_dep)
        top_k = min(top_k, settings_dep.top_k_max)

        # Validate payload before model readiness so abuse/input failures stay stable.
        image, byte_length, content_type = await read_and_validate_image(file, settings_dep)

        loaded = runtime_dep.get()
        if loaded is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="model_not_ready",
            )
        started = time.perf_counter()
        sem: asyncio.Semaphore = request.app.state.predict_sem
        try:
            async with asyncio.timeout(settings_dep.predict_timeout_sec):
                async with sem:
                    result = await asyncio.to_thread(
                        predict_image,
                        loaded,
                        image,
                        top_k=top_k,
                        request_id=request.state.request_id,
                    )
        except TimeoutError as exc:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="predict_timeout",
            ) from exc

        latency_ms = int((time.perf_counter() - started) * 1000)
        audit(
            "predict",
            "success",
            subject=principal.subject,
            status_code=200,
            model_id=loaded.model_id,
            content_type=content_type,
            byte_length=byte_length,
            request_id=request.state.request_id,
            latency_ms=latency_ms,
            decision=result.decision,
        )
        return result

    def _reset_hooks() -> None:
        get_rate_limiter().reset()
        get_audit_sink().reset()

    app.state._reset_hooks = _reset_hooks
    return app


def app_factory() -> FastAPI:
    """Uvicorn entrypoint: ``uvicorn cifar_cnn.api.app:app_factory --factory``."""
    return create_app()
