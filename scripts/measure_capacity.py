#!/usr/bin/env python3
"""Measure or synthesize serve capacity recommendations for Release C.

Prefer live HTTP measurements when --base-url is reachable; otherwise emit a
documented synthetic envelope from local FakeCIFAR-style inference timings.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import httpx
import torch
from PIL import Image

from cifar_cnn.api.runtime import ModelRuntime
from cifar_cnn.api.service import predict_image
from cifar_cnn.inference.bundle import pack_bundle
from cifar_cnn.models.simple_cnn import SimpleCNN

REPO = Path(__file__).resolve().parents[1]


def _png_bytes() -> bytes:
    import io

    buf = io.BytesIO()
    Image.new("RGB", (32, 32), (12, 24, 36)).save(buf, format="PNG")
    return buf.getvalue()


def measure_live(base_url: str, token: str, iterations: int) -> dict[str, float]:
    latencies: list[float] = []
    errors = 0
    payload = _png_bytes()
    headers = {"Authorization": f"Bearer {token}"}
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        ready = client.get("/ready")
        ready.raise_for_status()
        for _ in range(iterations):
            started = time.perf_counter()
            resp = client.post(
                "/v1/predict",
                headers=headers,
                files={"file": ("x.png", payload, "image/png")},
            )
            elapsed_ms = (time.perf_counter() - started) * 1000
            if resp.status_code != 200:
                errors += 1
            else:
                latencies.append(elapsed_ms)
    return _summarize(latencies, errors, iterations)


def measure_inprocess(iterations: int, workdir: Path) -> dict[str, float]:
    bundle = workdir / "capacity-bundle"
    pack_bundle(
        SimpleCNN(),
        bundle,
        bundle_id="capacity",
        version="0.0.1",
        run_parity=False,
    )
    runtime = ModelRuntime()
    loaded = runtime.load_bundle(bundle)
    image = Image.new("RGB", (32, 32), (12, 24, 36))
    # Warmup
    predict_image(loaded, image, top_k=3, request_id="warmup")
    latencies: list[float] = []
    errors = 0
    for i in range(iterations):
        started = time.perf_counter()
        try:
            predict_image(loaded, image, top_k=3, request_id=f"cap-{i}")
            latencies.append((time.perf_counter() - started) * 1000)
        except Exception:  # noqa: BLE001 — capacity probe
            errors += 1
    return _summarize(latencies, errors, iterations)


def _summarize(latencies: list[float], errors: int, iterations: int) -> dict[str, float]:
    if not latencies:
        return {
            "iterations": float(iterations),
            "errors": float(errors),
            "p50_ms": float("nan"),
            "p95_ms": float("nan"),
            "mean_ms": float("nan"),
            "throughput_rps": 0.0,
        }
    ordered = sorted(latencies)
    p95_idx = max(0, int(0.95 * (len(ordered) - 1)))
    mean = statistics.fmean(ordered)
    return {
        "iterations": float(iterations),
        "errors": float(errors),
        "p50_ms": float(statistics.median(ordered)),
        "p95_ms": float(ordered[p95_idx]),
        "mean_ms": float(mean),
        "throughput_rps": float(1000.0 / mean) if mean > 0 else 0.0,
    }


def recommend(metrics: dict[str, float], *, workers: int = 1) -> dict[str, object]:
    """Map measured latency to conservative CPU requests/limits for 1 replica."""
    p95 = metrics.get("p95_ms") or 50.0
    # SimpleCNN CPU inference is light; leave headroom for uvicorn + torch init.
    cpu_request = "250m"
    cpu_limit = "1000m"
    memory_request = "512Mi"
    memory_limit = "2Gi"
    if p95 > 200:
        cpu_request = "500m"
        cpu_limit = "1500m"
        memory_request = "1Gi"
    return {
        "replicas": 1,
        "workers": workers,
        "resources": {
            "requests": {"cpu": cpu_request, "memory": memory_request},
            "limits": {"cpu": cpu_limit, "memory": memory_limit},
        },
        "notes": [
            "Derived from local/smoke measurement; re-benchmark on target hardware before prod.",
            "Deploy images by digest only; mutable tags are forbidden for promotion.",
            "Torch stack CVEs remain under CYB-07 until upgrade; image rebuild SLA applies.",
        ],
        "startup_budget_sec": 45,
        "target_p95_ms": 100,
        "observed_p95_ms": p95,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="")
    parser.add_argument("--token", default="")
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO / "docs" / "evidence" / "release-c" / "phase-12-capacity.json",
    )
    args = parser.parse_args()

    mode = "inprocess"
    if args.base_url:
        if not args.token:
            raise SystemExit("--token required with --base-url")
        metrics = measure_live(args.base_url.rstrip("/"), args.token, args.iterations)
        mode = "live"
    else:
        work = REPO / "artifacts" / "capacity_smoke"
        work.mkdir(parents=True, exist_ok=True)
        metrics = measure_inprocess(args.iterations, work)

    payload = {
        "phase": 12,
        "mode": mode,
        "torch": torch.__version__,
        "metrics": metrics,
        "recommendation": recommend(metrics),
        "generated_utc_hint": "local measurement; CI may refresh on image workflow",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
