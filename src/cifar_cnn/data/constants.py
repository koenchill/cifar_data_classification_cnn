"""CIFAR-10 constants for guide-compliant loaders and visualization."""

from __future__ import annotations

# Official CIFAR-10 class names (guide Step 6 references undefined `classes`).
CIFAR10_CLASSES: tuple[str, ...] = (
    "airplane",
    "automobile",
    "bird",
    "cat",
    "deer",
    "dog",
    "frog",
    "horse",
    "ship",
    "truck",
)

NUM_CLASSES: int = len(CIFAR10_CLASSES)
TRAIN_SIZE: int = 50_000
TEST_SIZE: int = 10_000
IMAGE_SIZE: int = 32
NORMALIZE_MEAN: tuple[float, float, float] = (0.5, 0.5, 0.5)
NORMALIZE_STD: tuple[float, float, float] = (0.5, 0.5, 0.5)
DEFAULT_BATCH_SIZE: int = 32
DEFAULT_DATA_ROOT: str = "./data"
