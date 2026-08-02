"""Data provenance and transform lineage metadata."""

from __future__ import annotations

from typing import Any

from cifar_cnn.data.constants import (
    DEFAULT_DATA_ROOT,
    NORMALIZE_MEAN,
    NORMALIZE_STD,
    NUM_CLASSES,
    TEST_SIZE,
    TRAIN_SIZE,
)
from cifar_cnn.data.transforms import describe_guide_transform


def build_lineage_record(
    *,
    root: str = DEFAULT_DATA_ROOT,
    torchvision_version: str | None = None,
) -> dict[str, Any]:
    """Record source, access, and transformation lineage for CIFAR-10."""
    try:
        import torchvision

        tv_version = torchvision_version or torchvision.__version__
    except Exception:  # pragma: no cover - optional enrichment
        tv_version = torchvision_version or "unknown"

    return {
        "dataset": "CIFAR-10",
        "source": "torchvision.datasets.CIFAR10",
        "torchvision_version": tv_version,
        "license_citation": (
            "Krizhevsky, A. Learning Multiple Layers of Features from Tiny Images "
            "(2009). Distributed via Torchvision datasets."
        ),
        "download_path": root,
        "access_policy": "Public benchmark; local cache under project data/; no secrets.",
        "sizes": {"train": TRAIN_SIZE, "test": TEST_SIZE, "num_classes": NUM_CLASSES},
        "normalization": {"mean": list(NORMALIZE_MEAN), "std": list(NORMALIZE_STD)},
        "transforms": describe_guide_transform(),
        "change_control": (
            "Dataset or split changes are reviewed model-affecting changes "
            "(model + data owner)."
        ),
        "hashes": {
            "note": (
                "Torchvision manages remote archive integrity; record local cache "
                "hashes in evidence when regenerating splits for release packs."
            )
        },
    }
