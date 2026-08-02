#!/usr/bin/env python3
"""Pack champion SimpleCNN into a signed Release B model bundle."""

from __future__ import annotations

import json
from pathlib import Path

import torch
from torch.utils.data import DataLoader, TensorDataset

from cifar_cnn.inference.bundle import (
    pack_bundle,
    set_current_pointer,
    verify_bundle,
)
from cifar_cnn.models.simple_cnn import SimpleCNN
from cifar_cnn.training.trainer import build_criterion, build_optimizer, train_step


def _tiny_train(model: SimpleCNN) -> SimpleCNN:
    x = torch.randn(64, 3, 32, 32)
    y = torch.randint(0, 10, (64,))
    loader = DataLoader(TensorDataset(x, y), batch_size=16, shuffle=True)
    opt = build_optimizer(model)
    crit = build_criterion()
    device = torch.device("cpu")
    model.train()
    for i, batch in enumerate(loader):
        train_step(model, batch, crit, opt, device)
        if i >= 3:
            break
    model.eval()
    return model


def main() -> None:
    evidence = Path("docs/evidence/release-b")
    evidence.mkdir(parents=True, exist_ok=True)
    bundles = Path("models/bundles")
    model = _tiny_train(SimpleCNN())

    # Keep prior version for rollback demo if present.
    v1_dir = bundles / "simple_cnn-1.0.0"
    v2_dir = bundles / "simple_cnn-1.0.1"
    if not v1_dir.exists():
        pack_bundle(
            model,
            v1_dir,
            bundle_id="simple_cnn",
            version="1.0.0",
            champion_id="simple_cnn_baseline",
            metrics_summary={"source": "phase-09-champion-decision"},
        )
    pack_bundle(
        model,
        v2_dir,
        bundle_id="simple_cnn",
        version="1.0.1",
        champion_id="simple_cnn_baseline",
        metrics_summary={"source": "phase-09-champion-decision", "patch": "1.0.1"},
    )
    set_current_pointer(bundles, v2_dir.name)
    verify_bundle(v2_dir)

    meta = json.loads((v2_dir / "metadata.json").read_text(encoding="utf-8"))
    parity = meta.get("onnx", {}).get("parity", {})
    (evidence / "phase-10-onnx-parity.json").write_text(
        json.dumps(parity, indent=2) + "\n", encoding="utf-8"
    )
    (evidence / "phase-10-bundle-manifest.json").write_text(
        (v2_dir / "manifest.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print(f"Packed {v2_dir}; CURRENT -> {v2_dir.name}")
    print(f"parity_passed={parity.get('passed')} max_abs_diff={parity.get('max_abs_diff')}")


if __name__ == "__main__":
    main()
