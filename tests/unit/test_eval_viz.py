"""Unit tests for unnormalize helper and gallery labeling contracts."""

from __future__ import annotations

from pathlib import Path

import torch
from torch.utils.data import DataLoader, TensorDataset

from cifar_cnn.data.constants import CIFAR10_CLASSES
from cifar_cnn.evaluation.viz import save_prediction_gallery, unnormalize_guide
from cifar_cnn.models.simple_cnn import SimpleCNN


def test_unnormalize_guide_formula() -> None:
    img = torch.tensor([[[-1.0, 0.0], [1.0, 0.5]]]).repeat(3, 1, 1)
    # After Normalize(0.5,0.5): raw 0 → -1, raw 1 → 1; inverse is /2+0.5
    out = unnormalize_guide(torch.tensor([-1.0, 0.0, 1.0]))
    assert torch.allclose(out, torch.tensor([0.0, 0.5, 1.0]))
    assert unnormalize_guide(img).min() >= 0.0
    assert unnormalize_guide(img).max() <= 1.0


def test_gallery_eight_images_with_actual_predicted(tmp_path: Path) -> None:
    model = SimpleCNN()
    x = torch.randn(16, 3, 32, 32)
    y = torch.arange(16) % 10
    loader = DataLoader(TensorDataset(x, y), batch_size=8, shuffle=False)
    path = tmp_path / "gallery.png"
    save_prediction_gallery(model, loader, path, n_images=8)
    assert path.is_file() and path.stat().st_size > 0
    assert len(CIFAR10_CLASSES) == 10
