"""Controlled training loop: seeds, resume, early stop, schedule, tracking."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

import torch
import torch.nn as nn
from torch.optim.lr_scheduler import StepLR
from torch.utils.data import DataLoader

from cifar_cnn.training.authz import assert_artifact_write_allowed
from cifar_cnn.training.checkpoint import CheckpointManager
from cifar_cnn.training.config import ControlledTrainConfig
from cifar_cnn.training.tracking import ExperimentTracker, RunIdentity, git_sha_or_none
from cifar_cnn.training.trainer import build_criterion, build_optimizer, train_step


@dataclass
class ControlledTrainResult:
    epochs_trained: int
    best_metric: float
    best_checkpoint: str | None
    last_checkpoint: str | None
    early_stopped: bool = False
    history: list[dict[str, float]] = field(default_factory=list)
    resumed_from_epoch: int | None = None


def seed_everything(seed: int, *, deterministic: bool = True) -> None:
    """Seed Python and Torch RNGs for reproducible short runs."""
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def worker_init_fn(worker_id: int) -> None:
    """Deterministic DataLoader worker seeding (no NumPy required)."""
    worker_seed = (torch.initial_seed() + worker_id) % 2**32
    random.seed(worker_seed)
    torch.manual_seed(worker_seed)


@torch.no_grad()
def eval_loss(
    model: nn.Module,
    loader: DataLoader[Any],
    criterion: nn.Module,
    device: torch.device,
    *,
    max_batches: int | None = None,
) -> float:
    model.eval()
    total = 0.0
    n = 0
    for i, (inputs, labels) in enumerate(loader):
        if max_batches is not None and i >= max_batches:
            break
        inputs = inputs.to(device)
        labels = labels.to(device)
        loss = criterion(model(inputs), labels)
        total += float(loss.item()) * int(labels.size(0))
        n += int(labels.size(0))
    return total / n if n else float("inf")


def controlled_train_loop(
    model: nn.Module,
    trainloader: DataLoader[Any],
    config: ControlledTrainConfig,
    *,
    valloader: DataLoader[Any] | None = None,
) -> ControlledTrainResult:
    """Train with validated config, atomic checkpoints, early stop, and tracking."""
    config.validate()
    assert_artifact_write_allowed(config.artifact_dir, identity=config.identity)
    seed_everything(config.seed, deterministic=config.deterministic)

    device = torch.device(config.device)
    model = model.to(device)
    criterion = build_criterion()
    optimizer = build_optimizer(model, lr=config.lr)
    scheduler = (
        StepLR(
            optimizer,
            step_size=config.scheduler_step_size,
            gamma=config.scheduler_gamma,
        )
        if config.scheduler == "step"
        else None
    )

    ckpt = CheckpointManager(config.artifact_dir, identity=config.identity)
    tracker = ExperimentTracker(
        config.artifact_dir,
        RunIdentity(
            run_id=config.run_id,
            identity=config.identity,
            git_sha=git_sha_or_none(),
        ),
    )

    start_epoch = 0
    best_metric = float("inf")
    resumed_from: int | None = None
    if config.resume_from:
        state = ckpt.restore(
            config.resume_from, model=model, optimizer=optimizer, scheduler=scheduler
        )
        start_epoch = int(state["epoch"]) + 1
        best_metric = float(state.get("best_metric", best_metric))
        resumed_from = int(state["epoch"])
        tracker.log(f"resumed_from={config.resume_from} next_epoch={start_epoch}")

    result = ControlledTrainResult(
        epochs_trained=0,
        best_metric=best_metric,
        best_checkpoint=None,
        last_checkpoint=None,
        resumed_from_epoch=resumed_from,
    )
    patience_left = config.early_stop_patience
    global_step = 0

    try:
        for epoch in range(start_epoch, config.epochs):
            model.train()
            running = 0.0
            seen = 0
            for i, batch in enumerate(trainloader):
                if config.smoke_max_batches is not None and i >= config.smoke_max_batches:
                    break
                batch_loss = train_step(model, batch, criterion, optimizer, device)
                running += batch_loss
                seen += 1
                global_step += 1
                if i % config.log_every_n_batches == config.log_every_n_batches - 1:
                    avg = running / max(seen, 1)
                    tracker.log_metrics(
                        global_step, {"train_loss_window": avg}, epoch=epoch
                    )
                    running = 0.0
                    seen = 0

            eval_loader = valloader if valloader is not None else trainloader
            val_loss = eval_loss(
                model,
                eval_loader,
                criterion,
                device,
                max_batches=config.smoke_max_batches,
            )
            tracker.log_metrics(global_step, {"val_loss": val_loss}, epoch=epoch)
            result.history.append({"epoch": float(epoch), "val_loss": float(val_loss)})

            payload = ckpt.build_payload(
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
                epoch=epoch,
                best_metric=best_metric,
                extra={"run_id": config.run_id, "seed": config.seed},
            )
            last_meta = ckpt.save(payload, kind="last")
            result.last_checkpoint = str(last_meta.path)

            improved = val_loss < (best_metric - config.early_stop_min_delta)
            if improved:
                best_metric = val_loss
                payload["best_metric"] = best_metric
                best_meta = ckpt.save(payload, kind="best")
                result.best_checkpoint = str(best_meta.path)
                result.best_metric = best_metric
                patience_left = config.early_stop_patience
                tracker.log(f"new_best val_loss={best_metric:.6f}")
            else:
                patience_left -= 1
                tracker.log(f"no_improve patience_left={patience_left}")

            if scheduler is not None:
                scheduler.step()

            result.epochs_trained = epoch - start_epoch + 1
            if valloader is not None and patience_left <= 0:
                result.early_stopped = True
                tracker.log(f"early_stop at epoch={epoch}")
                break

        if result.best_checkpoint:
            ckpt.restore(result.best_checkpoint, model=model)
            tracker.log(f"restored_best {result.best_checkpoint}")
    finally:
        tracker.close()

    return result
