#!/usr/bin/env python3
"""Update overlay image digests for GitOps promotion (CI proposes; Argo reconciles)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OVERLAY_ROOT = ROOT / "deploy" / "kustomize" / "overlays"
DIGEST_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
IMAGE_BLOCK_RE = re.compile(
    r"(images:\n"
    r"  - name: ghcr\.io/koenchill/cifar_data_classification_cnn/api\n"
    r"    newName: ghcr\.io/koenchill/cifar_data_classification_cnn/api\n"
    r"    digest: )sha256:[a-f0-9]{64}",
    re.MULTILINE,
)


def update_overlay(env: str, digest: str) -> Path:
    path = OVERLAY_ROOT / env / "kustomization.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"missing overlay: {path}")
    text = path.read_text(encoding="utf-8")
    updated, n = IMAGE_BLOCK_RE.subn(rf"\g<1>{digest}", text, count=1)
    if n != 1:
        raise ValueError(f"could not locate pinned image digest block in {path}")
    path.write_text(updated, encoding="utf-8", newline="\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--digest", required=True, help="sha256:<64 hex> image digest")
    parser.add_argument(
        "--env",
        action="append",
        choices=("dev", "staging", "prod"),
        required=True,
        help="Overlay environment to update (repeatable)",
    )
    args = parser.parse_args(argv)
    digest = args.digest.strip()
    if not DIGEST_RE.match(digest):
        print(f"invalid digest: {digest}", file=sys.stderr)
        return 2
    for env in args.env:
        path = update_overlay(env, digest)
        print(f"updated {path.relative_to(ROOT)} -> {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
