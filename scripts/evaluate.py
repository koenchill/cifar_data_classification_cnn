#!/usr/bin/env python3
"""CLI for guide baseline evaluation, gallery, and model persistence."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from cifar_cnn.data.loaders import GuideDataConfig, build_guide_loaders, load_cifar10_datasets
from cifar_cnn.evaluation import (
    evaluate_accuracy,
    save_baseline_model,
    save_prediction_gallery,
    write_metrics,
)
from cifar_cnn.models.simple_cnn import load_state_dict
from cifar_cnn.training import TrainConfig, create_baseline_model, set_seed, train_loop
from cifar_cnn.training.trainer import build_criterion


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _fake_loaders(batch_size: int = 32):
    """Leakage-safe FakeCIFAR10 loaders (official test size = 10,000)."""
    # Ensure repo-root tests package is importable when running as a script.
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from tests.unit.fake_cifar import FakeCIFAR10

    trainset = FakeCIFAR10(train=True)
    testset = FakeCIFAR10(train=False)
    return build_guide_loaders(
        GuideDataConfig(batch_size=batch_size, download=False),
        train_subset=trainset,
        test_subset=testset,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate guide-baseline SimpleCNN")
    parser.add_argument("--config", default="configs/train/baseline.yaml")
    parser.add_argument(
        "--checkpoint",
        default="",
        help="Optional state_dict path; if empty, short-trains then evaluates",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="FakeCIFAR10 + short train; still evaluates full 10k test split",
    )
    parser.add_argument("--artifact-dir", default="artifacts/baseline_eval")
    parser.add_argument(
        "--gallery-path",
        default="docs/evidence/release-a/baseline_gallery.png",
    )
    parser.add_argument(
        "--metrics-path",
        default="docs/evidence/release-a/baseline_metrics.json",
    )
    parser.add_argument("--skip-save", action="store_true")
    args = parser.parse_args()

    raw = _load_yaml(Path(args.config))
    set_seed(int(raw.get("seed", 42)))
    batch_size = int(raw.get("batch_size", 32))
    device = str(raw.get("device", "cpu"))

    if args.smoke:
        trainloader, testloader = _fake_loaders(batch_size)
        data_note = {"dataset": "FakeCIFAR10", "test_size": 10_000}
    else:
        data_cfg = GuideDataConfig(root="./data", batch_size=batch_size, download=True)
        trainset, testset = load_cifar10_datasets(data_cfg)
        trainloader, testloader = build_guide_loaders(
            data_cfg, train_subset=trainset, test_subset=testset
        )
        data_note = {
            "dataset": "CIFAR10",
            "test_size": len(testset),
            "official_test_locked": True,
        }

    model = create_baseline_model()
    if args.checkpoint:
        load_state_dict(model, args.checkpoint)
    else:
        train_cfg = TrainConfig(
            epochs=1,
            lr=float(raw["lr"]),
            batch_size=batch_size,
            seed=int(raw.get("seed", 42)),
            device=device,
            log_every_n_batches=50,
            smoke_max_batches=5 if args.smoke else 20,
            artifact_dir=str(Path(args.artifact_dir) / "train"),
        )
        train_loop(model, trainloader, train_cfg)

    result = evaluate_accuracy(
        model,
        testloader,
        device=device,
        criterion=build_criterion(),
        expected_total=10_000,
    )
    print(result.message)
    if result.avg_loss is not None:
        print(f"Average test loss (additive): {result.avg_loss:.4f}")

    metrics_path = write_metrics(
        args.metrics_path,
        result,
        extra={"data": data_note, "model": "SimpleCNN", "device": device},
    )
    gallery_path = save_prediction_gallery(
        model, testloader, args.gallery_path, device=device
    )
    art = Path(args.artifact_dir)
    write_metrics(art / "metrics.json", result, extra={"data": data_note})
    save_prediction_gallery(model, testloader, art / "gallery.png", device=device)

    if not args.skip_save:
        repo_path, guide_path = save_baseline_model(model)
        print(f"Repo model: {repo_path}")
        print(f"Guide model: {guide_path}")

    print(f"Metrics: {metrics_path}")
    print(f"Gallery: {gallery_path}")


if __name__ == "__main__":
    main()
