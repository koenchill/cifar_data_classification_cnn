from __future__ import annotations

import os
from pathlib import Path

import pytest
from fake_cifar import FakeCIFAR10

from cifar_cnn.data.loaders import GuideDataConfig, load_cifar10_datasets


@pytest.fixture
def fake_cifar10_pair():
    return FakeCIFAR10(train=True), FakeCIFAR10(train=False), Path("./data")


@pytest.fixture(scope="session")
def live_cifar10_pair():
    """Optional real CIFAR-10 download when CIFAR_CNN_LIVE_DATA=1 or cache exists."""
    root = Path("./data")
    marker = root / "cifar-10-batches-py"
    live = os.environ.get("CIFAR_CNN_LIVE_DATA") == "1" or marker.exists()
    if not live:
        pytest.skip("Set CIFAR_CNN_LIVE_DATA=1 or cache CIFAR under ./data for live tests")
    cfg = GuideDataConfig(root=str(root), download=True, num_workers=0)
    trainset, testset = load_cifar10_datasets(cfg)
    return trainset, testset, root
