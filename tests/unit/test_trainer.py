"""Phase 4: guide trainer step order and running_loss accumulation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
import yaml
from torch.utils.data import DataLoader, TensorDataset

from cifar_cnn.models.simple_cnn import SimpleCNN
from cifar_cnn.training.trainer import (
    TrainConfig,
    build_criterion,
    build_optimizer,
    train_loop,
    train_step,
    write_run_record,
)


def _tiny_loader(batch_size: int = 4, n: int = 16) -> DataLoader[Any]:
    images = torch.randn(n, 3, 32, 32)
    labels = torch.randint(0, 10, (n,))
    return DataLoader(TensorDataset(images, labels), batch_size=batch_size, shuffle=False)


def test_trainer_step_order_and_types() -> None:
    """Guide order: zero_grad → forward → loss → backward → step."""
    model = SimpleCNN()
    criterion = build_criterion()
    optimizer = build_optimizer(model, lr=0.001)
    assert isinstance(criterion, nn.CrossEntropyLoss)
    assert optimizer.defaults["lr"] == 0.001
    assert optimizer.__class__.__name__ == "Adam"

    calls: list[str] = []
    real_zero = optimizer.zero_grad
    real_step = optimizer.step

    def zero_grad(*args: Any, **kwargs: Any) -> None:
        calls.append("zero_grad")
        return real_zero(*args, **kwargs)

    def step(*args: Any, **kwargs: Any) -> None:
        calls.append("step")
        return real_step(*args, **kwargs)

    optimizer.zero_grad = zero_grad  # type: ignore[method-assign]
    optimizer.step = step  # type: ignore[method-assign]

    original_forward = model.forward

    def tracked_forward(x: torch.Tensor) -> torch.Tensor:
        calls.append("forward")
        return original_forward(x)

    model.forward = tracked_forward  # type: ignore[method-assign]

    batch = (torch.randn(2, 3, 32, 32), torch.tensor([1, 2]))
    loss_val = train_step(model, batch, criterion, optimizer, torch.device("cpu"))
    assert isinstance(loss_val, float)
    assert loss_val == loss_val  # finite
    # zero_grad before forward; step after backward (implied by loss decrease path)
    assert calls.index("zero_grad") < calls.index("forward") < calls.index("step")


def test_running_loss_accumulation(tmp_path: Path) -> None:
    """Corrected loop must average accumulated batch losses, not stay at ~0."""
    model = SimpleCNN()
    loader = _tiny_loader(batch_size=4, n=8)
    logs: list[str] = []
    cfg = TrainConfig(
        epochs=1,
        lr=0.001,
        batch_size=4,
        log_every_n_batches=2,
        smoke_max_batches=4,
        artifact_dir=str(tmp_path / "run"),
    )
    result = train_loop(model, loader, cfg, log=logs.append)
    assert result.loss_history, "expected logged loss windows"
    for row in result.loss_history:
        assert row["loss"] > 0.0
    # Without accumulation, printed avg would be ~0 after first reset semantics.
    assert all(r["loss"] > 1e-6 for r in result.loss_history)
    assert any("Loss:" in line for line in logs)


def test_baseline_train_config_yaml() -> None:
    cfg = yaml.safe_load(Path("configs/train/baseline.yaml").read_text(encoding="utf-8"))
    assert cfg["epochs"] == 10
    assert cfg["lr"] == 0.001
    assert cfg["optimizer"] == "Adam"
    assert cfg["loss"] == "CrossEntropyLoss"
    assert cfg["batch_size"] == 32


def test_write_run_record_documents_guide_defect(tmp_path: Path) -> None:
    cfg = TrainConfig(epochs=1, artifact_dir=str(tmp_path))
    from cifar_cnn.training.trainer import TrainResult

    result = TrainResult(device="cpu", loss_history=[{"epoch": 1.0, "batch": 1.0, "loss": 2.3}])
    path = write_run_record(tmp_path / "run_record.json", config=cfg, result=result)
    text = path.read_text(encoding="utf-8")
    assert "running_loss" in text
    assert "accumulate" in text.lower() or "accumulation" in text.lower() or "adds" in text
