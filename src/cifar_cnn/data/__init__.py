"""CIFAR-10 data loading, splits, and lineage."""

from cifar_cnn.data.constants import CIFAR10_CLASSES, NUM_CLASSES
from cifar_cnn.data.loaders import GuideDataConfig, build_guide_loaders, load_cifar10_datasets
from cifar_cnn.data.splits import build_split_manifest, stratified_train_val_indices
from cifar_cnn.data.transforms import build_guide_transform

__all__ = [
    "CIFAR10_CLASSES",
    "NUM_CLASSES",
    "GuideDataConfig",
    "build_guide_transform",
    "build_guide_loaders",
    "load_cifar10_datasets",
    "build_split_manifest",
    "stratified_train_val_indices",
]
