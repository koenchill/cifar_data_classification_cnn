#!/usr/bin/env python3
"""Build the hardened API image using deploy/docker/dockerignore at repo root."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCKERFILE = ROOT / "deploy" / "docker" / "Dockerfile"
IGNORE_SRC = ROOT / "deploy" / "docker" / "dockerignore"
IGNORE_DST = ROOT / ".dockerignore"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default="cifar-cnn-api:local")
    parser.add_argument("--load", action="store_true", help="load into local docker (buildx)")
    args = parser.parse_args()

    if shutil.which("docker") is None:
        print("docker not found on PATH", file=sys.stderr)
        return 2

    created = False
    if not IGNORE_DST.exists():
        shutil.copyfile(IGNORE_SRC, IGNORE_DST)
        created = True
    else:
        # Prefer deploy/docker source of truth for this build.
        shutil.copyfile(IGNORE_SRC, IGNORE_DST)

    cmd = [
        "docker",
        "buildx",
        "build",
        "-f",
        str(DOCKERFILE),
        "-t",
        args.tag,
    ]
    if args.load:
        cmd.append("--load")
    cmd.append(str(ROOT))
    print(" ".join(cmd), flush=True)
    try:
        return subprocess.call(cmd)
    finally:
        if created and IGNORE_DST.exists():
            IGNORE_DST.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
