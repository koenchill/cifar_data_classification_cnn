"""Deterministic stratified train/val splits from the CIFAR-10 training pool."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from torch.utils.data import Dataset

from cifar_cnn.data.constants import NUM_CLASSES, TRAIN_SIZE
from cifar_cnn.data.loaders import assert_official_test_locked


@dataclass(frozen=True)
class SplitManifest:
    seed: int
    val_fraction: float
    train_indices: list[int]
    val_indices: list[int]
    class_counts_train: dict[str, int]
    class_counts_val: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "val_fraction": self.val_fraction,
            "train_size": len(self.train_indices),
            "val_size": len(self.val_indices),
            "train_indices": self.train_indices,
            "val_indices": self.val_indices,
            "class_counts_train": self.class_counts_train,
            "class_counts_val": self.class_counts_val,
            "notes": [
                "Indices refer to the official CIFAR-10 training set only.",
                "Official test set (train=False) is locked until final evaluation.",
            ],
        }


def _labels_from_dataset(dataset: Dataset[Any]) -> list[int]:
    # torchvision CIFAR10 exposes .targets
    targets = getattr(dataset, "targets", None)
    if targets is None:
        raise TypeError("Dataset must expose .targets for stratified splitting")
    return [int(t) for t in targets]


def stratified_train_val_indices(
    labels: list[int],
    *,
    val_fraction: float = 0.1,
    seed: int = 42,
) -> tuple[list[int], list[int]]:
    """Create disjoint stratified train/val index lists from training labels."""
    if not 0.0 < val_fraction < 1.0:
        raise ValueError("val_fraction must be in (0, 1)")
    if len(labels) != TRAIN_SIZE:
        raise ValueError(f"Expected {TRAIN_SIZE} training labels, got {len(labels)}")

    by_class: dict[int, list[int]] = defaultdict(list)
    for idx, label in enumerate(labels):
        by_class[int(label)].append(idx)

    generator = torch.Generator().manual_seed(seed)
    train_indices: list[int] = []
    val_indices: list[int] = []

    for class_id in range(NUM_CLASSES):
        class_idxs = by_class[class_id]
        if not class_idxs:
            raise ValueError(f"Missing examples for class {class_id}")
        perm = torch.randperm(len(class_idxs), generator=generator).tolist()
        shuffled = [class_idxs[i] for i in perm]
        n_val = max(1, int(round(len(shuffled) * val_fraction)))
        if n_val >= len(shuffled):
            n_val = len(shuffled) - 1
        val_indices.extend(shuffled[:n_val])
        train_indices.extend(shuffled[n_val:])

    train_indices.sort()
    val_indices.sort()

    train_set = set(train_indices)
    val_set = set(val_indices)
    if train_set & val_set:
        raise RuntimeError("Train/val indices are not disjoint")
    if train_set | val_set != set(range(TRAIN_SIZE)):
        raise RuntimeError("Train/val indices must cover the full training pool")

    assert_official_test_locked(train_set | val_set)
    return train_indices, val_indices


def build_split_manifest(
    dataset: Dataset[Any],
    *,
    val_fraction: float = 0.1,
    seed: int = 42,
) -> SplitManifest:
    labels = _labels_from_dataset(dataset)
    train_indices, val_indices = stratified_train_val_indices(
        labels, val_fraction=val_fraction, seed=seed
    )

    def counts(idxs: list[int]) -> dict[str, int]:
        out = {str(c): 0 for c in range(NUM_CLASSES)}
        for i in idxs:
            out[str(labels[i])] += 1
        return out

    return SplitManifest(
        seed=seed,
        val_fraction=val_fraction,
        train_indices=train_indices,
        val_indices=val_indices,
        class_counts_train=counts(train_indices),
        class_counts_val=counts(val_indices),
    )


def write_split_manifest(manifest: SplitManifest, path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest.to_dict(), indent=2) + "\n", encoding="utf-8")
    return out


def load_split_manifest(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("split manifest must be a JSON object")
    return data


def assert_disjoint_and_balanced(
    manifest: SplitManifest,
    *,
    relative_tol: float = 0.05,
) -> None:
    """Validate disjointness and approximate per-class balance."""
    train_set = set(manifest.train_indices)
    val_set = set(manifest.val_indices)
    if train_set & val_set:
        raise AssertionError("Train/val overlap detected")
    if len(train_set) + len(val_set) != TRAIN_SIZE:
        raise AssertionError("Train/val must partition the 50k training set")

    for class_id in range(NUM_CLASSES):
        key = str(class_id)
        n_train = manifest.class_counts_train[key]
        n_val = manifest.class_counts_val[key]
        total = n_train + n_val
        expected_val = total * manifest.val_fraction
        if abs(n_val - expected_val) > max(1.0, relative_tol * total):
            raise AssertionError(
                f"Class {class_id} val count {n_val} not within tolerance of {expected_val}"
            )
