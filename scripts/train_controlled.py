#!/usr/bin/env python3
"""CLI for Release B controlled training (checkpoints, early stop, tracking)."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

from torch.utils.data import DataLoader, Subset

from cifar_cnn.models.simple_cnn import SimpleCNN
from cifar_cnn.training.config import load_controlled_config
from cifar_cnn.training.controlled import controlled_train_loop, worker_init_fn


def _fake_loaders(batch_size: int, train_n: int = 256, val_n: int = 128):
    unit = Path(__file__).resolve().parents[1] / "tests" / "unit"
    if str(unit) not in sys.path:
        sys.path.insert(0, str(unit))
    from fake_cifar import FakeCIFAR10

    trainset = FakeCIFAR10(train=True)
    train_subset = Subset(trainset, list(range(train_n)))
    val_subset = Subset(trainset, list(range(train_n, train_n + val_n)))
    trainloader = DataLoader(
        train_subset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
        worker_init_fn=worker_init_fn,
    )
    valloader = DataLoader(
        val_subset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )
    return trainloader, valloader


def main() -> None:
    parser = argparse.ArgumentParser(description="Controlled training loop")
    parser.add_argument("--config", default="configs/train/controlled.yaml")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--resume-from", default="")
    args = parser.parse_args()

    cfg = load_controlled_config(args.config)
    if args.smoke:
        cfg = replace(
            cfg,
            epochs=3,
            smoke_max_batches=2,
            log_every_n_batches=1,
            artifact_dir="artifacts/controlled_smoke",
            run_id="controlled-smoke",
            early_stop_patience=5,
        )
    if args.resume_from:
        cfg = replace(cfg, resume_from=args.resume_from)

    trainloader, valloader = _fake_loaders(cfg.batch_size)
    result = controlled_train_loop(
        SimpleCNN(), trainloader, cfg, valloader=valloader
    )
    print(
        f"epochs_trained={result.epochs_trained} best={result.best_metric:.6f} "
        f"early_stopped={result.early_stopped}"
    )
    print(f"last={result.last_checkpoint}")
    print(f"best={result.best_checkpoint}")


if __name__ == "__main__":
    main()
