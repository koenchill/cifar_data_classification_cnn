"""Training loops, baseline trainer, and Release B controls."""

from cifar_cnn.training.authz import ArtifactWriteDenied, assert_artifact_write_allowed
from cifar_cnn.training.checkpoint import CheckpointManager, atomic_torch_save
from cifar_cnn.training.config import (
    ConfigValidationError,
    ControlledTrainConfig,
    load_controlled_config,
)
from cifar_cnn.training.controlled import (
    ControlledTrainResult,
    controlled_train_loop,
    seed_everything,
    worker_init_fn,
)
from cifar_cnn.training.tracking import ExperimentTracker, RunIdentity
from cifar_cnn.training.trainer import (
    TrainConfig,
    TrainResult,
    build_criterion,
    build_optimizer,
    create_baseline_model,
    set_seed,
    train_loop,
    train_step,
    write_run_record,
)

__all__ = [
    "ArtifactWriteDenied",
    "CheckpointManager",
    "ConfigValidationError",
    "ControlledTrainConfig",
    "ControlledTrainResult",
    "ExperimentTracker",
    "RunIdentity",
    "TrainConfig",
    "TrainResult",
    "assert_artifact_write_allowed",
    "atomic_torch_save",
    "build_criterion",
    "build_optimizer",
    "controlled_train_loop",
    "create_baseline_model",
    "load_controlled_config",
    "seed_everything",
    "set_seed",
    "train_loop",
    "train_step",
    "worker_init_fn",
    "write_run_record",
]
