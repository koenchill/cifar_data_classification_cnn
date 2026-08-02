"""Training loops and baseline trainer."""

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
    "TrainConfig",
    "TrainResult",
    "build_criterion",
    "build_optimizer",
    "create_baseline_model",
    "set_seed",
    "train_loop",
    "train_step",
    "write_run_record",
]
