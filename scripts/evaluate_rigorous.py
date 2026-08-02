#!/usr/bin/env python3
"""Smoke CLI for Phase 08 rigorous evaluation evidence."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Subset

from cifar_cnn.evaluation.gradcam import GradCAM, resolve_target_layer, save_gradcam_overlay
from cifar_cnn.evaluation.plots import save_confusion_heatmap
from cifar_cnn.evaluation.rigorous import (
    collect_predictions,
    compute_rigorous_metrics,
    write_rigorous_metrics,
)
from cifar_cnn.evaluation.robustness import run_robustness_suite, write_robustness_report
from cifar_cnn.evaluation.safety import policy_summary
from cifar_cnn.models.simple_cnn import SimpleCNN
from cifar_cnn.training.trainer import build_criterion, build_optimizer, train_step


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "tests" / "unit"))
    from fake_cifar import FakeCIFAR10

    out = Path("docs/evidence/release-b")
    out.mkdir(parents=True, exist_ok=True)

    train = Subset(FakeCIFAR10(train=True), list(range(128)))
    eval_ds = Subset(FakeCIFAR10(train=True), list(range(128, 256)))
    trainloader = DataLoader(train, batch_size=16, shuffle=True)
    evalloader = DataLoader(eval_ds, batch_size=16, shuffle=False)

    model = SimpleCNN()
    opt = build_optimizer(model)
    crit = build_criterion()
    device = torch.device("cpu")
    model.train()
    for i, batch in enumerate(trainloader):
        if i >= 5:
            break
        train_step(model, batch, crit, opt, device)

    preds, avg_loss = collect_predictions(
        model, evalloader, criterion=crit, max_batches=8
    )
    metrics = compute_rigorous_metrics(preds, avg_loss=avg_loss)
    write_rigorous_metrics(out / "phase-08-metrics.json", metrics)
    save_confusion_heatmap(metrics.confusion, out / "phase-08-confusion.png")

    rob = run_robustness_suite(model)
    write_robustness_report(out / "phase-08-robustness.json", rob)

    # Grad-CAM for one correct-ish and one forced incorrect display case
    cam = GradCAM(model, resolve_target_layer(model))
    try:
        x0, y0 = eval_ds[0]
        x = x0.unsqueeze(0)
        with torch.no_grad():
            pred0 = int(model(x).argmax(dim=1).item())
        r0 = cam(x, class_idx=pred0)
        save_gradcam_overlay(
            x0,
            r0,
            out / "phase-08-gradcam-pred.png",
            title=f"pred={pred0} actual={y0}",
        )
        other = (int(y0) + 1) % 10
        r1 = cam(x, class_idx=other)
        save_gradcam_overlay(
            x0,
            r1,
            out / "phase-08-gradcam-alt-class.png",
            title=f"alt_class={other} actual={y0}",
        )
    finally:
        cam.close()

    (out / "phase-08-safety-policy.json").write_text(
        json.dumps(policy_summary(), indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote rigorous evidence under {out}")
    print(
        f"accuracy={metrics.accuracy:.3f} macro_f1={metrics.macro_f1:.3f} "
        f"ece={metrics.ece:.3f}"
    )


if __name__ == "__main__":
    main()
