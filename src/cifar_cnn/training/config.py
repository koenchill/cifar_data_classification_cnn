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
    # Optional StepLR; "none" disables.
    scheduler: str = "step"
    scheduler_step_size: int = 5
    scheduler_gamma: float = 0.1
    resume_from: str | None = None
    # Identity used for artifact write authorization.
    identity: str = "training"
    run_id: str = "controlled-run"
    deterministic: bool = True

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
        if self.scheduler not in {"step", "none"}:
            raise ConfigValidationError("scheduler must be 'step' or 'none'")
        if self.identity not in {"training", "eval", "release"}:
            raise ConfigValidationError(
                "identity must be one of: training, eval, release"
            )
        if self.device not in {"cpu", "cuda"}:
            raise ConfigValidationError("device must be 'cpu' or 'cuda'")
        if self.resume_from is not None and not str(self.resume_from).strip():
            raise ConfigValidationError("resume_from must be a non-empty path when set")

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
