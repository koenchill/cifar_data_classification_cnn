"""Predeclared champion selection on validation metrics only (no test leakage)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


class ChampionSelectionError(ValueError):
    """Raised when selection inputs violate the declared protocol."""


@dataclass(frozen=True)
class SelectionEnvelope:
    max_size_mb: float = 50.0
    max_latency_ms: float = 250.0
    max_param_millions: float = 15.0


@dataclass(frozen=True)
class SelectionRule:
    """Frozen before any official-test evaluation.

    Order: filter by envelope, then rank by val_macro_f1, val_accuracy, lower ECE,
    then lower latency, then lower size.
    """

    name: str = "release-b-champion-v1"
    primary_metric: str = "val_macro_f1"
    secondary_metric: str = "val_accuracy"
    tertiary_metric: str = "val_ece"  # lower better
    envelope: SelectionEnvelope = field(default_factory=SelectionEnvelope)
    forbid_official_test_fields: tuple[str, ...] = (
        "test_accuracy",
        "test_macro_f1",
        "official_test_accuracy",
        "official_test_macro_f1",
    )


@dataclass
class CandidateMetrics:
    candidate_id: str
    model_name: str
    val_accuracy: float
    val_macro_f1: float
    val_ece: float
    robustness_pass_rate: float
    latency_ms: float
    size_mb: float
    param_millions: float
    interpretability_score: float = 0.5  # Grad-CAM support heuristic 0..1
    security_ops_score: float = 0.5
    cost_score: float = 0.5  # higher = cheaper to serve
    notes: str = ""
    # Any of these set → reject (test leakage)
    test_accuracy: float | None = None
    test_macro_f1: float | None = None
    official_test_accuracy: float | None = None
    official_test_macro_f1: float | None = None

    def leakage_fields_present(self) -> list[str]:
        leaked: list[str] = []
        for name in (
            "test_accuracy",
            "test_macro_f1",
            "official_test_accuracy",
            "official_test_macro_f1",
        ):
            if getattr(self, name) is not None:
                leaked.append(name)
        return leaked


@dataclass
class ChampionDecision:
    rule_name: str
    champion_id: str | None
    champion_model: str | None
    rejected: list[dict[str, Any]]
    ranking: list[str]
    rationale: list[str]
    reviews: dict[str, str]
    frozen_before_official_test: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _passes_envelope(c: CandidateMetrics, env: SelectionEnvelope) -> tuple[bool, str]:
    if c.size_mb > env.max_size_mb:
        return False, f"size_mb {c.size_mb:.2f} > max {env.max_size_mb}"
    if c.latency_ms > env.max_latency_ms:
        return False, f"latency_ms {c.latency_ms:.2f} > max {env.max_latency_ms}"
    if c.param_millions > env.max_param_millions:
        return (
            False,
            f"param_millions {c.param_millions:.2f} > max {env.max_param_millions}",
        )
    return True, "within envelope"


def select_champion(
    candidates: list[CandidateMetrics],
    *,
    rule: SelectionRule | None = None,
    model_owner_review: str = "pending",
    ai_risk_review: str = "pending",
) -> ChampionDecision:
    """Select champion using validation metrics only."""
    rule = rule or SelectionRule()
    rationale: list[str] = [
        f"rule={rule.name}",
        "official test metrics are forbidden in selection inputs",
        (
            f"rank by {rule.primary_metric} desc, {rule.secondary_metric} desc, "
            f"{rule.tertiary_metric} asc, latency_ms asc, size_mb asc"
        ),
    ]
    rejected: list[dict[str, Any]] = []
    eligible: list[CandidateMetrics] = []

    for c in candidates:
        leaked = c.leakage_fields_present()
        if leaked:
            raise ChampionSelectionError(
                f"Candidate {c.candidate_id} includes forbidden test fields: {leaked}"
            )
        ok, reason = _passes_envelope(c, rule.envelope)
        if not ok:
            rejected.append(
                {
                    "candidate_id": c.candidate_id,
                    "model_name": c.model_name,
                    "reason": reason,
                }
            )
            continue
        eligible.append(c)

    if not eligible:
        return ChampionDecision(
            rule_name=rule.name,
            champion_id=None,
            champion_model=None,
            rejected=rejected,
            ranking=[],
            rationale=rationale + ["no eligible candidates within envelope"],
            reviews={
                "model_owner": model_owner_review,
                "ai_risk": ai_risk_review,
            },
        )

    ranked = sorted(
        eligible,
        key=lambda c: (
            -c.val_macro_f1,
            -c.val_accuracy,
            c.val_ece,
            c.latency_ms,
            c.size_mb,
        ),
    )
    champ = ranked[0]
    for c in ranked[1:]:
        rejected.append(
            {
                "candidate_id": c.candidate_id,
                "model_name": c.model_name,
                "reason": (
                    f"ranked below champion on declared metrics "
                    f"(val_macro_f1={c.val_macro_f1:.4f})"
                ),
            }
        )
    rationale.append(
        f"champion={champ.candidate_id} val_macro_f1={champ.val_macro_f1:.4f} "
        f"val_acc={champ.val_accuracy:.4f} ece={champ.val_ece:.4f}"
    )
    return ChampionDecision(
        rule_name=rule.name,
        champion_id=champ.candidate_id,
        champion_model=champ.model_name,
        rejected=rejected,
        ranking=[c.candidate_id for c in ranked],
        rationale=rationale,
        reviews={
            "model_owner": model_owner_review,
            "ai_risk": ai_risk_review,
        },
    )


def write_champion_decision(path: str | Path, decision: ChampionDecision) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(decision.to_dict(), indent=2) + "\n", encoding="utf-8")
    return out
