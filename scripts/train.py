#!/usr/bin/env python3
"""CLI for guide baseline training."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
import yaml
from torch.utils.data import DataLoader, TensorDataset

from cifar_cnn.training import (
    TrainConfig,
    create_baseline_model,
    set_seed,
    train_loop,
    write_run_record,
)


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _synthetic_loader(batch_size: int, n: int = 64) -> DataLoader:
    """Tiny CIFAR-shaped loader for smoke/CI (no download)."""
    images = torch.zeros(n, 3, 32, 32)
    labels = torch.arange(n) % 10
    return DataLoader(TensorDataset(images, labels), batch_size=batch_size, shuffle=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train guide-baseline SimpleCNN")
    parser.add_argument(
        "--config",
        default="configs/train/baseline.yaml",
        help="Path to training config YAML",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Short CPU smoke run (1 epoch, few batches; synthetic data)",
    )
    parser.add_argument(
        "--synthetic",
        action="store_true",
        help="Force synthetic TensorDataset loaders (no download)",
    )
    args = parser.parse_args()

    cfg_path = Path(args.config)
    raw = _load_yaml(cfg_path)
    smoke_batches = 3 if args.smoke else raw.get("smoke_max_batches")
    epochs = 1 if args.smoke else int(raw["epochs"])
    artifact_dir = (
        "artifacts/baseline_smoke"
        if args.smoke
        else str(raw.get("artifact_dir", "artifacts/baseline"))
    )
    train_cfg = TrainConfig(
        epochs=epochs,
        lr=float(raw["lr"]),
        batch_size=int(raw["batch_size"]),
        seed=int(raw.get("seed", 42)),
        device=str(raw.get("device", "cpu")),
        log_every_n_batches=1 if args.smoke else int(raw.get("log_every_n_batches", 100)),
        smoke_max_batches=smoke_batches,
        artifact_dir=artifact_dir,
    )

    set_seed(train_cfg.seed)

    use_synthetic = args.synthetic or args.smoke
    if use_synthetic:
        trainloader = _synthetic_loader(train_cfg.batch_size)
        data_note = {"dataset": "TensorDataset", "split": "synthetic-smoke"}
    else:
        from cifar_cnn.data.loaders import (
            GuideDataConfig,
            build_guide_loaders,
            load_cifar10_datasets,
        )

        data_cfg = GuideDataConfig(
            root="./data",
            batch_size=train_cfg.batch_size,
            download=True,
        )
        trainset, testset = load_cifar10_datasets(data_cfg)
        trainloader, _testloader = build_guide_loaders(
            data_cfg, train_subset=trainset, test_subset=testset
        )
        data_note = {
            "dataset": "CIFAR10",
            "root": "./data",
            "train_size": len(trainset),
            "test_size": len(testset),
            "official_test_locked": True,
        }

    model = create_baseline_model()
    result = train_loop(model, trainloader, train_cfg)
    record_path = Path(train_cfg.artifact_dir) / "run_record.json"
    write_run_record(
        record_path,
        config=train_cfg,
        result=result,
        extra={"data": data_note, "config_file": str(cfg_path)},
    )
    print(f"Training complete. Checkpoint: {result.final_checkpoint}")
    print(f"Run record: {record_path}")
    print(f"Elapsed sec: {result.elapsed_sec:.3f}")


if __name__ == "__main__":
    main()
