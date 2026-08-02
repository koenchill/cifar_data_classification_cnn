"""Fair comparison helpers for champion candidates (validation split only)."""

from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from cifar_cnn.evaluation.rigorous import collect_predictions, compute_rigorous_metrics
from cifar_cnn.evaluation.robustness import run_robustness_suite
from cifar_cnn.models.champion import CandidateMetrics
from cifar_cnn.models.resnet_transfer import (
    count_trainable_parameters,
    estimate_state_dict_mb,
    measure_cpu_latency_ms,
)
from cifar_cnn.models.simple_cnn import count_parameters
from cifar_cnn.training.trainer import build_criterion, train_step


def evaluate_candidate_on_val(
    model: nn.Module,
    valloader: DataLoader[Any],
    *,
    candidate_id: str,
    model_name: str,
    max_batches: int | None = 8,
    notes: str = "",
    interpretability_score: float = 0.5,
    security_ops_score: float = 0.5,
) -> CandidateMetrics:
    """Score a candidate on a validation loader — never the official test set."""
    criterion = build_criterion()
    batch, avg_loss = collect_predictions(
        model, valloader, criterion=criterion, max_batches=max_batches
    )
    metrics = compute_rigorous_metrics(batch, avg_loss=avg_loss)
    rob = run_robustness_suite(model)
    total = max(len(rob.cases), 1)
    hard_fail = sum(1 for c in rob.cases if c.status == "fail")
    pass_rate = 1.0 - (hard_fail / total)

    size_mb = estimate_state_dict_mb(model)
    latency = measure_cpu_latency_ms(model, warmup=2, iters=5)
    params = count_parameters(model) / 1e6
    trainable = count_trainable_parameters(model) / 1e6
    cost_score = max(0.0, min(1.0, 1.0 - (size_mb / 60.0)))

    return CandidateMetrics(
        candidate_id=candidate_id,
        model_name=model_name,
        val_accuracy=metrics.accuracy,
        val_macro_f1=metrics.macro_f1,
        val_ece=metrics.ece,
        robustness_pass_rate=pass_rate,
        latency_ms=latency,
        size_mb=size_mb,
        param_millions=params,
        interpretability_score=interpretability_score,
        security_ops_score=security_ops_score,
        cost_score=cost_score,
        notes=(
            notes
            or f"val_batches<={max_batches}; avg_loss={avg_loss}; trainable_m={trainable:.3f}"
        ),
    )


def short_finetune(
    model: nn.Module,
    trainloader: DataLoader[Any],
    *,
    steps: int = 5,
    lr: float = 0.001,
) -> nn.Module:
    """Tiny CPU fine-tune for smoke comparisons (not a full transfer recipe)."""
    device = torch.device("cpu")
    model = model.to(device)
    params = [p for p in model.parameters() if p.requires_grad]
    if not params:
        raise ValueError("No trainable parameters for fine-tune")
    opt = torch.optim.Adam(params, lr=lr)
    crit = build_criterion()
    model.train()
    n = 0
    for batch in trainloader:
        train_step(model, batch, crit, opt, device)
        n += 1
        if n >= steps:
            break
    return model
