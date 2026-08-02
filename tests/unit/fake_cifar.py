"""Synthetic CIFAR-10-shaped dataset for leakage-safe unit tests (no download)."""

from __future__ import annotations

from typing import Any

import torch
from torch.utils.data import Dataset

from cifar_cnn.data.constants import NUM_CLASSES, TEST_SIZE, TRAIN_SIZE


class FakeCIFAR10(Dataset[Any]):
    """Minimal stand-in exposing ``targets`` like torchvision CIFAR10."""

    def __init__(self, *, train: bool = True, root: str = "./data") -> None:
        self.root = root
        self.train = train
        n = TRAIN_SIZE if train else TEST_SIZE
        per_class = n // NUM_CLASSES
        self.targets = [c for c in range(NUM_CLASSES) for _ in range(per_class)]
        assert len(self.targets) == n

    def __len__(self) -> int:
        return len(self.targets)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
        image = torch.full((3, 32, 32), 0.5)
        mean = torch.tensor([0.5, 0.5, 0.5]).view(3, 1, 1)
        std = torch.tensor([0.5, 0.5, 0.5]).view(3, 1, 1)
        image = (image - mean) / std
        return image, self.targets[index]
