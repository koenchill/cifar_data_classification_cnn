"""Guide-exact SimpleCNN (student guide Step 2)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from torch import Tensor


class SimpleCNN(nn.Module):
    """3→32→64→64 conv path with 1024→64→10 classifier; returns logits."""

    def __init__(self) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.conv3 = nn.Conv2d(64, 64, 3, padding=1)
        self.fc1 = nn.Linear(64 * 4 * 4, 64)
        self.fc2 = nn.Linear(64, 10)

    def forward(self, x: Tensor) -> Tensor:
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = self.pool(torch.relu(self.conv3(x)))
        x = x.view(-1, 64 * 4 * 4)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def save_state_dict(model: nn.Module, path: str | Path) -> Path:
    """Persist weights via ``torch.save`` of the state dict only (trusted format)."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Guide requires torch.save(state_dict); content is tensors-only mapping.
    torch.save(model.state_dict(), out)  # nosec B614
    return out


def load_state_dict(
    model: nn.Module,
    path: str | Path,
    *,
    expected_sha256: str | None = None,
) -> nn.Module:
    """Load an application-generated state dict; fail closed on mismatch/tamper."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Model artifact not found: {path}")

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256.lower():
        raise ValueError("Model artifact hash mismatch; refusing to load (fail closed)")

    # weights_only=True avoids arbitrary pickle object execution on modern torch.
    try:
        state = torch.load(path, map_location="cpu", weights_only=True)  # nosec B614
    except TypeError:  # pragma: no cover - older torch without weights_only
        state = torch.load(path, map_location="cpu")  # nosec B614

    if not isinstance(state, dict):
        raise TypeError("Expected a state_dict mapping; refusing non-dict artifact")

    model.load_state_dict(state)
    return model


def assert_compatible_input(x: Tensor) -> None:
    if x.ndim != 4 or x.shape[1:] != (3, 32, 32):
        raise ValueError(
            f"Expected input shape (N, 3, 32, 32); got {tuple(x.shape)}"
        )


def describe_architecture() -> dict[str, Any]:
    return {
        "name": "SimpleCNN",
        "layers": {
            "conv1": "Conv2d(3, 32, kernel_size=3, padding=1)",
            "pool": "MaxPool2d(2, 2)",
            "conv2": "Conv2d(32, 64, kernel_size=3, padding=1)",
            "conv3": "Conv2d(64, 64, kernel_size=3, padding=1)",
            "fc1": "Linear(1024, 64)",
            "fc2": "Linear(64, 10)",
        },
        "activation": "ReLU (conv blocks and fc1); logits from fc2 (no softmax)",
        "trusted_artifact": "PyTorch state_dict (.pth) produced by this application",
    }
