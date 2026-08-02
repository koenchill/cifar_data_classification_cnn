"""Synthetic smoke tests for PR CI (no CIFAR-10 download or training)."""

from __future__ import annotations


def test_guide_toolchain_imports() -> None:
    import matplotlib
    import torch
    import torchvision

    assert torch.__version__
    assert torchvision.__version__
    assert matplotlib.__version__


def test_package_importable() -> None:
    import cifar_cnn

    assert cifar_cnn is not None
