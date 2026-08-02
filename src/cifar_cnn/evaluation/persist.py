"""Guide Step 7: persist state_dict to repo and guide-literal paths."""

from __future__ import annotations

from pathlib import Path

import torch.nn as nn

from cifar_cnn.models.simple_cnn import load_state_dict, save_state_dict

REPO_MODEL_PATH = Path("models/cnn_model.pth")
GUIDE_MODEL_PATH = Path("cnn_model.pth")


def save_baseline_model(
    model: nn.Module,
    *,
    repo_path: str | Path = REPO_MODEL_PATH,
    guide_path: str | Path = GUIDE_MODEL_PATH,
) -> tuple[Path, Path]:
    """Write ``models/cnn_model.pth`` and guide-literal ``cnn_model.pth``."""
    repo = save_state_dict(model, repo_path)
    guide = save_state_dict(model, guide_path)
    print("Model saved successfully!")
    return repo, guide


def load_baseline_model(
    model: nn.Module,
    path: str | Path,
    *,
    expected_sha256: str | None = None,
) -> nn.Module:
    return load_state_dict(model, path, expected_sha256=expected_sha256)


def paths_have_identical_bytes(a: str | Path, b: str | Path) -> bool:
    pa, pb = Path(a), Path(b)
    return pa.is_file() and pb.is_file() and pa.read_bytes() == pb.read_bytes()
