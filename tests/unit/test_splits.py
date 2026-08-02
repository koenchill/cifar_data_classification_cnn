from __future__ import annotations

from pathlib import Path

import pytest

from cifar_cnn.data.constants import TRAIN_SIZE
from cifar_cnn.data.loaders import assert_official_test_locked
from cifar_cnn.data.splits import (
    assert_disjoint_and_balanced,
    build_split_manifest,
    load_split_manifest,
    stratified_train_val_indices,
    write_split_manifest,
)


def test_stratified_indices_rejects_wrong_length() -> None:
    labels = [c for c in range(10) for _ in range(100)]
    with pytest.raises(ValueError, match="50000"):
        stratified_train_val_indices(labels, val_fraction=0.1, seed=0)


def test_official_test_lock_rejects_out_of_range() -> None:
    with pytest.raises(ValueError, match="Official test set"):
        assert_official_test_locked({TRAIN_SIZE})


def test_split_manifest_disjoint_balanced_and_reproducible(fake_cifar10_pair) -> None:
    trainset, _testset, _root = fake_cifar10_pair
    m1 = build_split_manifest(trainset, val_fraction=0.1, seed=42)
    m2 = build_split_manifest(trainset, val_fraction=0.1, seed=42)
    assert m1.train_indices == m2.train_indices
    assert m1.val_indices == m2.val_indices
    assert_disjoint_and_balanced(m1)
    assert len(m1.train_indices) + len(m1.val_indices) == TRAIN_SIZE
    assert set(m1.train_indices).isdisjoint(m1.val_indices)


def test_write_repo_split_manifest(fake_cifar10_pair) -> None:
    trainset, _testset, _root = fake_cifar10_pair
    manifest = build_split_manifest(trainset, val_fraction=0.1, seed=42)
    out = Path("data/splits/split_manifest.json")
    write_split_manifest(manifest, out)
    loaded = load_split_manifest(out)
    assert loaded["seed"] == 42
    assert loaded["train_size"] + loaded["val_size"] == TRAIN_SIZE
    assert "Official test set" in " ".join(loaded["notes"])
