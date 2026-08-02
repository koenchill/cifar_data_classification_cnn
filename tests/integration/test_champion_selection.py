"""Phase 09: champion selection without official-test leakage."""

from __future__ import annotations

from pathlib import Path

import pytest
import torch
import yaml
from fake_cifar import FakeCIFAR10
from torch.utils.data import DataLoader, Subset

from cifar_cnn.models.champion import (
    CandidateMetrics,
    ChampionSelectionError,
    SelectionEnvelope,
    SelectionRule,
    select_champion,
    write_champion_decision,
)
from cifar_cnn.models.compare import evaluate_candidate_on_val, short_finetune
from cifar_cnn.models.improved_cnn import ImprovedCNN
from cifar_cnn.models.resnet_transfer import (
    build_resnet18_cifar,
    describe_transfer_stack,
    estimate_state_dict_mb,
)
from cifar_cnn.models.simple_cnn import SimpleCNN


def test_champion_selection_rejects_test_leakage() -> None:
    with pytest.raises(ChampionSelectionError, match="forbidden test fields"):
        select_champion(
            [
                CandidateMetrics(
                    candidate_id="leaky",
                    model_name="SimpleCNN",
                    val_accuracy=0.5,
                    val_macro_f1=0.4,
                    val_ece=0.2,
                    robustness_pass_rate=1.0,
                    latency_ms=10.0,
                    size_mb=1.0,
                    param_millions=0.1,
                    test_accuracy=0.99,
                )
            ]
        )


def test_champion_selection_envelope_and_ranking(tmp_path: Path) -> None:
    rule = SelectionRule(
        envelope=SelectionEnvelope(
            max_size_mb=10.0, max_latency_ms=1000.0, max_param_millions=20.0
        )
    )
    small = CandidateMetrics(
        candidate_id="small",
        model_name="SimpleCNN",
        val_accuracy=0.70,
        val_macro_f1=0.65,
        val_ece=0.20,
        robustness_pass_rate=1.0,
        latency_ms=5.0,
        size_mb=1.0,
        param_millions=0.12,
    )
    better = CandidateMetrics(
        candidate_id="better",
        model_name="ImprovedCNN",
        val_accuracy=0.72,
        val_macro_f1=0.68,
        val_ece=0.18,
        robustness_pass_rate=1.0,
        latency_ms=6.0,
        size_mb=1.2,
        param_millions=0.13,
    )
    huge = CandidateMetrics(
        candidate_id="huge",
        model_name="ResNet18CIFAR",
        val_accuracy=0.90,
        val_macro_f1=0.90,
        val_ece=0.05,
        robustness_pass_rate=1.0,
        latency_ms=20.0,
        size_mb=99.0,
        param_millions=11.0,
    )
    decision = select_champion(
        [small, better, huge],
        rule=rule,
        model_owner_review="approved-smoke",
        ai_risk_review="approved-smoke",
    )
    assert decision.champion_id == "better"
    assert any(r["candidate_id"] == "huge" for r in decision.rejected)
    assert decision.frozen_before_official_test is True
    path = write_champion_decision(tmp_path / "decision.json", decision)
    assert path.is_file()


def test_champion_selection_transfer_stack_and_smoke_compare() -> None:
    meta = describe_transfer_stack(pretrained=False, freeze_mode="backbone")
    assert meta["adapted_for_cifar"] is True
    assert "BSD-3" in meta["license_note"] or "BSD-3-Clause" in meta["license_note"]

    train = Subset(FakeCIFAR10(train=True), list(range(64)))
    val = Subset(FakeCIFAR10(train=True), list(range(64, 128)))
    trainloader = DataLoader(train, batch_size=16, shuffle=True)
    valloader = DataLoader(val, batch_size=16, shuffle=False)

    simple = short_finetune(SimpleCNN(), trainloader, steps=3)
    improved = short_finetune(
        ImprovedCNN(batch_norm=True, dropout=True), trainloader, steps=3
    )
    resnet = short_finetune(
        build_resnet18_cifar(pretrained=False, freeze_mode="none"),
        trainloader,
        steps=2,
    )

    assert estimate_state_dict_mb(resnet) < 50.0
    x = torch.randn(2, 3, 32, 32)
    assert resnet(x).shape == (2, 10)

    cands = [
        evaluate_candidate_on_val(
            simple,
            valloader,
            candidate_id="simple_cnn_baseline",
            model_name="SimpleCNN",
            max_batches=2,
            interpretability_score=0.8,
        ),
        evaluate_candidate_on_val(
            improved,
            valloader,
            candidate_id="improved_cnn_reg",
            model_name="ImprovedCNN",
            max_batches=2,
            interpretability_score=0.8,
        ),
        evaluate_candidate_on_val(
            resnet,
            valloader,
            candidate_id="resnet18_transfer",
            model_name="ResNet18CIFAR",
            max_batches=2,
            interpretability_score=0.6,
            notes="smoke random-init ResNet; pretrained path is offline",
        ),
    ]
    for c in cands:
        assert c.leakage_fields_present() == []

    cfg = yaml.safe_load(
        Path("configs/model/champion_selection.yaml").read_text(encoding="utf-8")
    )
    rule = SelectionRule(
        name=cfg["rule_name"],
        envelope=SelectionEnvelope(**cfg["envelope"]),
    )
    decision = select_champion(
        cands,
        rule=rule,
        model_owner_review="approved-protocol-smoke",
        ai_risk_review="approved-protocol-smoke",
    )
    assert decision.champion_id is not None
    assert decision.champion_id in decision.ranking
    assert "official test metrics are forbidden" in " ".join(decision.rationale)
