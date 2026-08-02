"""Improved CNN with optional BatchNorm and Dropout (Release B; additive)."""

from __future__ import annotations

from typing import Any, cast

import torch
import torch.nn as nn
from torch import Tensor


class ImprovedCNN(nn.Module):
    """Guide topology with configurable BN after each conv and Dropout on the MLP.

    Same spatial path as ``SimpleCNN`` (3→32→64→64, 1024→64→10 logits) so
    comparisons stay architecture-aligned. BN/Dropout default on for the
    improved path; both can be disabled for ablations.
    """

    def __init__(
        self,
        *,
        batch_norm: bool = True,
        dropout: bool = True,
        dropout_p: float = 0.3,
        num_classes: int = 10,
    ) -> None:
        super().__init__()
        if not 0.0 <= dropout_p < 1.0:
            raise ValueError("dropout_p must be in [0, 1)")
        self.batch_norm = batch_norm
        self.dropout_enabled = dropout
        self.dropout_p = dropout_p

        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(32) if batch_norm else nn.Identity()
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(64) if batch_norm else nn.Identity()
        self.conv3 = nn.Conv2d(64, 64, 3, padding=1)
        self.bn3 = nn.BatchNorm2d(64) if batch_norm else nn.Identity()
        self.pool = nn.MaxPool2d(2, 2)
        self.drop = nn.Dropout(dropout_p) if dropout else nn.Identity()
        self.fc1 = nn.Linear(64 * 4 * 4, 64)
        self.fc2 = nn.Linear(64, num_classes)

    def forward(self, x: Tensor) -> Tensor:
        x = self.pool(torch.relu(self.bn1(self.conv1(x))))
        x = self.pool(torch.relu(self.bn2(self.conv2(x))))
        x = self.pool(torch.relu(self.bn3(self.conv3(x))))
        x = x.view(-1, 64 * 4 * 4)
        x = self.drop(x)
        x = torch.relu(self.fc1(x))
        x = self.drop(x)
        return cast(Tensor, self.fc2(x))


def describe_improved_architecture(
    *,
    batch_norm: bool = True,
    dropout: bool = True,
    dropout_p: float = 0.3,
) -> dict[str, Any]:
    return {
        "name": "ImprovedCNN",
        "baseline_topology": "SimpleCNN",
        "batch_norm": batch_norm,
        "dropout": dropout,
        "dropout_p": dropout_p if dropout else 0.0,
        "output": "logits",
        "note": "Additive Release B model; does not replace guide SimpleCNN path",
    }
