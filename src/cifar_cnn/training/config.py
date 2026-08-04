"""Typed, validated training-control configuration (Release B)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any


class ConfigValidationError(ValueError):
    """Raised when a controlled training config fails validation."""


@dataclass(frozen=True)
class ControlledTrainConfig:
    """Additive controls layered on the guide baseline hyperparameters."""

    epochs: int = 10
    lr: float = 0.001
    batch_size: int = 32
    seed: int = 42
    device: str = "cpu"
    log_every_n_batches: int = 100
    smoke_max_batches: int | None = None
    artifact_dir: str = "artifacts/controlled"
    # Early stopping on validation loss (requires valloader).
    early_stop_patience: int = 3
    early_stop_min_delta: float = 1e-4
    # Optional LR schedule; "none" disables.
    scheduler: str = "step"
    scheduler_step_size: int = 5
    scheduler_gamma: float = 0.1
    scheduler_t_max: int | None = None
    scheduler_eta_min: float = 0.0
    resume_from: str | None = None
    # Load model weights only (fresh optimizer/scheduler); preferred for recipe changes.
    init_weights: str | None = None
    # Identity used for artifact write authorization.
    identity: str = "training"
    run_id: str = "controlled-run"
    deterministic: bool = True
    # Model / data recipe (defaults preserve SimpleCNN controlled path).
    model: str = "SimpleCNN"
    batch_norm: bool = True
    dropout: bool = True
    dropout_p: float = 0.3
    train_augment: bool = False
    color_jitter: bool = False
    cutout: bool = False
    cutout_p: float = 0.5
    data_root: str = "./data"
    split_manifest: str = "data/splits/split_manifest.json"
    export_state_dict: str = "model_best.pth"
    pretrained: bool = False
    freeze_mode: str = "none"
    normalize: str = "guide"
    optimizer: str = "adam"
    weight_decay: float = 0.0
    momentum: float = 0.9
    label_smoothing: float = 0.0

    def validate(self) -> None:
        if self.epochs < 1:
            raise ConfigValidationError("epochs must be >= 1")
        if self.lr <= 0:
            raise ConfigValidationError("lr must be > 0")
        if self.batch_size < 1:
            raise ConfigValidationError("batch_size must be >= 1")
        if self.early_stop_patience < 1:
            raise ConfigValidationError("early_stop_patience must be >= 1")
        if self.early_stop_min_delta < 0:
            raise ConfigValidationError("early_stop_min_delta must be >= 0")
        if self.scheduler not in {"step", "cosine", "none"}:
            raise ConfigValidationError("scheduler must be 'step', 'cosine', or 'none'")
        if self.scheduler_eta_min < 0:
            raise ConfigValidationError("scheduler_eta_min must be >= 0")
        if self.scheduler_t_max is not None and self.scheduler_t_max < 1:
            raise ConfigValidationError("scheduler_t_max must be >= 1 when set")
        if self.identity not in {"training", "eval", "release"}:
            raise ConfigValidationError(
                "identity must be one of: training, eval, release"
            )
        if self.device not in {"cpu", "cuda"}:
            raise ConfigValidationError("device must be 'cpu' or 'cuda'")
        if self.resume_from is not None and not str(self.resume_from).strip():
            raise ConfigValidationError("resume_from must be a non-empty path when set")
        if self.init_weights is not None and not str(self.init_weights).strip():
            raise ConfigValidationError("init_weights must be a non-empty path when set")
        if self.resume_from and self.init_weights:
            raise ConfigValidationError("set only one of resume_from or init_weights")
        if self.model not in {"SimpleCNN", "ImprovedCNN", "ResNet18CIFAR"}:
            raise ConfigValidationError(
                "model must be 'SimpleCNN', 'ImprovedCNN', or 'ResNet18CIFAR'"
            )
        if not 0.0 <= self.dropout_p < 1.0:
            raise ConfigValidationError("dropout_p must be in [0, 1)")
        if not 0.0 <= self.cutout_p <= 1.0:
            raise ConfigValidationError("cutout_p must be in [0, 1]")
        if not 0.0 <= self.label_smoothing < 1.0:
            raise ConfigValidationError("label_smoothing must be in [0, 1)")
        if not str(self.split_manifest).strip():
            raise ConfigValidationError("split_manifest must be a non-empty path")
        if not str(self.export_state_dict).strip():
            raise ConfigValidationError("export_state_dict must be a non-empty filename")
        if self.freeze_mode not in {"none", "backbone", "all_but_fc"}:
            raise ConfigValidationError(
                "freeze_mode must be 'none', 'backbone', or 'all_but_fc'"
            )
        if self.normalize not in {"guide", "imagenet"}:
            raise ConfigValidationError("normalize must be 'guide' or 'imagenet'")
        if self.optimizer not in {"adam", "sgd", "adamw"}:
            raise ConfigValidationError("optimizer must be 'adam', 'sgd', or 'adamw'")
        if self.weight_decay < 0:
            raise ConfigValidationError("weight_decay must be >= 0")
        if not 0.0 <= self.momentum < 1.0:
            raise ConfigValidationError("momentum must be in [0, 1)")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_controlled_config(path: str | Path) -> ControlledTrainConfig:
    """Load YAML config into a validated ControlledTrainConfig."""
    import yaml  # type: ignore[import-untyped]

    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}

    if not isinstance(raw, dict):
        raise ConfigValidationError("config root must be a mapping")
    known = {f.name for f in fields(ControlledTrainConfig)}
    kwargs = {k: v for k, v in raw.items() if k in known}
    cfg = ControlledTrainConfig(**kwargs)
    cfg.validate()
    return cfg
