# syntax=docker/dockerfile:1.7
# Hardened inference image — multi-stage, digest-pinned base, non-root runtime.
# Build (from repo root):
#   docker buildx build --ignorefile deploy/docker/dockerignore \
#     -f deploy/docker/Dockerfile -t cifar-cnn-api:local .

ARG PYTHON_BASE=python@sha256:b18992999dbe963a45a8a4da40ac2b1975be1a776d939d098c647482bcad5cba

# ---------------------------------------------------------------------------
# Builder — install runtime deps into an isolated venv (CPU torch wheels)
# ---------------------------------------------------------------------------
# DL3006: digest pin is in PYTHON_BASE default (tagless @sha256).
# hadolint ignore=DL3006
FROM ${PYTHON_BASE} AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

# CPU torch index keeps the serve image smaller than the CUDA default.
# Package versions are pinned in pyproject.toml (DL3013 N/A for local path install).
# hadolint ignore=DL3013
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir . \
      --extra-index-url https://download.pytorch.org/whl/cpu

# ---------------------------------------------------------------------------
# Runtime — no compilers, no dataset, no training entrypoints
# ---------------------------------------------------------------------------
# hadolint ignore=DL3006
FROM ${PYTHON_BASE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:${PATH}" \
    # Fail-closed prod defaults; local compose overrides to development/static.
    APP_ENV=production \
    CIFAR_CNN_OIDC_MODE=jwks \
    CIFAR_CNN_ALLOW_ANON_PREDICT=false \
    MODEL_BUNDLE_PATH=/app/models/bundles/simple_cnn-1.0.1 \
    HOME=/tmp \
    MPLCONFIGDIR=/tmp/matplotlib

# Non-root identity (numeric for K8s runAsNonRoot / runAsUser)
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --home-dir /tmp --shell /usr/sbin/nologin app \
 && mkdir -p /app /tmp/matplotlib \
 && chown -R app:app /app /tmp/matplotlib

WORKDIR /app

COPY --from=builder --chown=app:app /opt/venv /opt/venv
COPY --chown=app:app src/cifar_cnn ./src/cifar_cnn
COPY --chown=app:app models/bundles/simple_cnn-1.0.1 ./models/bundles/simple_cnn-1.0.1
COPY --chown=app:app configs/serve ./configs/serve

# Ensure package is importable without writable site-packages installs.
ENV PYTHONPATH=/app/src

USER 10001:10001

EXPOSE 8000

# Preload path is MODEL_BUNDLE_PATH; readiness fails closed if verify fails.
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["uvicorn", "cifar_cnn.api.app:app_factory", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
