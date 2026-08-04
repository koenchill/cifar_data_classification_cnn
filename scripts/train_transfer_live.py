#!/usr/bin/env python3
"""Two-stage ResNet18 ImageNet -> CIFAR-10 fine-tune (locked 45k/5k).

Stage 1: freeze backbone, train FC head.
Stage 2: unfreeze all; early-stop on val. Official 10k test is never used.

GPU (recommended):
  python scripts/train_transfer_live.py --device cuda

CPU fallback (slow):
  python scripts/train_transfer_live.py --device cpu

After completion:
  python scripts/evaluate_rigorous.py --live --model ResNet18CIFAR \\
    --normalize imagenet --checkpoint artifacts/transfer_live/model_best.pth \\
    --out-dir artifacts/transfer_rigorous --tta
"""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

import torch

from cifar_cnn.data.loaders import GuideDataConfig, build_train_val_loaders_from_manifest
from cifar_cnn.models.resnet_transfer import build_resnet18_cifar, set_freeze_mode
from cifar_cnn.models.simple_cnn import load_state_dict, save_state_dict
from cifar_cnn.training.config import ControlledTrainConfig, load_controlled_config
from cifar_cnn.training.controlled import controlled_train_loop


def _resolve_device(requested: str) -> str:
    if requested == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if requested == "cuda" and not torch.cuda.is_available():
        raise SystemExit(
            "CUDA requested but torch.cuda.is_available() is False. "
            "Install a CUDA build of PyTorch (see https://pytorch.org/get-started/locally/) "
            "or pass --device cpu."
        )
    return requested


def _apply_device(cfg: ControlledTrainConfig, device: str) -> ControlledTrainConfig:
    return replace(cfg, device=device)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Training device (auto picks cuda when available)",
    )
    parser.add_argument(
        "--stage1-config",
        default="",
        help="Override stage-1 YAML (default: GPU or CPU transfer_stage1*.yaml)",
    )
    parser.add_argument(
        "--stage2-config",
        default="",
        help="Override stage-2 YAML (default: GPU or CPU transfer_stage2*.yaml)",
    )
    parser.add_argument(
        "--skip-stage1",
        action="store_true",
        help="Load --init-checkpoint and jump to stage 2",
    )
    parser.add_argument("--init-checkpoint", default="")
    parser.add_argument("--stage1-epochs", type=int, default=0)
    parser.add_argument("--stage2-epochs", type=int, default=0)
    args = parser.parse_args()

    device = _resolve_device(args.device)
    if device == "cuda":
        print(f"device=cuda name={torch.cuda.get_device_name(0)}")
    else:
        print("device=cpu")

    stage1_path = args.stage1_config or (
        "configs/train/transfer_stage1_gpu.yaml"
        if device == "cuda"
        else "configs/train/transfer_stage1.yaml"
    )
    stage2_path = args.stage2_config or (
        "configs/train/transfer_stage2_gpu.yaml"
        if device == "cuda"
        else "configs/train/transfer_stage2.yaml"
    )

    s1 = _apply_device(load_controlled_config(stage1_path), device)
    data_cfg = GuideDataConfig(
        root=s1.data_root,
        batch_size=s1.batch_size,
        download=True,
        num_workers=0,
    )
    trainloader, valloader, meta = build_train_val_loaders_from_manifest(
        data_cfg,
        split_manifest=s1.split_manifest,
        train_augment=True,
        color_jitter=True,
        cutout=s1.cutout,
        cutout_p=s1.cutout_p,
        normalize="imagenet",
    )
    print(f"data={meta}")
    print(f"stage1_config={stage1_path}")
    print(f"stage2_config={stage2_path}")

    if args.skip_stage1:
        if not args.init_checkpoint:
            raise SystemExit("--skip-stage1 requires --init-checkpoint")
        model = build_resnet18_cifar(pretrained=False, freeze_mode="none")
        load_state_dict(model, args.init_checkpoint)
        export1 = Path(args.init_checkpoint)
    else:
        model = build_resnet18_cifar(pretrained=True, freeze_mode="backbone")
        cfg1 = _apply_device(load_controlled_config(stage1_path), device)
        if args.stage1_epochs > 0:
            cfg1 = replace(cfg1, epochs=args.stage1_epochs)
        result1 = controlled_train_loop(model, trainloader, cfg1, valloader=valloader)
        export1 = Path(cfg1.artifact_dir) / cfg1.export_state_dict
        save_state_dict(model, export1)
        (Path(cfg1.artifact_dir) / "run_record.json").write_text(
            json.dumps(
                {
                    "stage": 1,
                    "device": device,
                    "best_val_loss": result1.best_metric,
                    "epochs_trained": result1.epochs_trained,
                    "early_stopped": result1.early_stopped,
                    "export_state_dict": str(export1),
                    "history": result1.history,
                    "data": meta,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(
            f"[stage1] epochs={result1.epochs_trained} "
            f"best_val_loss={result1.best_metric:.6f} export={export1}"
        )

    set_freeze_mode(model, "none")
    cfg2 = _apply_device(load_controlled_config(stage2_path), device)
    if args.stage2_epochs > 0:
        cfg2 = replace(cfg2, epochs=args.stage2_epochs)
    result2 = controlled_train_loop(model, trainloader, cfg2, valloader=valloader)
    export2 = Path(cfg2.artifact_dir) / cfg2.export_state_dict
    save_state_dict(model, export2)

    final = Path("artifacts/transfer_live/model_best.pth")
    final.parent.mkdir(parents=True, exist_ok=True)
    save_state_dict(model, final)

    summary = {
        "device": device,
        "stage1_config": stage1_path,
        "stage2_config": stage2_path,
        "stage1_export": str(export1),
        "stage2_export": str(export2),
        "final_export": str(final),
        "best_val_loss": result2.best_metric,
        "epochs_trained": result2.epochs_trained,
        "early_stopped": result2.early_stopped,
        "history": result2.history,
        "data": meta,
        "eval_hint": (
            "python scripts/evaluate_rigorous.py --live --model ResNet18CIFAR "
            f"--normalize imagenet --checkpoint {final} "
            "--out-dir artifacts/transfer_rigorous --tta"
        ),
    }
    (Path(cfg2.artifact_dir) / "run_record.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    (final.parent / "run_record.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"[stage2] epochs={result2.epochs_trained} "
        f"best_val_loss={result2.best_metric:.6f} export={export2}"
    )
    print(f"final_export={final}")
    print(summary["eval_hint"])


if __name__ == "__main__":
    main()
