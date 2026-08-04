#!/usr/bin/env python3
"""Rigorous evaluation: accuracy, P/R/F1, confusion, ROC-AUC, ECE.

Default ``--smoke`` uses FakeCIFAR for CI. ``--live`` uses real CIFAR-10
(50k train / 10k locked official test) with an optional checkpoint.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Subset
from torchvision.datasets import CIFAR10

from cifar_cnn.evaluation.gradcam import GradCAM, resolve_target_layer, save_gradcam_overlay
from cifar_cnn.evaluation.plots import save_confusion_heatmap, save_roc_curves
from cifar_cnn.evaluation.rigorous import (
    collect_predictions,
    compute_rigorous_metrics,
    write_rigorous_metrics,
)
from cifar_cnn.evaluation.robustness import run_robustness_suite, write_robustness_report
from cifar_cnn.evaluation.safety import policy_summary
from cifar_cnn.models.improved_cnn import ImprovedCNN
from cifar_cnn.models.resnet_transfer import build_resnet18_cifar
from cifar_cnn.models.simple_cnn import SimpleCNN, load_state_dict
from cifar_cnn.training.trainer import build_criterion, build_optimizer, train_step


def _build_model(name: str) -> torch.nn.Module:
    if name == "ImprovedCNN":
        return ImprovedCNN(batch_norm=True, dropout=True, dropout_p=0.3)
    if name == "ResNet18CIFAR":
        return build_resnet18_cifar(pretrained=False, freeze_mode="none")
    if name == "SimpleCNN":
        return SimpleCNN()
    raise SystemExit(
        f"Unsupported --model {name!r}; use SimpleCNN, ImprovedCNN, or ResNet18CIFAR"
    )


def _smoke_loaders() -> tuple[DataLoader, DataLoader, object]:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "tests" / "unit"))
    from fake_cifar import FakeCIFAR10

    train = Subset(FakeCIFAR10(train=True), list(range(128)))
    eval_ds = Subset(FakeCIFAR10(train=True), list(range(128, 256)))
    trainloader = DataLoader(train, batch_size=16, shuffle=True)
    evalloader = DataLoader(eval_ds, batch_size=16, shuffle=False)
    return trainloader, evalloader, eval_ds


def _live_loaders(
    batch_size: int, *, normalize: str = "guide"
) -> tuple[DataLoader, DataLoader, object]:
    from cifar_cnn.data.loaders import GuideDataConfig, resolve_data_root
    from cifar_cnn.data.transforms import build_eval_transform, build_guide_transform

    if normalize not in {"guide", "imagenet"}:
        raise SystemExit("--normalize must be 'guide' or 'imagenet'")
    cfg = GuideDataConfig(root="./data", batch_size=batch_size, download=True)
    root = str(resolve_data_root(cfg.root))
    # Eval/test must match training normalize; never augment.
    eval_tf = build_eval_transform(normalize=normalize)  # type: ignore[arg-type]
    train_tf = build_guide_transform(normalize=normalize)  # type: ignore[arg-type]
    trainset = CIFAR10(root=root, train=True, download=cfg.download, transform=train_tf)
    testset = CIFAR10(root=root, train=False, download=False, transform=eval_tf)
    trainloader = DataLoader(trainset, batch_size=batch_size, shuffle=False)
    testloader = DataLoader(testset, batch_size=batch_size, shuffle=False)
    return trainloader, testloader, testset


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use real CIFAR-10 (50k train / 10k official test)",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="FakeCIFAR smoke path (default if neither --live nor --smoke)",
    )
    parser.add_argument(
        "--checkpoint",
        default="",
        help="State-dict or full checkpoint path for --live",
    )
    parser.add_argument(
        "--model",
        default="SimpleCNN",
        choices=["SimpleCNN", "ImprovedCNN", "ResNet18CIFAR"],
        help="Architecture matching the checkpoint",
    )
    parser.add_argument(
        "--normalize",
        default="guide",
        choices=["guide", "imagenet"],
        help="Must match training normalize (imagenet for ResNet transfer)",
    )
    parser.add_argument(
        "--tta",
        action="store_true",
        help="Horizontal-flip test-time augmentation (average softmax)",
    )
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument(
        "--out-dir",
        default="",
        help="Evidence directory (default: release-b or artifacts/baseline_rigorous)",
    )
    parser.add_argument("--skip-gradcam", action="store_true")
    parser.add_argument("--skip-robustness", action="store_true")
    args = parser.parse_args()

    live = bool(args.live)
    if not live and not args.smoke:
        args.smoke = True

    if live:
        out = Path(args.out_dir or "artifacts/baseline_rigorous")
        trainloader, evalloader, eval_ds = _live_loaders(
            args.batch_size, normalize=args.normalize
        )
        split_note = {
            "dataset": "CIFAR10",
            "total_images": 60_000,
            "train_size": 50_000,
            "test_size": 10_000,
            "eval_split": "official_test_locked",
            "official_test_locked": True,
            "normalize": args.normalize,
        }
    else:
        out = Path(args.out_dir or "docs/evidence/release-b")
        trainloader, evalloader, eval_ds = _smoke_loaders()
        split_note = {"dataset": "FakeCIFAR10", "eval_split": "smoke_subset"}

    out.mkdir(parents=True, exist_ok=True)
    device = torch.device("cpu")
    model = _build_model(args.model)
    crit = build_criterion()

    if live:
        if not args.checkpoint:
            raise SystemExit("--live requires --checkpoint <state_dict.pth>")
        ckpt = Path(args.checkpoint)
        if not ckpt.is_file():
            hint = ""
            if "transfer_live" in str(ckpt).replace("\\", "/"):
                hint = (
                    "\nResNet transfer weights are missing. Train on a GPU host first:\n"
                    "  python scripts/train_transfer_live.py --device cuda\n"
                    "Or use the Colab notebook notebooks/colab_transfer_gpu.ipynb, then place\n"
                    "model_best.pth under artifacts/transfer_live/.\n"
                    "CPU champion (available now):\n"
                    "  python scripts/evaluate_rigorous.py --live --model ImprovedCNN "
                    "--checkpoint artifacts/improved_boost/model_best.pth "
                    "--out-dir artifacts/improved_boost_rigorous_tta --tta"
                )
            raise SystemExit(f"Model artifact not found: {ckpt}{hint}")
        load_state_dict(model, ckpt)
    else:
        opt = build_optimizer(model)
        model.train()
        for i, batch in enumerate(trainloader):
            if i >= 5:
                break
            train_step(model, batch, crit, opt, device)

    preds, avg_loss = collect_predictions(
        model,
        evalloader,
        criterion=crit,
        max_batches=None if live else 8,
        tta_flip=bool(args.tta),
    )
    metrics = compute_rigorous_metrics(preds, avg_loss=avg_loss)
    metrics_path = write_rigorous_metrics(out / "metrics.json", metrics)
    if not live:
        write_rigorous_metrics(out / "phase-08-metrics.json", metrics)

    cm_path = save_confusion_heatmap(
        metrics.confusion, out / ("phase-08-confusion.png" if not live else "confusion.png")
    )
    roc_path = save_roc_curves(
        preds.labels,
        preds.probs,
        out / ("phase-08-roc.png" if not live else "roc_curves.png"),
    )

    summary = {
        "split": split_note,
        "model": args.model,
        "normalize": args.normalize,
        "tta_flip": bool(args.tta),
        "checkpoint": args.checkpoint or None,
        "n_samples": metrics.n_samples,
        "accuracy": metrics.accuracy,
        "avg_loss": metrics.avg_loss,
        "macro_precision": metrics.macro_precision,
        "macro_recall": metrics.macro_recall,
        "macro_f1": metrics.macro_f1,
        "weighted_precision": metrics.weighted_precision,
        "weighted_recall": metrics.weighted_recall,
        "weighted_f1": metrics.weighted_f1,
        "roc_auc_macro": metrics.roc_auc_macro,
        "ece": metrics.ece,
        "per_class": {k: vars(v) for k, v in metrics.per_class.items()},
        "artifacts": {
            "metrics": str(metrics_path),
            "confusion": str(cm_path),
            "roc": str(roc_path),
        },
        "notes": metrics.notes,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    if not args.skip_robustness:
        rob = run_robustness_suite(model)
        write_robustness_report(
            out / ("phase-08-robustness.json" if not live else "robustness.json"), rob
        )

    if not args.skip_gradcam:
        try:
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
                    out / ("phase-08-gradcam-pred.png" if not live else "gradcam_pred.png"),
                    title=f"pred={pred0} actual={y0}",
                )
                other = (int(y0) + 1) % 10
                r1 = cam(x, class_idx=other)
                save_gradcam_overlay(
                    x0,
                    r1,
                    out
                    / ("phase-08-gradcam-alt-class.png" if not live else "gradcam_alt.png"),
                    title=f"alt_class={other} actual={y0}",
                )
            finally:
                cam.close()
        except Exception as exc:  # pragma: no cover - best-effort evidence
            (out / "gradcam_skip.txt").write_text(str(exc) + "\n", encoding="utf-8")

    policy_path = out / ("phase-08-safety-policy.json" if not live else "safety_policy.json")
    policy_path.write_text(json.dumps(policy_summary(), indent=2) + "\n", encoding="utf-8")

    print(f"Wrote rigorous evidence under {out}")
    print(
        f"n={metrics.n_samples} accuracy={metrics.accuracy:.4f} "
        f"macro_P={metrics.macro_precision:.4f} macro_R={metrics.macro_recall:.4f} "
        f"macro_F1={metrics.macro_f1:.4f} roc_auc_macro={metrics.roc_auc_macro} "
        f"ece={metrics.ece:.4f}"
    )
    print("Per-class precision / recall / F1:")
    for name, scores in metrics.per_class.items():
        print(
            f"  {name:12s} P={scores.precision:.3f} R={scores.recall:.3f} "
            f"F1={scores.f1:.3f} support={scores.support}"
        )


if __name__ == "__main__":
    main()
