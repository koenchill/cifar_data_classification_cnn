"""Phase 08: metric fixture tests (no official-test tuning)."""

from __future__ import annotations

from pathlib import Path

import torch
import torch.nn.functional as F

from cifar_cnn.evaluation.gradcam import GradCAM, resolve_target_layer, save_gradcam_overlay
from cifar_cnn.evaluation.rigorous import (
    PredictionBatch,
    binary_roc_auc,
    compute_rigorous_metrics,
    confusion_matrix,
    expected_calibration_error,
    per_class_prf,
)
from cifar_cnn.evaluation.robustness import run_robustness_suite
from cifar_cnn.evaluation.safety import ConfidencePolicy, decide_from_probs, policy_summary
from cifar_cnn.models.simple_cnn import SimpleCNN


def test_metrics_fixtures_confusion_and_prf() -> None:
    # 3-class toy fixture with known counts
    y_true = torch.tensor([0, 0, 1, 1, 2, 2])
    y_pred = torch.tensor([0, 1, 1, 1, 2, 0])
    cm = confusion_matrix(y_true, y_pred, num_classes=3)
    assert cm.tolist() == [
        [1, 1, 0],
        [0, 2, 0],
        [1, 0, 1],
    ]
    names = ("a", "b", "c")
    scores = per_class_prf(cm, names)
    # class b: tp=2, fp=1, fn=0 -> p=2/3, r=1, f1=0.8
    assert abs(scores["b"].precision - 2 / 3) < 1e-6
    assert abs(scores["b"].recall - 1.0) < 1e-6
    assert abs(scores["b"].f1 - 0.8) < 1e-6


def test_metrics_fixtures_roc_auc_and_ece() -> None:
    y = torch.tensor([0, 0, 1, 1])
    scores = torch.tensor([0.1, 0.4, 0.35, 0.8])
    auc = binary_roc_auc(y, scores)
    assert auc is not None and 0.5 <= auc <= 1.0

    # Perfectly confident and correct -> ECE ~ 0
    probs = torch.tensor(
        [
            [0.9, 0.05, 0.05],
            [0.1, 0.8, 0.1],
        ]
    )
    labels = torch.tensor([0, 1])
    assert expected_calibration_error(probs, labels, n_bins=5) <= 0.16


def test_metrics_fixtures_rigorous_bundle() -> None:
    logits = torch.tensor(
        [
            [5.0, 0.0, 0.0],
            [0.0, 4.0, 0.0],
            [0.0, 0.0, 3.0],
            [2.0, 2.1, 0.0],
        ]
    )
    labels = torch.tensor([0, 1, 2, 1])
    probs = F.softmax(logits, dim=1)
    preds = probs.argmax(dim=1)
    batch = PredictionBatch(logits=logits, probs=probs, preds=preds, labels=labels)
    metrics = compute_rigorous_metrics(
        batch, avg_loss=0.5, class_names=("a", "b", "c")
    )
    assert metrics.n_samples == 4
    assert 0.0 <= metrics.accuracy <= 1.0
    assert metrics.macro_f1 >= 0.0
    assert "Softmax confidence is not proof of correctness." in metrics.notes
    assert metrics.to_dict()["official_test_locked_for_tuning"] is True


def test_metrics_fixtures_safety_policy() -> None:
    low = decide_from_probs(torch.tensor([0.4, 0.3, 0.3]))
    assert low.decision == "low_confidence"
    uncertain = decide_from_probs(
        torch.tensor([0.48, 0.47, 0.05]),
        policy=ConfidencePolicy(low_confidence_threshold=0.4, uncertain_margin=0.05),
    )
    assert uncertain.decision == "uncertain"
    accept = decide_from_probs(torch.tensor([0.9, 0.05, 0.05]))
    assert accept.decision == "accept"
    summary = policy_summary()
    assert "Softmax confidence is not proof of correctness" in summary["non_claims"]


def test_metrics_fixtures_robustness_and_gradcam(tmp_path: Path) -> None:
    model = SimpleCNN()
    report = run_robustness_suite(model, seed=1)
    names = {c.name for c in report.cases}
    assert "wrong_size" in names and "ood_uniform_noise" in names
    assert any(c.status == "expected_reject" for c in report.cases if c.name == "wrong_size")
    assert "do not certify" in report.disclaimer.lower() or "not certify" in report.disclaimer

    x = torch.randn(1, 3, 32, 32)
    cam = GradCAM(model, resolve_target_layer(model))
    try:
        result = cam(x)
        assert result.heatmap.shape == (32, 32)
        path = save_gradcam_overlay(
            x[0], result, tmp_path / "cam.png", title="fixture"
        )
        assert path.is_file()
    finally:
        cam.close()
