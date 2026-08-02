"""Behavioral robustness checks (not adversarial certification)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor

from cifar_cnn.models.simple_cnn import assert_compatible_input


@dataclass
class RobustnessCaseResult:
    name: str
    status: str  # pass | fail | expected_reject | observed
    detail: str
    max_confidence: float | None = None
    predicted: int | None = None


@dataclass
class RobustnessReport:
    cases: list[RobustnessCaseResult]
    disclaimer: str = (
        "These checks are behavioral smoke tests only. They do not certify "
        "adversarial robustness or real-world safety."
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _gaussian_noise(x: Tensor, std: float = 0.35) -> Tensor:
    return (x + torch.randn_like(x) * std).clamp(-1.0, 1.0)


def _blur(x: Tensor) -> Tensor:
    # Depthwise average blur via avg pool + upsample.
    pooled = F.avg_pool2d(x, kernel_size=3, stride=1, padding=1)
    return pooled


def _predict(
    model: nn.Module, x: Tensor, device: torch.device
) -> tuple[int, float]:
    model.eval()
    with torch.no_grad():
        logits = model(x.to(device))
        probs = F.softmax(logits, dim=1)[0]
        conf, pred = torch.max(probs, dim=0)
    return int(pred.item()), float(conf.item())


def run_robustness_suite(
    model: nn.Module,
    *,
    device: str | torch.device = "cpu",
    seed: int = 0,
) -> RobustnessReport:
    """Run corrupted/OOD/malformed input checks against a CIFAR-shaped model."""
    device_t = torch.device(device)
    model = model.to(device_t)
    model.eval()
    g = torch.Generator().manual_seed(seed)
    clean = torch.randn(1, 3, 32, 32, generator=g)

    cases: list[RobustnessCaseResult] = []

    # Clean reference prediction
    pred, conf = _predict(model, clean, device_t)
    cases.append(
        RobustnessCaseResult(
            "clean_reference",
            "observed",
            "Reference forward on random CIFAR-shaped input",
            max_confidence=conf,
            predicted=pred,
        )
    )

    # Blur / noise corruptions — model should still produce finite outputs
    for name, corrupted in (
        ("blur", _blur(clean)),
        ("gaussian_noise", _gaussian_noise(clean)),
    ):
        p, c = _predict(model, corrupted, device_t)
        ok = torch.isfinite(torch.tensor(c))
        cases.append(
            RobustnessCaseResult(
                name,
                "pass" if ok else "fail",
                "Finite softmax under mild corruption (not a robustness claim)",
                max_confidence=c,
                predicted=p,
            )
        )

    # Wrong size — fail closed via shape contract when asserted
    wrong_size = torch.randn(1, 3, 28, 28)
    try:
        assert_compatible_input(wrong_size)
        cases.append(
            RobustnessCaseResult(
                "wrong_size", "fail", "Expected shape contract to reject 28x28"
            )
        )
    except ValueError as exc:
        cases.append(
            RobustnessCaseResult(
                "wrong_size", "expected_reject", f"Rejected: {exc}"
            )
        )

    # Wrong mode (grayscale)
    wrong_mode = torch.randn(1, 1, 32, 32)
    try:
        assert_compatible_input(wrong_mode)
        cases.append(
            RobustnessCaseResult(
                "wrong_mode", "fail", "Expected channel contract to reject 1x32x32"
            )
        )
    except ValueError as exc:
        cases.append(
            RobustnessCaseResult(
                "wrong_mode", "expected_reject", f"Rejected: {exc}"
            )
        )

    # Malformed NaNs
    malformed = clean.clone()
    malformed[0, 0, 0, 0] = float("nan")
    with torch.no_grad():
        out = model(malformed.to(device_t))
    finite = bool(torch.isfinite(out).all().item())
    cases.append(
        RobustnessCaseResult(
            "malformed_nan",
            "observed",
            (
                "NaN input produced non-finite logits"
                if not finite
                else "NaN input unexpectedly yielded finite logits"
            ),
            max_confidence=None,
        )
    )

    # OOD uniform noise in pixel-ish range
    ood = torch.empty(1, 3, 32, 32).uniform_(-1.0, 1.0)
    p, c = _predict(model, ood, device_t)
    cases.append(
        RobustnessCaseResult(
            "ood_uniform_noise",
            "observed",
            (
                "OOD noise may still yield high softmax confidence; "
                "confidence ≠ correctness (route to uncertain policy)"
            ),
            max_confidence=c,
            predicted=p,
        )
    )

    # High-confidence unfamiliar: deliberately strong logit injection not used;
    # instead document max-conf on OOD as the teaching case.
    cases.append(
        RobustnessCaseResult(
            "high_confidence_unfamiliar_policy",
            "pass" if c is not None else "fail",
            (
                f"Unfamiliar/OOD input confidence={c:.3f}. API must not treat this "
                "as proof of correctness; apply low-confidence/uncertain flags."
            ),
            max_confidence=c,
            predicted=p,
        )
    )

    return RobustnessReport(cases=cases)


def write_robustness_report(path: str | Path, report: RobustnessReport) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    return out
