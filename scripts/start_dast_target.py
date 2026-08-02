#!/usr/bin/env python3
"""Start a local inference API for DAST (ZAP baseline) against an ephemeral bundle."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _wait_ready(url: str, timeout_sec: float) -> None:
    deadline = time.time() + timeout_sec
    last_err = ""
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:  # noqa: S310 — local DAST only
                if resp.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = str(exc)
        time.sleep(0.5)
    raise RuntimeError(f"DAST target not ready at {url}: {last_err}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--ready-timeout", type=float, default=120.0)
    args = parser.parse_args(argv)

    sys.path.insert(0, str(ROOT / "src"))
    from cifar_cnn.inference.bundle import pack_bundle  # noqa: E402
    from cifar_cnn.models.simple_cnn import SimpleCNN  # noqa: E402

    tmp = Path(tempfile.mkdtemp(prefix="cifar-dast-"))
    bundle = tmp / "bundle"
    pack_bundle(SimpleCNN(), bundle, bundle_id="dast", version="0.0.1", run_parity=False)

    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": str(ROOT / "src"),
            "APP_ENV": "development",
            "CIFAR_CNN_OIDC_MODE": "static",
            "OIDC_ISSUER": "https://cifar-cnn.local/dast",
            "OIDC_AUDIENCE": "cifar-cnn-api",
            "CIFAR_CNN_OIDC_HS256_SECRET": "cifar-cnn-dast-hs256-not-for-production",
            "CIFAR_CNN_ALLOW_ANON_PREDICT": "false",
            "MODEL_BUNDLE_PATH": str(bundle),
            "CIFAR_CNN_MAX_UPLOAD_BYTES": "1000000",
            "CIFAR_CNN_RATE_LIMIT_PER_MIN": "120",
            "CIFAR_CNN_PREDICT_TIMEOUT_SEC": "10",
            "CIFAR_CNN_TOP_K_MAX": "5",
            "CIFAR_CNN_AUTH_READY": "false",
        }
    )

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "cifar_cnn.api.app:app_factory",
        "--factory",
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--log-level",
        "warning",
    ]
    proc = subprocess.Popen(cmd, cwd=ROOT, env=env)  # noqa: S603
    ready = f"http://{args.host}:{args.port}/health"
    try:
        _wait_ready(ready, args.ready_timeout)
        print(f"dast_target_ready url={ready} pid={proc.pid}", flush=True)
        # Stay up until CI stops the job or sends SIGTERM.
        proc.wait()
        return int(proc.returncode or 0)
    except Exception:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        raise


if __name__ == "__main__":
    raise SystemExit(main())
