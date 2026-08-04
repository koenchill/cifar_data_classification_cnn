#!/usr/bin/env python3
"""CLI for controlled training (checkpoints, early stop, tracking).

Examples:
  # CI / protocol smoke (FakeCIFAR)
  python scripts/train_controlled.py --smoke

  # ImprovedCNN + aug on locked 45k/5k split
  python scripts/train_controlled.py --config configs/train/improved_full.yaml --live

  # ResNet18 ImageNet transfer (prefer scripts/train_transfer_live.py for 2-stage)
  python scripts/train_controlled.py --config configs/train/transfer_full.yaml --live
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Subset

from cifar_cnn.models.improved_cnn import ImprovedCNN
from cifar_cnn.models.resnet_transfer import build_resnet18_cifar
from cifar_cnn.models.simple_cnn import SimpleCNN, save_state_dict
from cifar_cnn.training.config import ControlledTrainConfig, load_controlled_config
from cifar_cnn.training.controlled import controlled_train_loop, worker_init_fn


def _build_model(cfg: ControlledTrainConfig) -> torch.nn.Module:
    if cfg.model == "ImprovedCNN":
        return ImprovedCNN(
            batch_norm=cfg.batch_norm,
            dropout=cfg.dropout,
            dropout_p=cfg.dropout_p,
        )
    if cfg.model == "ResNet18CIFAR":
        return build_resnet18_cifar(
            pretrained=cfg.pretrained,
            freeze_mode=cfg.freeze_mode,  # type: ignore[arg-type]
        )
    return SimpleCNN()


def _fake_loaders(cfg: ControlledTrainConfig, train_n: int = 256, val_n: int = 128):
    unit = Path(__file__).resolve().parents[1] / "tests" / "unit"
    if str(unit) not in sys.path:
        sys.path.insert(0, str(unit))
    from fake_cifar import FakeCIFAR10

    from cifar_cnn.models.ablation import TensorTrainAugmentDataset

    trainset = FakeCIFAR10(train=True)
    train_base = Subset(trainset, list(range(train_n)))
    val_subset = Subset(trainset, list(range(train_n, train_n + val_n)))
    train_ds = TensorTrainAugmentDataset(train_base, augment=cfg.train_augment)
    trainloader = DataLoader(
        train_ds,
        batch_size=cfg.batch_size,
        shuffle=True,
        num_workers=0,
        worker_init_fn=worker_init_fn,
    )
    valloader = DataLoader(
        val_subset,
        batch_size=cfg.batch_size,
        shuffle=False,
        num_workers=0,
    )
    meta = {
        "dataset": "FakeCIFAR10",
        "train_size": train_n,
        "val_size": val_n,
        "train_augment": cfg.train_augment,
        "normalize": cfg.normalize,
    }
    return trainloader, valloader, meta


def _live_loaders(cfg: ControlledTrainConfig):
    from cifar_cnn.data.loaders import GuideDataConfig, build_train_val_loaders_from_manifest

    data_cfg = GuideDataConfig(
        root=cfg.data_root,
        batch_size=cfg.batch_size,
        download=True,
        num_workers=0,
    )
    return build_train_val_loaders_from_manifest(
        data_cfg,
        split_manifest=cfg.split_manifest,
        train_augment=cfg.train_augment,
        color_jitter=cfg.color_jitter,
        cutout=cfg.cutout,
        cutout_p=cfg.cutout_p,
        normalize=cfg.normalize,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Controlled training loop")
    parser.add_argument("--config", default="configs/train/controlled.yaml")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use real CIFAR-10 train pool + locked split manifest (not FakeCIFAR)",
    )
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--resume-from", default="")
    parser.add_argument(
        "--epochs",
        type=int,
        default=0,
        help="Override config epochs (0 = use config)",
    )
    parser.add_argument(
        "--device",
        default="",
        choices=["", "cpu", "cuda"],
        help="Override config device (cuda requires CUDA-enabled torch)",
    )
    args = parser.parse_args()

    cfg = load_controlled_config(args.config)
    if args.device:
        if args.device == "cuda" and not torch.cuda.is_available():
            raise SystemExit(
                "CUDA requested but torch.cuda.is_available() is False. "
                "Install CUDA PyTorch or use --device cpu."
            )
        cfg = replace(cfg, device=args.device)
    if args.smoke:
        cfg = replace(
            cfg,
            epochs=3 if args.epochs <= 0 else args.epochs,
            smoke_max_batches=2,
            log_every_n_batches=1,
            artifact_dir="artifacts/controlled_smoke"
            if cfg.artifact_dir == "artifacts/controlled"
            else f"{cfg.artifact_dir}_smoke",
            run_id=f"{cfg.run_id}-smoke",
            early_stop_patience=5,
            pretrained=False if cfg.model == "ResNet18CIFAR" else cfg.pretrained,
        )
    elif args.epochs > 0:
        cfg = replace(cfg, epochs=args.epochs)
    if args.resume_from:
        cfg = replace(cfg, resume_from=args.resume_from)

    if args.live:
        trainloader, valloader, data_meta = _live_loaders(cfg)
    else:
        trainloader, valloader, data_meta = _fake_loaders(cfg)

    model = _build_model(cfg)
    result = controlled_train_loop(model, trainloader, cfg, valloader=valloader)

    export_path = Path(cfg.artifact_dir) / cfg.export_state_dict
    save_state_dict(model, export_path)

    record = {
        "config_file": args.config,
        "model": cfg.model,
        "pretrained": cfg.pretrained,
        "freeze_mode": cfg.freeze_mode,
        "normalize": cfg.normalize,
        "optimizer": cfg.optimizer,
        "weight_decay": cfg.weight_decay,
        "label_smoothing": cfg.label_smoothing,
        "scheduler": cfg.scheduler,
        "train_augment": cfg.train_augment,
        "color_jitter": cfg.color_jitter,
        "cutout": cfg.cutout,
        "init_weights": cfg.init_weights,
        "data": data_meta,
        "epochs_trained": result.epochs_trained,
        "best_val_loss": result.best_metric,
        "early_stopped": result.early_stopped,
        "best_checkpoint": result.best_checkpoint,
        "last_checkpoint": result.last_checkpoint,
        "export_state_dict": str(export_path),
        "history": result.history,
    }
    record_path = Path(cfg.artifact_dir) / "run_record.json"
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    print(
        f"epochs_trained={result.epochs_trained} best_val_loss={result.best_metric:.6f} "
        f"early_stopped={result.early_stopped}"
    )
    print(f"last={result.last_checkpoint}")
    print(f"best={result.best_checkpoint}")
    print(f"export_state_dict={export_path}")
    print(f"run_record={record_path}")


if __name__ == "__main__":
    main()
