"""Confidence / uncertain decision policy for future API responses."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

import torch
import torch.nn.functional as F
from torch import Tensor

Decision = Literal["accept", "low_confidence", "uncertain"]


@dataclass(frozen=True)
class ConfidencePolicy:
    """When the API should return low-confidence / uncertain flags.

    Softmax confidence is **not** treated as proof of correctness.
    """

    low_confidence_threshold: float = 0.55
    uncertain_margin: float = 0.08


@dataclass(frozen=True)
class DecisionResult:
    decision: Decision
    top1_class: int
    top1_confidence: float
    top2_class: int | None
    margin: float
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def decide_from_probs(
    probs: Tensor,
    *,
    policy: ConfidencePolicy | None = None,
) -> DecisionResult:
    """Apply confidence policy to a single-example probability vector."""
    policy = policy or ConfidencePolicy()
    if probs.ndim != 1:
        raise ValueError("Expected a 1-D probability vector")
    ordered = torch.argsort(probs, descending=True)
    top1 = int(ordered[0].item())
    top2 = int(ordered[1].item()) if probs.numel() > 1 else None
    c1 = float(probs[top1].item())
    c2 = float(probs[top2].item()) if top2 is not None else 0.0
    margin = c1 - c2

    if c1 < policy.low_confidence_threshold:
        return DecisionResult(
            "low_confidence",
            top1,
            c1,
            top2,
            margin,
            (f"top1_confidence {c1:.3f} < threshold {policy.low_confidence_threshold}",),
        )

    if margin < policy.uncertain_margin:
        return DecisionResult(
            "uncertain",
            top1,
            c1,
            top2,
            margin,
            (f"margin {margin:.3f} < uncertain_margin {policy.uncertain_margin}",),
        )

    return DecisionResult(
        "accept",
        top1,
        c1,
        top2,
        margin,
        ("confidence and margin within accept band (still not correctness proof)",),
    )


def decide_from_logits(
    logits: Tensor,
    *,
    policy: ConfidencePolicy | None = None,
) -> DecisionResult:
    if logits.ndim == 2:
        logits = logits[0]
    probs = F.softmax(logits, dim=0)
    return decide_from_probs(probs, policy=policy)


def policy_summary(policy: ConfidencePolicy | None = None) -> dict[str, Any]:
    policy = policy or ConfidencePolicy()
    return {
        "policy": asdict(policy),
        "api_behavior": {
            "accept": "Return top-1 class with confidence; include disclaimer fields",
            "low_confidence": "Return prediction with low_confidence=true flag",
            "uncertain": "Return prediction with uncertain=true (ambiguous top-2)",
        },
        "non_claims": [
            "Softmax confidence is not proof of correctness",
            "Policy does not certify adversarial or OOD robustness",
        ],
    }
