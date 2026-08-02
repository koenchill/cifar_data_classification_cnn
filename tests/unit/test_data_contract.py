from __future__ import annotations

from pathlib import Path

import torch
import yaml
from torch.utils.data import RandomSampler, SequentialSampler
from torchvision import transforms
from torchvision.transforms import Normalize, ToTensor

from cifar_cnn.data.constants import (
    DEFAULT_BATCH_SIZE,
    NORMALIZE_MEAN,
    NORMALIZE_STD,
    TEST_SIZE,
    TRAIN_SIZE,
)
from cifar_cnn.data.loaders import GuideDataConfig, build_guide_loaders
from cifar_cnn.data.transforms import build_guide_transform, describe_guide_transform


def test_guide_transform_compose_exact() -> None:
    transform = build_guide_transform()
    assert isinstance(transform, transforms.Compose)
    assert len(transform.transforms) == 2
    assert isinstance(transform.transforms[0], ToTensor)
    assert isinstance(transform.transforms[1], Normalize)
    normalize = transform.transforms[1]
    assert tuple(float(x) for x in normalize.mean) == NORMALIZE_MEAN
    assert tuple(float(x) for x in normalize.std) == NORMALIZE_STD


def test_guide_transform_lineage_no_augmentation() -> None:
    desc = describe_guide_transform()
    assert desc["augmentation"] is False
    assert desc["compose"][0]["name"] == "ToTensor"
    assert desc["compose"][1]["mean"] == list(NORMALIZE_MEAN)


def test_baseline_yaml_matches_guide_contract() -> None:
    path = Path("configs/data/baseline.yaml")
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert cfg["root"] == "./data"
    assert cfg["download"] is True
    assert cfg["batch_size"] == 32
    assert cfg["train_shuffle"] is True
    assert cfg["test_shuffle"] is False
    assert cfg["normalize"]["mean"] == [0.5, 0.5, 0.5]
    assert cfg["normalize"]["std"] == [0.5, 0.5, 0.5]
    assert cfg["augmentation_on_eval"] is False
    assert cfg["split"]["official_test_locked"] is True


def test_cifar10_sizes_guide_contract(fake_cifar10_pair) -> None:
    trainset, testset, _root = fake_cifar10_pair
    assert len(trainset) == TRAIN_SIZE
    assert len(testset) == TEST_SIZE


def test_guide_loaders_batch_and_shuffle_flags(fake_cifar10_pair) -> None:
    trainset, testset, root = fake_cifar10_pair
    cfg = GuideDataConfig(
        root=str(root),
        download=False,
        batch_size=DEFAULT_BATCH_SIZE,
        train_shuffle=True,
        test_shuffle=False,
    )
    trainloader, testloader = build_guide_loaders(
        cfg, train_subset=trainset, test_subset=testset
    )
    assert trainloader.batch_size == 32
    assert testloader.batch_size == 32
    assert isinstance(trainloader.sampler, RandomSampler)
    assert isinstance(testloader.sampler, SequentialSampler)


def test_sample_tensor_shape_and_normalization(fake_cifar10_pair) -> None:
    trainset, _testset, _root = fake_cifar10_pair
    image, label = trainset[0]
    assert isinstance(image, torch.Tensor)
    assert image.shape == (3, 32, 32)
    assert 0 <= int(label) < 10
    assert float(image.min()) >= -1.0 - 1e-5
    assert float(image.max()) <= 1.0 + 1e-5


def test_live_cifar10_sizes_when_available(live_cifar10_pair) -> None:
    trainset, testset, _root = live_cifar10_pair
    assert len(trainset) == TRAIN_SIZE
    assert len(testset) == TEST_SIZE
