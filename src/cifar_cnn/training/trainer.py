"""Guide baseline trainer (Steps 3–4) with corrected running-loss reporting."""

from __future__ import annotations

import json
import platform
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from torch import Tensor
from torch.optim import SGD, Adam, Optimizer
from torch.utils.data import DataLoader

from cifar_cnn.models.simple_cnn import SimpleCNN, save_state_dict


@dataclass(frozen=True)
class TrainConfig:
    epochs: int = 10
    lr: float = 0.001
    batch_size: int = 32
    seed: int = 42
    device: str = "cpu"
    log_every_n_batches: int = 100
    smoke_max_batches: int | None = None
    artifact_dir: str = "artifacts/baseline"


@dataclass
class TrainResult:
    loss_history: list[dict[str, float]] = field(default_factory=list)
    epoch_times_sec: list[float] = field(default_factory=list)
    final_checkpoint: str | None = None
    run_record_path: str | None = None
    device: str = "cpu"
    elapsed_sec: float = 0.0


def build_criterion(*, label_smoothing: float = 0.0) -> nn.CrossEntropyLoss:
    if not 0.0 <= label_smoothing < 1.0:
        raise ValueError("label_smoothing must be in [0, 1)")
    return nn.CrossEntropyLoss(label_smoothing=label_smoothing)


def build_optimizer(
    model: nn.Module,
    lr: float = 0.001,
    *,
    optimizer: str = "adam",
    weight_decay: float = 0.0,
    momentum: float = 0.9,
) -> Optimizer:
    """Build optimizer over trainable params only (respects freeze_mode)."""
    params = [p for p in model.parameters() if p.requires_grad]
    if not params:
        raise ValueError("No trainable parameters for optimizer")
    name = optimizer.lower()
    if name == "sgd":
        return SGD(params, lr=lr, momentum=momentum, weight_decay=weight_decay)
    if name == "adam":
        return Adam(params, lr=lr, weight_decay=weight_decay)
    if name == "adamw":
        from torch.optim import AdamW

        return AdamW(params, lr=lr, weight_decay=weight_decay)
    raise ValueError(f"Unsupported optimizer: {optimizer}")


def train_step(
    model: nn.Module,
    batch: tuple[Tensor, Tensor],
    criterion: nn.Module,
    optimizer: Adam,
    device: torch.device,
) -> float:
    """One guide-ordered optimizer step; returns loss.item()."""
    inputs, labels = batch
    inputs = inputs.to(device)
    labels = labels.to(device)
    model.train()
    optimizer.zero_grad()
    outputs = model(inputs)
    loss = criterion(outputs, labels)
    loss.backward()
    optimizer.step()
    return float(loss.item())


def set_seed(seed: int) -> None:
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_loop(
    model: nn.Module,
    trainloader: DataLoader[Any],
    config: TrainConfig,
    *,
    log: Callable[[str], None] | None = None,
) -> TrainResult:
    """Run the guide training loop with corrected ``running_loss`` accumulation."""
    device = torch.device(config.device)
    model = model.to(device)
    criterion = build_criterion()
    optimizer = build_optimizer(model, lr=config.lr)
    result = TrainResult(device=str(device))
    emit: Callable[[str], None] = log or print

    artifact_dir = Path(config.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    for epoch in range(config.epochs):
        epoch_t0 = time.perf_counter()
        running_loss = 0.0
        model.train()
        for i, data in enumerate(trainloader):
            if config.smoke_max_batches is not None and i >= config.smoke_max_batches:
                break
            batch_loss = train_step(model, data, criterion, optimizer, device)
            # Guide snippet omits this accumulation; we correct it here.
            running_loss += batch_loss
            if i % config.log_every_n_batches == config.log_every_n_batches - 1:
                avg = running_loss / config.log_every_n_batches
                emit(f"Epoch {epoch + 1}, Batch {i + 1}, Loss: {avg}")
                result.loss_history.append(
                    {
                        "epoch": float(epoch + 1),
                        "batch": float(i + 1),
                        "loss": float(avg),
                    }
                )
                running_loss = 0.0
        result.epoch_times_sec.append(time.perf_counter() - epoch_t0)

    result.elapsed_sec = time.perf_counter() - t0
    ckpt = artifact_dir / "checkpoint_last.pth"
    save_state_dict(model, ckpt)
    result.final_checkpoint = str(ckpt)
    return result


def write_run_record(
    path: str | Path,
    *,
    config: TrainConfig,
    result: TrainResult,
    extra: dict[str, Any] | None = None,
) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "config": asdict(config),
        "device": result.device,
        "elapsed_sec": result.elapsed_sec,
        "epoch_times_sec": result.epoch_times_sec,
        "loss_history": result.loss_history,
        "final_checkpoint": result.final_checkpoint,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "torch": torch.__version__,
        },
        "guide_defect_note": (
            "Student guide Step 4 prints running_loss/100 but never accumulates "
            "loss.item(); this trainer adds running_loss += loss.item() each batch."
        ),
        "model": "SimpleCNN",
    }
    if extra:
        payload.update(extra)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def create_baseline_model() -> SimpleCNN:
    return SimpleCNN()
