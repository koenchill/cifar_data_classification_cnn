"""Baseline and rigorous evaluation packages."""

from cifar_cnn.evaluation.gradcam import GradCAM, resolve_target_layer, save_gradcam_overlay
from cifar_cnn.evaluation.metrics import EvalResult, evaluate_accuracy, write_metrics
from cifar_cnn.evaluation.persist import (
    GUIDE_MODEL_PATH,
    REPO_MODEL_PATH,
    load_baseline_model,
    paths_have_identical_bytes,
    save_baseline_model,
)
from cifar_cnn.evaluation.rigorous import (
    RigorousMetrics,
    collect_predictions,
    compute_rigorous_metrics,
    write_rigorous_metrics,
)
from cifar_cnn.evaluation.robustness import (
    RobustnessReport,
    run_robustness_suite,
    write_robustness_report,
)
from cifar_cnn.evaluation.safety import (
    ConfidencePolicy,
    decide_from_logits,
    decide_from_probs,
    policy_summary,
)
from cifar_cnn.evaluation.viz import (
    save_prediction_gallery,
    tensor_to_hwc,
    unnormalize_guide,
)

__all__ = [
    "GUIDE_MODEL_PATH",
    "REPO_MODEL_PATH",
    "ConfidencePolicy",
    "EvalResult",
    "GradCAM",
    "RigorousMetrics",
    "RobustnessReport",
    "collect_predictions",
    "compute_rigorous_metrics",
    "decide_from_logits",
    "decide_from_probs",
    "evaluate_accuracy",
    "load_baseline_model",
    "paths_have_identical_bytes",
    "policy_summary",
    "resolve_target_layer",
    "run_robustness_suite",
    "save_baseline_model",
    "save_gradcam_overlay",
    "save_prediction_gallery",
    "tensor_to_hwc",
    "unnormalize_guide",
    "write_metrics",
    "write_rigorous_metrics",
    "write_robustness_report",
]
