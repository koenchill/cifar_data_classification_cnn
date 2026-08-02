"""Guide-exact CIFAR-10 dataset and DataLoader construction (Step 1)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from torch.utils.data import DataLoader, Dataset, Subset
from torchvision.datasets import CIFAR10

from cifar_cnn.data.constants import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_DATA_ROOT,
    TEST_SIZE,
    TRAIN_SIZE,
)
from cifar_cnn.data.transforms import build_eval_transform, build_guide_transform


@dataclass(frozen=True)
class GuideDataConfig:
    """Baseline loader flags matching the student guide."""

    root: str = DEFAULT_DATA_ROOT
    batch_size: int = DEFAULT_BATCH_SIZE
    train_shuffle: bool = True
    test_shuffle: bool = False
    download: bool = True
    num_workers: int = 0


def resolve_data_root(root: str | Path = DEFAULT_DATA_ROOT) -> Path:
    """Resolve dataset root; guide uses ``./data`` (project ``data/``)."""
    path = Path(root)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def load_cifar10_datasets(
    config: GuideDataConfig | None = None,
) -> tuple[CIFAR10, CIFAR10]:
    """Load train/test CIFAR-10 with the guide transform."""
    cfg = config or GuideDataConfig()
    transform = build_guide_transform()
    root = str(resolve_data_root(cfg.root))
    trainset = CIFAR10(
        root=root,
        train=True,
        download=cfg.download,
        transform=transform,
    )
    testset = CIFAR10(
        root=root,
        train=False,
        download=cfg.download,
        transform=transform,
    )
    if len(trainset) != TRAIN_SIZE:
        raise ValueError(f"Expected train size {TRAIN_SIZE}, got {len(trainset)}")
    if len(testset) != TEST_SIZE:
        raise ValueError(f"Expected test size {TEST_SIZE}, got {len(testset)}")
    return trainset, testset


def load_cifar10_train_eval_datasets(
    config: GuideDataConfig | None = None,
    *,
    train_transform: Callable[[Any], Any] | None = None,
    eval_transform: Callable[[Any], Any] | None = None,
) -> tuple[CIFAR10, CIFAR10]:
    """Additive loader: train transform may augment; eval never should.

    Defaults preserve guide transforms when both are omitted.
    """
    cfg = config or GuideDataConfig()
    train_tf = train_transform or build_guide_transform()
    eval_tf = eval_transform or build_eval_transform()
    root = str(resolve_data_root(cfg.root))
    trainset = CIFAR10(
        root=root,
        train=True,
        download=cfg.download,
        transform=train_tf,
    )
    testset = CIFAR10(
        root=root,
        train=False,
        download=cfg.download,
        transform=eval_tf,
    )
    if len(trainset) != TRAIN_SIZE:
        raise ValueError(f"Expected train size {TRAIN_SIZE}, got {len(trainset)}")
    if len(testset) != TEST_SIZE:
        raise ValueError(f"Expected test size {TEST_SIZE}, got {len(testset)}")
    return trainset, testset


def build_guide_loaders(
    config: GuideDataConfig | None = None,
    *,
    train_subset: Dataset[Any] | None = None,
    test_subset: Dataset[Any] | None = None,
) -> tuple[DataLoader[Any], DataLoader[Any]]:
    """Build train/test DataLoaders with guide batch size and shuffle flags."""
    cfg = config or GuideDataConfig()
    if train_subset is None or test_subset is None:
        trainset, testset = load_cifar10_datasets(cfg)
        train_data: Dataset[Any] = train_subset or trainset
        test_data: Dataset[Any] = test_subset or testset
    else:
        train_data = train_subset
        test_data = test_subset

    trainloader = DataLoader(
        train_data,
        batch_size=cfg.batch_size,
        shuffle=cfg.train_shuffle,
        num_workers=cfg.num_workers,
    )
    testloader = DataLoader(
        test_data,
        batch_size=cfg.batch_size,
        shuffle=cfg.test_shuffle,
        num_workers=cfg.num_workers,
    )
    return trainloader, testloader


def assert_official_test_locked(indices_used_for_training: set[int] | None = None) -> None:
    """Document/enforce that the official 10k test set is not used for training.

    The official test set is a separate ``train=False`` CIFAR10 split. Training
    subsets must be drawn only from the 50k training pool (indices 0..49999).
    """
    if indices_used_for_training is None:
        return
    illegal = {i for i in indices_used_for_training if i < 0 or i >= TRAIN_SIZE}
    if illegal:
        raise ValueError(
            "Official test set must remain locked; training indices must be "
            f"within [0, {TRAIN_SIZE}). Illegal indices sample: {sorted(illegal)[:5]}"
        )


def subset_from_indices(dataset: Dataset[Any], indices: list[int]) -> Subset[Any]:
    return Subset(dataset, indices)
