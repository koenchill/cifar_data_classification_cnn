"""Baseline evaluation, gallery visualization, and model persistence."""

from cifar_cnn.evaluation.metrics import EvalResult, evaluate_accuracy, write_metrics
from cifar_cnn.evaluation.persist import (
    GUIDE_MODEL_PATH,
    REPO_MODEL_PATH,
    load_baseline_model,
    paths_have_identical_bytes,
    save_baseline_model,
)
from cifar_cnn.evaluation.viz import (
    save_prediction_gallery,
    tensor_to_hwc,
    unnormalize_guide,
)

__all__ = [
    "GUIDE_MODEL_PATH",
    "REPO_MODEL_PATH",
    "EvalResult",
    "evaluate_accuracy",
    "load_baseline_model",
    "paths_have_identical_bytes",
    "save_baseline_model",
    "save_prediction_gallery",
    "tensor_to_hwc",
    "unnormalize_guide",
    "write_metrics",
]
