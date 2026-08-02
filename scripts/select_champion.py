#!/usr/bin/env python3
"""Smoke fair comparison + champion decision (validation metrics only)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from torch.utils.data import DataLoader, Subset

from cifar_cnn.models.champion import (
    SelectionEnvelope,
    SelectionRule,
    select_champion,
    write_champion_decision,
)
from cifar_cnn.models.compare import evaluate_candidate_on_val, short_finetune
from cifar_cnn.models.improved_cnn import ImprovedCNN
from cifar_cnn.models.resnet_transfer import build_resnet18_cifar, describe_transfer_stack
from cifar_cnn.models.simple_cnn import SimpleCNN, save_state_dict


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "tests" / "unit"))
    from fake_cifar import FakeCIFAR10

    out = Path("docs/evidence/release-b")
    out.mkdir(parents=True, exist_ok=True)
    art = Path("artifacts/champion_smoke")
    art.mkdir(parents=True, exist_ok=True)

    train = Subset(FakeCIFAR10(train=True), list(range(128)))
    val = Subset(FakeCIFAR10(train=True), list(range(128, 256)))
    trainloader = DataLoader(train, batch_size=16, shuffle=True)
    valloader = DataLoader(val, batch_size=16, shuffle=False)

    models = {
        "simple_cnn_baseline": short_finetune(SimpleCNN(), trainloader, steps=5),
        "improved_cnn_reg": short_finetune(
            ImprovedCNN(batch_norm=True, dropout=True), trainloader, steps=5
        ),
        "resnet18_transfer": short_finetune(
            build_resnet18_cifar(pretrained=False), trainloader, steps=3
        ),
    }
    names = {
        "simple_cnn_baseline": "SimpleCNN",
        "improved_cnn_reg": "ImprovedCNN",
        "resnet18_transfer": "ResNet18CIFAR",
    }

    comparison = []
    candidates = []
    for cid, model in models.items():
        metrics = evaluate_candidate_on_val(
            model,
            valloader,
            candidate_id=cid,
            model_name=names[cid],
            max_batches=4,
            interpretability_score=0.8 if "resnet" not in cid else 0.6,
        )
        candidates.append(metrics)
        comparison.append(metrics.__dict__)
        save_state_dict(model, art / f"{cid}.pth")

    cfg = yaml.safe_load(
        Path("configs/model/champion_selection.yaml").read_text(encoding="utf-8")
    )
    rule = SelectionRule(
        name=cfg["rule_name"],
        envelope=SelectionEnvelope(**cfg["envelope"]),
    )
    decision = select_champion(
        candidates,
        rule=rule,
        model_owner_review="approved-smoke",
        ai_risk_review="approved-smoke-residual-AIR-01/03/05",
    )
    write_champion_decision(out / "phase-09-champion-decision.json", decision)
    (out / "phase-09-comparison.json").write_text(
        json.dumps(
            {
                "split": "validation_smoke_FakeCIFAR",
                "official_test_used": False,
                "transfer_stack": describe_transfer_stack(
                    pretrained=False, freeze_mode="none"
                ),
                "candidates": comparison,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"champion={decision.champion_id} ranking={decision.ranking}")


if __name__ == "__main__":
    main()
