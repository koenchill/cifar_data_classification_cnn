"""Atomic full-state checkpoints with best/last/resume support."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from torch.optim import Optimizer
from torch.optim.lr_scheduler import LRScheduler

from cifar_cnn.training.authz import assert_artifact_write_allowed


@dataclass
class CheckpointMeta:
    path: Path
    kind: str  # last | best | epoch
    epoch: int
    best_metric: float


def atomic_torch_save(obj: Any, path: str | Path) -> Path:
    """Write via temp file + ``os.replace`` (atomic on the same filesystem)."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + ".tmp")
    torch.save(obj, tmp)  # nosec B614 - trusted local training artifact
    os.replace(tmp, out)
    return out


class CheckpointManager:
    """Manage last/best full-state checkpoints under an authorized artifact dir."""

    def __init__(
        self,
        artifact_dir: str | Path,
        *,
        identity: str = "training",
        cwd: Path | None = None,
    ) -> None:
        self.artifact_dir = Path(artifact_dir)
        self.identity = identity
        self.cwd = cwd
        assert_artifact_write_allowed(
            self.artifact_dir / ".write_probe", identity=identity, cwd=cwd
        )
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.last_path = self.artifact_dir / "checkpoint_last.pt"
        self.best_path = self.artifact_dir / "checkpoint_best.pt"

    def build_payload(
        self,
        *,
        model: nn.Module,
        optimizer: Optimizer,
        scheduler: LRScheduler | None,
        epoch: int,
        best_metric: float,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": (
                scheduler.state_dict() if scheduler is not None else None  # type: ignore[no-untyped-call]
            ),
            "epoch": epoch,
            "best_metric": best_metric,
            "torch_rng_state": torch.get_rng_state(),
            "cuda_rng_state_all": (
                torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None
            ),
        }
        if extra:
            payload["extra"] = extra
        return payload

    def save(
        self,
        payload: dict[str, Any],
        *,
        kind: str = "last",
    ) -> CheckpointMeta:
        if kind == "last":
            path = self.last_path
        elif kind == "best":
            path = self.best_path
        else:
            path = self.artifact_dir / f"checkpoint_epoch_{payload['epoch']:03d}.pt"

        assert_artifact_write_allowed(path, identity=self.identity, cwd=self.cwd)
        atomic_torch_save(payload, path)
        return CheckpointMeta(
            path=path,
            kind=kind,
            epoch=int(payload["epoch"]),
            best_metric=float(payload["best_metric"]),
        )

    def load(self, path: str | Path) -> dict[str, Any]:
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"Checkpoint not found: {path}")
        try:
            state = torch.load(path, map_location="cpu", weights_only=False)  # nosec B614
        except TypeError:  # pragma: no cover
            state = torch.load(path, map_location="cpu")  # nosec B614
        if not isinstance(state, dict) or "model_state_dict" not in state:
            raise TypeError("Invalid checkpoint payload; refusing to load")
        return state

    def restore(
        self,
        path: str | Path,
        *,
        model: nn.Module,
        optimizer: Optimizer | None = None,
        scheduler: LRScheduler | None = None,
    ) -> dict[str, Any]:
        state = self.load(path)
        model.load_state_dict(state["model_state_dict"])
        if optimizer is not None and state.get("optimizer_state_dict") is not None:
            optimizer.load_state_dict(state["optimizer_state_dict"])
        if (
            scheduler is not None
            and state.get("scheduler_state_dict") is not None
        ):
            scheduler.load_state_dict(state["scheduler_state_dict"])
        if state.get("torch_rng_state") is not None:
            torch.set_rng_state(state["torch_rng_state"])
        return state
